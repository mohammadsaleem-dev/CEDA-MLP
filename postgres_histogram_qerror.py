import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("cardinality_dataset.csv")

# PostgreSQL estimates
estimated = df["estimated_rows"]

# Actual cardinalities
actual = df["actual_rows"]

# Compute Q-errors
qerrors = []

for est, act in zip(estimated, actual):

    q = max(
        est / max(act, 1),
        act / max(est, 1)
    )

    qerrors.append(q)

qerrors = np.array(qerrors)

print("\nPostgreSQL (Histogram) Q-Error Statistics\n")

print(f"Median Q-Error: {np.median(qerrors):.2f}x")

print(f"90th Percentile: {np.percentile(qerrors, 90):.2f}x")

print(f"95th Percentile: {np.percentile(qerrors, 95):.2f}x")

print(f"Worst Case Q-Error: {np.max(qerrors):.2f}x")