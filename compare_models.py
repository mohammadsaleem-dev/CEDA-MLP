import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor

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

# Target
y = df["actual_rows"]

# Split dataset
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
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            learning_rate='adaptive',
            max_iter=2000,
            random_state=42
        )
}

results = []

# Train and evaluate
for name, model in models.items():

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    r2 = r2_score(y_test, predictions)

    results.append({

        "Model": name,

        "MAE": mae,

        "R2": r2
    })

# Results table
results_df = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print(results_df)

# Save results
results_df.to_csv("model_comparison.csv", index=False)

print("\nResults saved to model_comparison.csv")