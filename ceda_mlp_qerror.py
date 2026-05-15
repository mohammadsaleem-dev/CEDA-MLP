import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv("cardinality_dataset.csv")

# Features
X = df[[

    "estimated_rows",

    "startup_cost",

    "total_cost",

    "execution_time_ms",

    "correlation_feature",

    "join_count",

    "selectivity"
]]

# Target (log-space)
y = np.log1p(df["actual_rows"])

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42
)

# NORMALIZE FEATURES
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

X_test = scaler.transform(X_test)

# MLP Model
model = MLPRegressor(

    hidden_layer_sizes=(128, 64, 32),

    activation='relu',

    learning_rate='adaptive',

    max_iter=3000,

    early_stopping=True,

    random_state=42
)

print("\nTraining CEDA-MLP...\n")

# Train
model.fit(X_train, y_train)

# Predict in log-space
predictions_log = model.predict(X_test)

# Convert back
predictions = np.expm1(predictions_log)

# Prevent negatives/zeros
predictions = np.maximum(predictions, 1)

# Actual values
actual_values = np.expm1(y_test)

# Compute Q-errors
qerrors = []

for pred, actual in zip(predictions, actual_values):

    q = max(

        pred / max(actual, 1),

        actual / max(pred, 1)
    )

    qerrors.append(q)

qerrors = np.array(qerrors)

# Statistics
median_q = np.median(qerrors)

pct90 = np.percentile(qerrors, 90)

pct95 = np.percentile(qerrors, 95)

worst = np.max(qerrors)

print("\nCEDA-MLP Q-ERROR STATISTICS\n")

print(f"Median Q-Error: {median_q:.2f}x")

print(f"90th Percentile: {pct90:.2f}x")

print(f"95th Percentile: {pct95:.2f}x")

print(f"Worst Case Q-Error: {worst:.2f}x")