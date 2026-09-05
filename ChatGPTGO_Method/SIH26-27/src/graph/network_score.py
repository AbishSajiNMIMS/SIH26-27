from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Khiladi786"


def calculate_scores():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    with driver.session() as session:

        # Drop existing graph if it exists
        session.run(
            "CALL gds.graph.drop('criminal-network', false)"
        )

        # Create analytical graph
        try:
            session.run(
                """
                CALL gds.graph.project(
                    'criminal-network',
                    'Person',
                    {
                        CALLS: {
                            orientation: 'UNDIRECTED'
                        }
                    }
                )
                """
            )
        except Exception as e:
            print(f"Error creating graph: {e}")
            driver.close()
            return

        # Degree
        degree_result = session.run(
            """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[:CALLS]-(other:Person)

            RETURN p.id AS person,
                   count(DISTINCT other) AS degree
            """
        )

        degree = {
            record["person"]: record["degree"]
            for record in degree_result
        }

        # Betweenness
        betweenness_result = session.run(
            """
            CALL gds.betweenness.stream('criminal-network')
            YIELD nodeId, score

            RETURN gds.util.asNode(nodeId).id AS person,
                   score
            """
        )

        betweenness = {
            record["person"]: record["score"]
            for record in betweenness_result
        }

        # PageRank
        pagerank_result = session.run(
            """
            CALL gds.pageRank.stream('criminal-network')
            YIELD nodeId, score

            RETURN gds.util.asNode(nodeId).id AS person,
                   score
            """
        )

        pagerank = {
            record["person"]: record["score"]
            for record in pagerank_result
        }

        # Display results
        print("\nNETWORK INTELLIGENCE")
        print("--------------------")

        for person in degree:

            print(
                f"{person} | "
                f"Degree: {degree[person]} | "
                f"Betweenness: {betweenness.get(person, 0):.2f} | "
                f"PageRank: {pagerank.get(person, 0):.4f}"
            )

    # Remove temporary analytical graph
    with driver.session() as session:
        try:
            session.run(
                "CALL gds.graph.drop('criminal-network')"
            )
        except:
            pass

    driver.close()


if __name__ == "__main__":
    calculate_scores()