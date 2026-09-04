import json
import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.data import Data
from torch_geometric.nn import GCNConv


INPUT_FILE = "data/processed/graph.json"


# -----------------------------
# Load graph
# -----------------------------

def load_graph():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        graph = json.load(file)

    nodes = graph["nodes"]
    edges = graph["edges"]

    node_to_index = {
        node: i
        for i, node in enumerate(nodes)
    }

    edge_list = []

    for edge in edges:

        source = node_to_index[edge["source"]]
        target = node_to_index[edge["target"]]

        edge_list.append([source, target])

    edge_index = torch.tensor(
        edge_list,
        dtype=torch.long
    ).t().contiguous()

    x = torch.ones(
        (len(nodes), 1),
        dtype=torch.float
    )

    return Data(
        x=x,
        edge_index=edge_index
    ), nodes


# -----------------------------
# GCN Model
# -----------------------------

class GCN(nn.Module):

    def __init__(self):

        super().__init__()

        self.conv1 = GCNConv(1, 16)
        self.conv2 = GCNConv(16, 8)

    def forward(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = F.relu(x)

        x = self.conv2(x, edge_index)

        return x


# -----------------------------
# Link scoring
# -----------------------------

def link_score(embeddings, source, target):

    return torch.sigmoid(
        torch.sum(
            embeddings[source] * embeddings[target]
        )
    )


# -----------------------------
# Main
# -----------------------------

def main():

    data, nodes = load_graph()

    model = GCN()

    embeddings = model(
        data.x,
        data.edge_index
    )

    print("\nGNN GRAPH")
    print("---------")
    print(f"Nodes: {data.num_nodes}")
    print(f"Edges: {data.num_edges}")
    print(f"Embedding size: {embeddings.shape[1]}")

    print("\nNODE EMBEDDINGS")
    print("----------------")

    for i, person in enumerate(nodes):

        print(
            f"{person}: "
            f"{embeddings[i].detach().numpy()}"
        )

    # Example prediction
    source = 0
    target = 2

    score = link_score(
        embeddings,
        source,
        target
    )

    print("\nEXAMPLE LINK SCORE")
    print("------------------")
    print(
        f"{nodes[source]} -> {nodes[target]}: "
        f"{score.item():.4f}"
    )


if __name__ == "__main__":
    main()