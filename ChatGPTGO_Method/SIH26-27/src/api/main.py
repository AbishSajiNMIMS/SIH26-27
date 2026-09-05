from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import os

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
def get_network():

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
# Shutdown
# --------------------------------------------------

@app.on_event("shutdown")
def shutdown():

    if driver:
        driver.close()