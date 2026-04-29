import mysql.connector
import pandas as pd
import random
import time
import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
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

    # SIMPLE FILTERS
    "SELECT * FROM students WHERE gpa > 3.0",
    "SELECT * FROM students WHERE gpa < 2.5",
    "SELECT * FROM students WHERE city='Amman'",
    "SELECT * FROM students WHERE city='Zarqa'",
    "SELECT * FROM students WHERE dept_id=3",
    "SELECT * FROM students WHERE status='Active'",
    "SELECT * FROM students WHERE gender='Male'",
    "SELECT * FROM students WHERE enrollment_year=2024",

    # RANGE
    "SELECT * FROM students WHERE gpa BETWEEN 2.5 AND 3.5",
    "SELECT * FROM students WHERE student_id BETWEEN 100 AND 1000",

    # SORT
    "SELECT * FROM students ORDER BY gpa DESC LIMIT 100",
    "SELECT * FROM students ORDER BY first_name LIMIT 50",

    # GROUP BY
    "SELECT dept_id, AVG(gpa) FROM students GROUP BY dept_id",
    "SELECT city, COUNT(*) FROM students GROUP BY city",
    "SELECT grade, COUNT(*) FROM enrollments GROUP BY grade",

    # JOINS
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
# FEATURES / TARGET
# ==================================================

X = df[["joins", "where", "groupby", "orderby", "length"]]
y = df["runtime_ms"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# ==================================================
# MODELS
# ==================================================

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        random_state=42
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        random_state=42
    )
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

    results.append([name, mae, r2])

    print("================================")
    print(name)
    print("MAE:", round(mae, 3))
    print("R2 :", round(r2, 3))

    if r2 > best_r2:
        best_r2 = r2
        best_model = model
        best_name = name
        best_pred = pred

# ==================================================
# SAVE MODEL RESULTS CSV
# ==================================================

results_df = pd.DataFrame(
    results,
    columns=["Model", "MAE", "R2"]
)

results_df.to_csv("model_results.csv", index=False)

print("================================")
print("Best Model:", best_name)

# ==================================================
# GRAPH 1: ACTUAL VS PREDICTED
# ==================================================

plt.figure(figsize=(8,5))
plt.scatter(y_test, best_pred)
plt.xlabel("Actual Runtime (ms)")
plt.ylabel("Predicted Runtime (ms)")
plt.title("Best Model: Actual vs Predicted")
plt.tight_layout()
plt.savefig("results.png")
plt.close()

# ==================================================
# GRAPH 2: MODEL COMPARISON
# ==================================================

plt.figure(figsize=(8,5))
plt.bar(results_df["Model"], results_df["R2"])
plt.xticks(rotation=20)
plt.ylabel("R2 Score")
plt.title("Model Comparison")
plt.tight_layout()
plt.savefig("model_comparison.png")
plt.close()

# ==================================================
# GRAPH 3: FEATURE IMPORTANCE
# ==================================================

if hasattr(best_model, "feature_importances_"):

    importance = best_model.feature_importances_
    features = X.columns

    plt.figure(figsize=(8,5))
    plt.bar(features, importance)
    plt.title("Feature Importance")
    plt.ylabel("Importance")
    plt.tight_layout()
    plt.savefig("feature_importance.png")
    plt.close()

print("All graphs saved.")

# ==================================================
# CLOSE CONNECTION
# ==================================================

cursor.close()
conn.close()