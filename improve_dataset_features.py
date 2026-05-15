import pandas as pd

# -----------------------------------
# LOAD DATASET
# -----------------------------------

df = pd.read_csv(
    "cardinality_dataset.csv"
)

# -----------------------------------
# FEATURE 1
# Predicate Count
# -----------------------------------

predicate_counts = []

for q in df["query"]:

    q_lower = q.lower()

    count = (

        q_lower.count("where")

        + q_lower.count("and")

        + q_lower.count("or")
    )

    predicate_counts.append(count)

df["predicate_count"] = (
    predicate_counts
)

# -----------------------------------
# FEATURE 2
# Estimated Selectivity
# -----------------------------------

estimated_selectivity = []

for est, sel in zip(

    df["estimated_rows"],

    df["selectivity"]
):

    total_rows = est / max(
        sel,
        0.000001
    )

    est_sel = est / max(
        total_rows,
        1
    )

    estimated_selectivity.append(
        est_sel
    )

df["estimated_selectivity"] = (
    estimated_selectivity
)

# -----------------------------------
# FEATURE 3
# Query Complexity
# -----------------------------------

query_complexity = []

for joins, preds in zip(

    df["join_count"],

    df["predicate_count"]
):

    complexity = (
        joins * preds
    )

    query_complexity.append(
        complexity
    )

df["query_complexity"] = (
    query_complexity
)

# -----------------------------------
# FEATURE 4
# REALISTIC CORRELATION STRENGTH
# -----------------------------------

correlation_strength = []

for joins, preds, sel in zip(

    df["join_count"],

    df["predicate_count"],

    df["selectivity"]
):

    strength = (

        joins

        * preds

        * sel
    )

    correlation_strength.append(
        strength
    )

df["correlation_strength"] = (
    correlation_strength
)

# -----------------------------------
# SAVE DATASET
# -----------------------------------

df.to_csv(

    "cardinality_dataset_improved.csv",

    index=False
)

print(
    "\nImproved dataset saved:"
)

print(
    "cardinality_dataset_improved.csv"
)

print("\nNew Features Added:\n")

print(df[[

    "predicate_count",

    "estimated_selectivity",

    "query_complexity",

    "correlation_strength"

]].head())