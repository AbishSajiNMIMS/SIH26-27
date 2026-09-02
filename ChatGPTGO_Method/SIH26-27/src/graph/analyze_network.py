from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Khiladi$786"


def analyze_degree():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    with driver.session() as session:

        result = session.run(
            """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[:CALLS]-(other:Person)

            RETURN p.id AS person,
                   count(DISTINCT other) AS unique_contacts

            ORDER BY unique_contacts DESC
            """
        )

        print("\nNETWORK RANKING")
        print("----------------")

        rank = 1

        for record in result:
            print(
                f"{rank}. {record['person']} "
                f"-> {record['unique_contacts']} unique contacts"
            )
            rank += 1

    driver.close()


if __name__ == "__main__":
    analyze_degree()