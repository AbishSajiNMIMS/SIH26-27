import csv
from pathlib import Path

from neo4j import GraphDatabase




INPUT_FILE = Path("C:\\Users\\sajim\\OneDrive\\Desktop\\SIH26-27\\ChatGPTGO_Method\\SIH26-27\\data\\processed\\cdr_clean.csv")

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Khiladi$786"


def load_cdr_data():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    with driver.session() as session:

        # Start clean for our test dataset
        session.run("MATCH (n) DETACH DELETE n")

        with open(INPUT_FILE, "r", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                session.run(
                    """
                    MERGE (caller:Person {id: $caller})
                    MERGE (receiver:Person {id: $receiver})

                    CREATE (caller)-[:CALLS {
                        timestamp: $timestamp,
                        duration_sec: $duration,
                        cell_tower: $tower
                    }]->(receiver)
                    """,
                    caller=row["caller"],
                    receiver=row["receiver"],
                    timestamp=row["timestamp"],
                    duration=int(row["duration_sec"]),
                    tower=row["cell_tower"]
                )

    driver.close()

    print("CDR data successfully loaded into Neo4j.")


if __name__ == "__main__":
    load_cdr_data()