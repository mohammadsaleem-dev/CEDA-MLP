# compare_models_corr.py

import pandas as pd
import time
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor

# Load dataset
df = pd.read_csv("cardinality_dataset.csv")

# FEATURES WITH CORRELATION FEATURE
# CEDA-MLP VERSION

X = df[[
    "estimated_rows",
    "startup_cost",
    "total_cost",
    "execution_time_ms",
    "correlation_feature",
    "join_count",
    "selectivity"
]]

# Target
y = df["actual_rows"]

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Models
models = {

    "Linear Regression":
        LinearRegression(),

    "Decision Tree":
        DecisionTreeRegressor(
            random_state=42
        ),

    "Random Forest":
        RandomForestRegressor(
            n_estimators=100,
            random_state=42
        ),

    "Gradient Boosting":
        GradientBoostingRegressor(
            random_state=42
        ),

    "MLP Regressor":
        MLPRegressor(
            hidden_layer_sizes=(64, 32),
            max_iter=1000,
            random_state=42
        )
}

results = []

print("\nTRAINING MODELS...\n")

# Train & Evaluate
for name, model in models.items():

    print(f"Training {name}...")

    # TRAINING TIME
    train_start = time.time()

    model.fit(X_train, y_train)

    training_time = round(
        time.time() - train_start,
        2
    )

    # SAVE MODEL
    model_filename = (
        name.replace(" ", "_") + ".pkl"
    )

    joblib.dump(model, model_filename)

    # MODEL SIZE
    model_size = round(
        os.path.getsize(model_filename)
        / (1024 * 1024),
        2
    )

    # INFERENCE LATENCY
    inference_start = time.time()

    predictions = model.predict(X_test)

    inference_latency = (
        (time.time() - inference_start)
        / len(X_test)
    ) * 1000

    # METRICS
    mae = mean_absolute_error(
        y_test,
        predictions
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    results.append({

        "Model": name,

        "MAE": round(mae, 3),

        "R2": round(r2, 6),

        "Training Time (s)": training_time,

        "Model Size (MB)": model_size,

        "Inference Latency (ms)":
            round(inference_latency, 4)
    })

# Results table
results_df = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print(results_df)

# Save results
results_df.to_csv(
    "model_comparison_corr.csv",
    index=False
)

print(
    "\nResults saved to "
    "model_comparison_corr.csv"
)