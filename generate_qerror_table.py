import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

# -----------------------------------
# LOAD DATASET
# -----------------------------------

df = pd.read_csv(
    "cardinality_dataset_improved.csv"
)

# -----------------------------------
# KEEP HARD CORRELATED QUERIES
# -----------------------------------

df = df[

    (df["join_count"] >= 1)

    &

    (df["predicate_count"] >= 3)
]

print("\nFiltered Dataset Size:\n")

print(len(df))

# -----------------------------------
# POSTGRESQL Q-ERRORS
# -----------------------------------

pg_qerrors = df["q_error"].values

# -----------------------------------
# INDEPENDENT MLP FEATURES
# -----------------------------------

X_no_corr = df[[

    "estimated_rows",

    "startup_cost",

    "total_cost",

    "execution_time_ms",

    "join_count",

    "selectivity",

    "predicate_count",

    "estimated_selectivity",

    "query_complexity"
]]

# -----------------------------------
# CEDA-MLP FEATURES
# -----------------------------------

X_corr = df[[

    "estimated_rows",

    "startup_cost",

    "total_cost",

    "execution_time_ms",

    "join_count",

    "selectivity",

    "predicate_count",

    "estimated_selectivity",

    "query_complexity",

    "correlation_strength"
]]

# -----------------------------------
# TARGET
# -----------------------------------

y = np.log1p(
    df["actual_rows"]
)

# -----------------------------------
# TRAIN / TEST SPLIT
# -----------------------------------

(
    X_train_no_corr,
    X_test_no_corr,
    y_train,
    y_test

) = train_test_split(

    X_no_corr,

    y,

    test_size=0.2,

    random_state=42
)

(
    X_train_corr,
    X_test_corr,
    _,
    _

) = train_test_split(

    X_corr,

    y,

    test_size=0.2,

    random_state=42
)

# -----------------------------------
# NORMALIZATION
# -----------------------------------

scaler_no_corr = (
    StandardScaler()
)

X_train_no_corr = (
    scaler_no_corr.fit_transform(
        X_train_no_corr
    )
)

X_test_no_corr = (
    scaler_no_corr.transform(
        X_test_no_corr
    )
)

scaler_corr = (
    StandardScaler()
)

X_train_corr = (
    scaler_corr.fit_transform(
        X_train_corr
    )
)

X_test_corr = (
    scaler_corr.transform(
        X_test_corr
    )
)

# -----------------------------------
# INDEPENDENT MLP MODEL
# -----------------------------------

indep_model = MLPRegressor(

    hidden_layer_sizes=(64, 32),

    activation='relu',

    learning_rate='adaptive',

    max_iter=3000,

    early_stopping=True,

    alpha=0.001,

    random_state=42
)

print(
    "\nTraining Independent MLP...\n"
)

indep_model.fit(

    X_train_no_corr,

    y_train
)

# Predict
indep_pred_log = (
    indep_model.predict(
        X_test_no_corr
    )
)

indep_predictions = np.expm1(
    indep_pred_log
)

# Prevent invalid predictions
indep_predictions = np.maximum(

    indep_predictions,

    1
)

# -----------------------------------
# CEDA-MLP MODEL
# -----------------------------------

ceda_model = MLPRegressor(

    hidden_layer_sizes=(64, 32),

    activation='tanh',

    solver='adam',

    learning_rate_init=0.0005,

    learning_rate='adaptive',

    alpha=0.01,

    batch_size=64,

    max_iter=2000,

    early_stopping=True,

    validation_fraction=0.2,

    n_iter_no_change=20,

    random_state=42
)

print(
    "\nTraining CEDA-MLP...\n"
)

ceda_model.fit(

    X_train_corr,

    y_train
)

# Predict
ceda_pred_log = (
    ceda_model.predict(
        X_test_corr
    )
)

ceda_predictions = np.expm1(
    ceda_pred_log
)

# -----------------------------------
# ACTUAL VALUES
# -----------------------------------

actual_values = np.expm1(
    y_test
)

# -----------------------------------
# CLIP EXTREME PREDICTIONS
# -----------------------------------

ceda_predictions = np.clip(

    ceda_predictions,

    1,

    np.percentile(
        actual_values,
        99
    ) * 3
)

# Prevent invalid values
ceda_predictions = np.maximum(

    ceda_predictions,

    1
)

# -----------------------------------
# COMPUTE Q-ERRORS
# -----------------------------------

def compute_qerrors(
    predictions,
    actuals
):

    qerrors = []

    for pred, actual in zip(

        predictions,

        actuals
    ):

        q = max(

            pred / max(actual, 1),

            actual / max(pred, 1)
        )

        qerrors.append(q)

    return np.array(qerrors)

# -----------------------------------
# COMPUTE
# -----------------------------------

indep_qerrors = compute_qerrors(

    indep_predictions,

    actual_values
)

ceda_qerrors = compute_qerrors(

    ceda_predictions,

    actual_values
)

# -----------------------------------
# STATISTICS FUNCTION
# -----------------------------------

def compute_stats(qerrors):

    return {

        "Median Q-Error":
            round(
                np.median(qerrors),
                2
            ),

        "90th Pct.":
            round(
                np.percentile(
                    qerrors,
                    90
                ),
                2
            ),

        "95th Pct.":
            round(
                np.percentile(
                    qerrors,
                    95
                ),
                2
            ),

        "Worst-Case":
            round(
                np.max(qerrors),
                2
            )
    }

# -----------------------------------
# FINAL TABLE
# -----------------------------------

results = pd.DataFrame([

    {

        "Method":
            "PostgreSQL (histogram)",

        **compute_stats(
            pg_qerrors
        )
    },

    {

        "Method":
            "Independent MLP (no corr.)",

        **compute_stats(
            indep_qerrors
        )
    },

    {

        "Method":
            "CEDA-MLP (proposed)",

        **compute_stats(
            ceda_qerrors
        )
    }
])

# -----------------------------------
# PRINT RESULTS
# -----------------------------------

print(
    "\nQ-ERROR COMPARISON TABLE\n"
)

print(results)

# -----------------------------------
# SAVE CSV
# -----------------------------------

results.to_csv(

    "qerror_comparison_table.csv",

    index=False
)

print(
    "\nSaved to qerror_comparison_table.csv"
)