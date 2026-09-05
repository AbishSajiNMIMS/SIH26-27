from neo4j import GraphDatabase
import json


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Khiladi786"

OUTPUT_FILE = "data/processed/graph.json"


def export_graph():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    nodes = []
    edges = []

    with driver.session() as session:

        node_result = session.run(
            """
            MATCH (p:Person)
            RETURN p.id AS id
            ORDER BY p.id
            """
        )

        for record in node_result:
            nodes.append(record["id"])

        edge_result = session.run(
            """
            MATCH (a:Person)-[:CALLS]->(b:Person)
            RETURN a.id AS source,
                   b.id AS target
            """
        )

        for record in edge_result:
            edges.append({
                "source": record["source"],
                "target": record["target"]
            })

    driver.close()

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(graph, file, indent=2)

    print(f"Exported {len(nodes)} nodes.")
    print(f"Exported {len(edges)} edges.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    export_graph()