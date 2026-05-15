import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("cardinality_dataset.csv")

q_errors = df["q_error"]

median_q = np.median(q_errors)

pct90 = np.percentile(q_errors, 90)

pct95 = np.percentile(q_errors, 95)

worst = np.max(q_errors)

print("\nQ-ERROR STATISTICS\n")

print(f"Median Q-Error: {median_q:.2f}x")

print(f"90th Percentile: {pct90:.2f}x")

print(f"95th Percentile: {pct95:.2f}x")

print(f"Worst Case Q-Error: {worst:.2f}x")