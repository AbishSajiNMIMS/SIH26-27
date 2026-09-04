import json
import torch
from torch_geometric.data import Data


INPUT_FILE = "data/processed/graph.json"


def prepare_graph():

    # Load graph
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        graph = json.load(file)

    nodes = graph["nodes"]
    edges = graph["edges"]

    # Give every person a numeric index
    node_to_index = {
        node: index
        for index, node in enumerate(nodes)
    }

    # Convert edges to numeric form
    edge_list = []

    for edge in edges:

        source = node_to_index[edge["source"]]
        target = node_to_index[edge["target"]]

        edge_list.append([source, target])

    # PyTorch Geometric expects [2, number_of_edges]
    edge_index = torch.tensor(
        edge_list,
        dtype=torch.long
    ).t().contiguous()

    # Simple node features
    # For now every person starts with one feature: 1
    x = torch.ones(
        (len(nodes), 1),
        dtype=torch.float
    )

    # Create PyG graph
    data = Data(
        x=x,
        edge_index=edge_index
    )

    print("\nPYTORCH GEOMETRIC GRAPH")
    print("-----------------------")
    print(f"Nodes: {data.num_nodes}")
    print(f"Edges: {data.num_edges}")
    print(f"Node features: {data.num_node_features}")

    print("\nNODE MAPPING")
    print("------------")

    for person, index in node_to_index.items():
        print(f"{index} -> {person}")


if __name__ == "__main__":
    prepare_graph()