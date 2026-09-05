from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import os
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_role
)
from src.api.evidence import router as evidence_router
# --------------------------------------------------
# Neo4j Configuration
# --------------------------------------------------

NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687"
)

NEO4J_USERNAME = os.getenv(
    "NEO4J_USERNAME",
    "neo4j"
)

NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD",
    "Khiladi786"
)


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="SIH 26189 - Criminal Network Analysis API",
    version="1.0.0"
)
app.include_router(evidence_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Neo4j Driver
# --------------------------------------------------

driver = None

if NEO4J_PASSWORD:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        user["username"],
        user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }
# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():

    if driver is None:
        return {
            "status": "error",
            "neo4j": "password not configured"
        }

    try:

        with driver.session() as session:
            session.run("RETURN 1").single()

        return {
            "status": "ok",
            "neo4j": "connected"
        }

    except Exception as e:

        return {
            "status": "error",
            "neo4j": "connection failed",
            "message": str(e)
        }


# --------------------------------------------------
# Get Network
# --------------------------------------------------

@app.get("/network")
def get_network(
    current_user=Depends(get_current_user)
):

    if driver is None:
        raise HTTPException(
            status_code=500,
            detail="Neo4j password not configured"
        )

    try:

        with driver.session() as session:

            node_result = session.run(
                """
                MATCH (p:Person)
                RETURN p.id AS id
                ORDER BY p.id
                """
            )

            nodes = [
                {
                    "id": record["id"],
                    "label": record["id"],
                    "type": "Person"
                }
                for record in node_result
            ]

            edge_result = session.run(
                """
                MATCH (a:Person)-[r:CALLS]->(b:Person)
                RETURN
                    a.id AS source,
                    b.id AS target,
                    r.duration_sec AS duration_sec,
                    r.timestamp AS timestamp,
                    r.cell_tower AS cell_tower
                """
            )

            edges = [
                {
                    "source": record["source"],
                    "target": record["target"],
                    "type": "CALLS",
                    "duration_sec": record["duration_sec"],
                    "timestamp": record["timestamp"],
                    "cell_tower": record["cell_tower"]
                }
                for record in edge_result
            ]

        return {
            "nodes": nodes,
            "edges": edges
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# --------------------------------------------------
# ADMIN ENDPOINT
# --------------------------------------------------

@app.get("/admin")
def admin_endpoint(
    current_user=Depends(
        require_role("admin")
    )
):

    return {
        "message": "Admin access granted",
        "user": current_user["username"]
    }

# --------------------------------------------------
# Shutdown
# --------------------------------------------------

@app.on_event("shutdown")
def shutdown():

    if driver:
        driver.close()