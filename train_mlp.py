import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Load dataset
df = pd.read_csv("cardinality_dataset.csv")

print(df.head())

# Features
X = df[[
    "estimated_rows",
    "startup_cost",
    "total_cost",
    "execution_time_ms"
]]

# Target
y = df["actual_rows"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create MLP model
model = MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    max_iter=1000,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Evaluation
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\nRESULTS")
print("MAE:", mae)
print("R2:", r2)

# Compare predictions
results = pd.DataFrame({
    "Actual": y_test,
    "Predicted": predictions
})

print(results.head(20))

# Save predictions
results.to_csv("mlp_predictions.csv", index=False)

print("\nPredictions saved to mlp_predictions.csv")