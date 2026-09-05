import json
import torch
import torch.nn.functional as F

from torch_geometric.data import Data
from torch_geometric.transforms import RandomLinkSplit
from torch_geometric.nn import GCNConv

from sklearn.metrics import roc_auc_score, average_precision_score


# --------------------------------------------------
# Load Graph
# --------------------------------------------------

with open(
    "data/processed/graph.json",
    "r",
    encoding="utf-8"
) as f:

    graph = json.load(f)


# --------------------------------------------------
# Map Person IDs to Numeric IDs
# --------------------------------------------------

person_ids = sorted(
    set(
        [edge["source"] for edge in graph["edges"]]
        +
        [edge["target"] for edge in graph["edges"]]
    )
)

person_to_index = {
    person: index
    for index, person in enumerate(person_ids)
}


# --------------------------------------------------
# Create Edge Index
# --------------------------------------------------

edge_list = []

for edge in graph["edges"]:

    source = person_to_index[edge["source"]]
    target = person_to_index[edge["target"]]

    edge_list.append([source, target])


edge_index = torch.tensor(
    edge_list,
    dtype=torch.long
).t().contiguous()


# --------------------------------------------------
# Node Features
# --------------------------------------------------

num_nodes = len(person_ids)

x = torch.ones(
    (num_nodes, 1),
    dtype=torch.float
)


data = Data(
    x=x,
    edge_index=edge_index
)


# --------------------------------------------------
# Train / Validation / Test Split
# --------------------------------------------------

splitter = RandomLinkSplit(
    num_val=0.15,
    num_test=0.15,
    is_undirected=True,
    add_negative_train_samples=True
)

train_data, val_data, test_data = splitter(data)


# --------------------------------------------------
# GCN Model
# --------------------------------------------------

class GCN(torch.nn.Module):

    def __init__(self):

        super().__init__()

        self.conv1 = GCNConv(1, 16)
        self.conv2 = GCNConv(16, 8)

    def encode(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = F.relu(x)

        x = self.conv2(x, edge_index)

        return x

    def decode(self, z, edge_label_index):

        source = edge_label_index[0]
        target = edge_label_index[1]

        return (
            z[source] * z[target]
        ).sum(dim=1)


# --------------------------------------------------
# Initialize Model
# --------------------------------------------------

model = GCN()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)


# --------------------------------------------------
# Training
# --------------------------------------------------

print("\nTRAINING GNN")
print("------------")

for epoch in range(1, 101):

    model.train()

    optimizer.zero_grad()

    z = model.encode(
        train_data.x,
        train_data.edge_index
    )

    predictions = model.decode(
        z,
        train_data.edge_label_index
    )

    loss = F.binary_cross_entropy_with_logits(
        predictions,
        train_data.edge_label.float()
    )

    loss.backward()

    optimizer.step()

    if epoch % 10 == 0:

        print(
            f"Epoch {epoch:03d} | "
            f"Loss: {loss.item():.4f}"
        )


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

model.eval()

with torch.no_grad():

    z = model.encode(
        test_data.x,
        test_data.edge_index
    )

    logits = model.decode(
        z,
        test_data.edge_label_index
    )

    probabilities = torch.sigmoid(logits)


y_true = test_data.edge_label.cpu().numpy()

y_score = probabilities.cpu().numpy()


# --------------------------------------------------
# Evaluation Metrics
# --------------------------------------------------

try:

    roc_auc = roc_auc_score(
        y_true,
        y_score
    )

    average_precision = average_precision_score(
        y_true,
        y_score
    )

    print("\nMODEL EVALUATION")
    print("----------------")
    print(
        f"ROC-AUC:            {roc_auc:.4f}"
    )

    print(
        f"Average Precision:  {average_precision:.4f}"
    )

except ValueError as e:

    print(
        "\nEvaluation could not be calculated:"
    )

    print(e)


# --------------------------------------------------
# Top Predicted Links
# --------------------------------------------------

print("\nPREDICTED RELATIONSHIPS")
print("-----------------------")


test_edges = test_data.edge_label_index.t()

results = []

for i, edge in enumerate(test_edges):

    source_index = edge[0].item()
    target_index = edge[1].item()

    source = person_ids[source_index]
    target = person_ids[target_index]

    score = y_score[i]

    results.append(
        (
            source,
            target,
            float(score)
        )
    )


results.sort(
    key=lambda item: item[2],
    reverse=True
)


for source, target, score in results[:10]:

    print(
        f"{source} -> {target} | "
        f"probability={score:.4f}"
    )