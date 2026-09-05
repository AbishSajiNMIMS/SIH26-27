import json

from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Khiladi786"

INPUT_FILE = "data/processed/fir_entities.json"


def load_fir():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        fir = json.load(file)

    with driver.session() as session:

        # Create the case
        session.run(
            """
            MERGE (c:Case {id: $case_id})
            """,
            case_id=fir["case_id"]
        )

        # Create entities
        for entity in fir["entities"]:

            if entity["type"] == "Person":

                session.run(
                    """
                    MERGE (p:Person {id: $id})
                    """,
                    id=entity["id"]
                )

            elif entity["type"] == "Location":

                session.run(
                    """
                    MERGE (l:Location {name: $name})
                    """,
                    name=entity["id"]
                )

            elif entity["type"] == "Phone":

                session.run(
                    """
                    MERGE (p:Phone {number: $number})
                    """,
                    number=entity["id"]
                )

        # Create relationships
        for relationship in fir["relationships"]:

            source = relationship["source"]
            target = relationship["target"]
            rel_type = relationship["type"]

            if rel_type == "MENTIONED_IN":

                session.run(
                    """
                    MATCH (p:Person {id: $source})
                    MATCH (c:Case {id: $target})

                    MERGE (p)-[:MENTIONED_IN]->(c)
                    """,
                    source=source,
                    target=target
                )

            elif rel_type == "LOCATED_AT":

                session.run(
                    """
                    MATCH (c:Case {id: $source})
                    MATCH (l:Location {name: $target})

                    MERGE (c)-[:LOCATED_AT]->(l)
                    """,
                    source=source,
                    target=target
                )

    driver.close()

    print("FIR data successfully loaded into Neo4j.")


if __name__ == "__main__":
    load_fir()