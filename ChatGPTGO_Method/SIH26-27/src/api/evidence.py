import hashlib
import uuid
from datetime import datetime, timezone

import httpx

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)

from src.api.auth import get_current_user


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)


FABRIC_GATEWAY_URL = "http://localhost:3000"


def calculate_sha256(file: UploadFile) -> str:

    sha256 = hashlib.sha256()

    while True:

        chunk = file.file.read(1024 * 1024)

        if not chunk:
            break

        sha256.update(chunk)

    return sha256.hexdigest()


@router.post("/hash")
async def hash_evidence(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    try:

        # --------------------------------
        # 1. Calculate SHA-256
        # --------------------------------

        file_hash = calculate_sha256(file)

        # --------------------------------
        # 2. Generate evidence ID
        # --------------------------------

        evidence_id = f"EVD-{uuid.uuid4().hex[:12].upper()}"

        # --------------------------------
        # 3. Create timestamp
        # --------------------------------

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        username = current_user["username"]

        # --------------------------------
        # 4. Send evidence hash to Fabric
        # --------------------------------

        payload = {
            "id": evidence_id,
            "filename": file.filename,
            "sha256": file_hash,
            "uploadedBy": username,
            "timestamp": timestamp,
        }

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            response = await client.post(
                f"{FABRIC_GATEWAY_URL}/record-evidence",
                json=payload,
            )

        # --------------------------------
        # 5. Handle Gateway response
        # --------------------------------

        if response.status_code != 200:

            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Fabric Gateway failed",
                    "gateway_response": response.text,
                },
            )

        fabric_result = response.json()

        # --------------------------------
        # 6. Return complete result
        # --------------------------------

        return {
            "status": "anchored",
            "filename": file.filename,
            "sha256": file_hash,
            "evidence_id": evidence_id,
            "uploaded_by": username,
            "timestamp": timestamp,
            "fabric": fabric_result,
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )