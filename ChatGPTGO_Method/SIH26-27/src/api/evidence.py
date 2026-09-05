import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from src.api.auth import get_current_user


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)


# --------------------------------------------------
# SHA-256 Calculation
# --------------------------------------------------

def calculate_sha256(file: UploadFile):

    sha256 = hashlib.sha256()

    while True:

        chunk = file.file.read(1024 * 1024)

        if not chunk:
            break

        sha256.update(chunk)

    return sha256.hexdigest()


# --------------------------------------------------
# Evidence Hash Endpoint
# --------------------------------------------------

@router.post("/hash")
def hash_evidence(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    try:

        file_hash = calculate_sha256(file)

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        return {
            "filename": file.filename,
            "sha256": file_hash,
            "timestamp": timestamp,
            "uploaded_by": current_user["username"],
            "status": "hashed"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )