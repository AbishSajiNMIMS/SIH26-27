import csv
from pathlib import Path



INPUT_FILE = Path("ChatGPTGO_Method/SIH26-27/data/processed/cdr_clean.csv")


def build_graph():
    nodes = set()
    edges = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            caller = row["caller"]
            receiver = row["receiver"]

            # Create nodes
            nodes.add(caller)
            nodes.add(receiver)

            # Create an edge
            edges.append({
                "source": caller,
                "target": receiver,
                "timestamp": row["timestamp"],
                "duration_sec": int(row["duration_sec"]),
                "cell_tower": row["cell_tower"]
            })

    print("\nNODES")
    print("-----")

    for node in sorted(nodes):
        print(node)

    print("\nEDGES")
    print("-----")

    for edge in edges:
        print(
            f'{edge["source"]} -> {edge["target"]} '
            f'| duration={edge["duration_sec"]} sec '
            f'| tower={edge["cell_tower"]}'
        )

    print("\nSUMMARY")
    print("-------")
    print(f"Total nodes: {len(nodes)}")
    print(f"Total edges: {len(edges)}")


if __name__ == "__main__":
    build_graph()