import json
import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from torch_geometric.transforms import RandomLinkSplit


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
# GCN
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
# Link predictor
# -----------------------------

def predict_links(embeddings, edge_label_index):

    source = edge_label_index[0]
    target = edge_label_index[1]

    scores = (
        embeddings[source] *
        embeddings[target]
    ).sum(dim=1)

    return scores


# -----------------------------
# Main
# -----------------------------

def main():

    data, nodes = load_graph()

    # Split existing edges into train/validation/test
    transform = RandomLinkSplit(
        num_val=0.2,
        num_test=0.2,
        is_undirected=False,
        add_negative_train_samples=True
    )

    train_data, val_data, test_data = transform(data)

    model = GCN()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.01
    )

    # -------------------------
    # Training
    # -------------------------

    print("\nTRAINING GNN")
    print("------------")

    for epoch in range(1, 101):

        model.train()

        optimizer.zero_grad()

        embeddings = model(
            train_data.x,
            train_data.edge_index
        )

        scores = predict_links(
            embeddings,
            train_data.edge_label_index
        )

        loss = F.binary_cross_entropy_with_logits(
            scores,
            train_data.edge_label.float()
        )

        loss.backward()

        optimizer.step()

        if epoch % 10 == 0:
            print(
                f"Epoch {epoch:3d} | "
                f"Loss: {loss.item():.4f}"
            )

    print("\nTraining complete.")

    # -------------------------
    # Test
    # -------------------------

    model.eval()

    with torch.no_grad():

        embeddings = model(
            test_data.x,
            test_data.edge_index
        )

        scores = torch.sigmoid(
            predict_links(
                embeddings,
                test_data.edge_label_index
            )
        )

    print("\nTEST LINK SCORES")
    print("----------------")

    for i in range(
        min(10, len(scores))
    ):

        source = test_data.edge_label_index[0][i].item()
        target = test_data.edge_label_index[1][i].item()

        label = test_data.edge_label[i].item()

        print(
            f"{nodes[source]} -> {nodes[target]} | "
            f"score={scores[i].item():.4f} | "
            f"actual={int(label)}"
        )


if __name__ == "__main__":
    main()