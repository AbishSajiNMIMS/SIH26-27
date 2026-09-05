from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Khiladi786"


def detect_communities():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    with driver.session() as session:

        # Remove old analytical graph if present
        try:
            session.run(
                "CALL gds.graph.drop('criminal-network', false)"
            )
        except Exception:
            pass

        # Create analytical graph
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

        result = session.run(
            """
            CALL gds.louvain.stream('criminal-network')
            YIELD nodeId, communityId

            RETURN
                gds.util.asNode(nodeId).id AS person,
                communityId

            ORDER BY communityId, person
            """
        )

        communities = {}

        for record in result:

            community_id = record["communityId"]
            person = record["person"]

            if community_id not in communities:
                communities[community_id] = []

            communities[community_id].append(person)

        print("\nDETECTED COMMUNITIES")
        print("--------------------")

        for community_id, members in communities.items():

            print(
                f"Community {community_id}: "
                f"{', '.join(members)} "
                f"({len(members)} members)"
            )

        # Remove analytical graph
        session.run(
            "CALL gds.graph.drop('criminal-network', false)"
        )

    driver.close()


if __name__ == "__main__":
    detect_communities()