import mysql.connector
import pandas as pd
import random
import time
import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# ==================================================
# MYSQL CONNECTION
# ==================================================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Moody5ds*",
    database="researchdb"
)

cursor = conn.cursor()

# ==================================================
# QUERY WORKLOAD
# ==================================================

queries = [

    "SELECT * FROM students WHERE gpa > 3.0",
    "SELECT * FROM students WHERE gpa < 2.5",
    "SELECT * FROM students WHERE city='Amman'",
    "SELECT * FROM students WHERE city='Zarqa'",
    "SELECT * FROM students WHERE dept_id=3",
    "SELECT * FROM students WHERE status='Active'",
    "SELECT * FROM students WHERE gender='Male'",
    "SELECT * FROM students WHERE enrollment_year=2024",

    "SELECT * FROM students WHERE gpa BETWEEN 2.5 AND 3.5",
    "SELECT * FROM students WHERE student_id BETWEEN 100 AND 1000",

    "SELECT * FROM students ORDER BY gpa DESC LIMIT 100",
    "SELECT * FROM students ORDER BY first_name LIMIT 50",

    "SELECT dept_id, AVG(gpa) FROM students GROUP BY dept_id",
    "SELECT city, COUNT(*) FROM students GROUP BY city",
    "SELECT grade, COUNT(*) FROM enrollments GROUP BY grade",

    """
    SELECT s.first_name, e.grade
    FROM students s
    JOIN enrollments e ON s.student_id=e.student_id
    WHERE s.gpa > 3.0
    """,

    """
    SELECT s.first_name, c.course_title
    FROM students s
    JOIN enrollments e ON s.student_id=e.student_id
    JOIN course_sections cs ON e.section_id=cs.section_id
    JOIN courses c ON cs.course_id=c.course_id
    WHERE s.gpa > 2.5
    """,

    """
    SELECT d.dept_name, AVG(s.gpa)
    FROM students s
    JOIN departments d ON s.dept_id=d.dept_id
    GROUP BY d.dept_name
    """,

    """
    SELECT c.course_title, COUNT(e.enroll_id)
    FROM courses c
    JOIN course_sections cs ON c.course_id=cs.course_id
    JOIN enrollments e ON cs.section_id=e.section_id
    GROUP BY c.course_title
    ORDER BY COUNT(e.enroll_id) DESC
    """
]

# ==================================================
# DATA COLLECTION
# ==================================================

data = []

for i in range(500):

    q = random.choice(queries)

    start = time.time()
    cursor.execute(q)
    cursor.fetchall()
    end = time.time()

    runtime = (end - start) * 1000

    row = {
        "joins": q.upper().count("JOIN"),
        "where": 1 if "WHERE" in q.upper() else 0,
        "groupby": 1 if "GROUP BY" in q.upper() else 0,
        "orderby": 1 if "ORDER BY" in q.upper() else 0,
        "length": len(q),
        "runtime_ms": runtime
    }

    data.append(row)

df = pd.DataFrame(data)
df.to_csv("dataset.csv", index=False)

print("Dataset saved.")

# ==================================================
# QUERY TYPE (for hybrid model)
# ==================================================
df["query_type"] = df["joins"].apply(
    lambda x: "simple" if x <= 1 else ("medium" if x <= 3 else "complex")
)

# ==================================================
# FEATURES / TARGET
# ==================================================

features = ["joins", "where", "groupby", "orderby", "length"]

X = df[features]
y = df["runtime_ms"]

# ==================================================
# SMALL DATA EXPERIMENT
# ==================================================

train_sizes = [50, 100, 200, 300, 500]

for size in train_sizes:

    mae_list = []
    r2_list = []

    for run in range(5):

        df_sample = df.sample(n=size)

        X_sample = df_sample[features]
        y_sample = df_sample["runtime_ms"]

        X_train, X_test, y_train, y_test = train_test_split(
            X_sample, y_sample, test_size=0.2
        )

        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        mae_list.append(mean_absolute_error(y_test, pred))
        r2_list.append(r2_score(y_test, pred))

    print("====================================")
    print("Training Size:", size)
    print("Avg MAE:", round(sum(mae_list)/5, 3))
    print("Avg R2 :", round(sum(r2_list)/5, 3))

# ==================================================
# FINAL TRAIN
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==================================================
# MODELS
# ==================================================

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
}

results = []

best_r2 = -999
best_model = None
best_name = ""
best_pred = None

for name, model in models.items():

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))

    results.append([name, mae, r2, rmse])

    print("================================")
    print(name)
    print("MAE :", round(mae, 3))
    print("R2  :", round(r2, 3))
    print("RMSE:", round(rmse, 3))

    if r2 > best_r2:
        best_r2 = r2
        best_model = model
        best_name = name
        best_pred = pred

# ==================================================
# SAVE RESULTS
# ==================================================

results_df = pd.DataFrame(
    results,
    columns=["Model", "MAE", "R2", "RMSE"]
)

results_df.to_csv("model_results.csv", index=False)

print("================================")
print("Best Model:", best_name)

# ==================================================
# HYBRID MODEL (SQP-HybridBoost)
# ==================================================

print("\n================================")
print("SQP-HybridBoost (Hybrid Model)")
print("================================")

models_hybrid = {
    "simple": DecisionTreeRegressor(random_state=42),
    "medium": RandomForestRegressor(n_estimators=100, random_state=42),
    "complex": GradientBoostingRegressor(n_estimators=100, random_state=42)
}

hybrid_models = {}

# Train separate models per query type
for q_type in ["simple", "medium", "complex"]:

    df_sub = df[df["query_type"] == q_type]

    if len(df_sub) < 10:
        print(f"Skipping {q_type}: not enough samples ({len(df_sub)})")
        continue

    X_sub = df_sub[features]
    y_sub = df_sub["runtime_ms"]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X_sub, y_sub, test_size=0.2, random_state=42
    )

    model = models_hybrid[q_type]
    model.fit(X_tr, y_tr)

    hybrid_models[q_type] = model

    print(f"{q_type} model trained (samples: {len(df_sub)})")


def hybrid_predict(row):
    q_type = row["query_type"]

    if q_type in hybrid_models:
        model = hybrid_models[q_type]
        return model.predict(pd.DataFrame([row[features]]))[0]
    else:
        return best_model.predict(pd.DataFrame([row[features]]))[0]

# Prepare test set with query_type
df_test = X_test.copy()
df_test["runtime_ms"] = y_test.values
df_test["query_type"] = df_test["joins"].apply(
    lambda x: "simple" if x <= 1 else ("medium" if x <= 3 else "complex")
)

# Predictions
hybrid_preds = df_test.apply(hybrid_predict, axis=1)

# Metrics
hybrid_mae = mean_absolute_error(df_test["runtime_ms"], hybrid_preds)
hybrid_r2 = r2_score(df_test["runtime_ms"], hybrid_preds)
hybrid_rmse = np.sqrt(mean_squared_error(df_test["runtime_ms"], hybrid_preds))

print("\n================================")
print("Hybrid Model Results")
print("MAE :", round(hybrid_mae, 3))
print("R2  :", round(hybrid_r2, 3))
print("RMSE:", round(hybrid_rmse, 3))

# Add hybrid results to comparison DataFrame and save
results_df.loc[len(results_df)] = ["SQP-HybridBoost", hybrid_mae, hybrid_r2, hybrid_rmse]
results_df.to_csv("model_results.csv", index=False)

# ==================================================
# FEATURE IMPORTANCE
# ==================================================

if hasattr(best_model, "feature_importances_"):

    importance = best_model.feature_importances_

    print("Feature Importance:")
    for f, imp in zip(features, importance):
        print(f, ":", round(imp, 3))

    plt.figure(figsize=(8,5))
    plt.bar(features, importance)
    plt.title("Feature Importance")
    plt.savefig("feature_importance.png")
    plt.close()

# ==================================================
# GRAPH 1
# ==================================================

plt.figure(figsize=(8,5))
plt.scatter(y_test, best_pred)
plt.xlabel("Actual Runtime (ms)")
plt.ylabel("Predicted Runtime (ms)")
plt.title("Prediction")
plt.savefig("results.png")
plt.close()

# ==================================================
# GRAPH 2
# ==================================================

plt.figure(figsize=(8,5))
plt.bar(results_df["Model"], results_df["R2"])
plt.title("Model Comparison")
plt.savefig("model_comparison.png")
plt.close()

print("All graphs saved.")

# ==================================================
# CLOSE
# ==================================================

cursor.close()
conn.close()