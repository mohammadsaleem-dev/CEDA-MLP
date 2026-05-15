# CEDA-MLP: Correlation-Aware Cardinality Estimation Using Deep Neural Networks for Skewed Database Workloads

## Overview

CEDA-MLP (Correlation-Enhanced Deep Architecture for Multi-Layer Perceptron) is a machine learning-based cardinality estimation framework designed to improve SQL query optimization under correlated and skewed database workloads.

Traditional database systems such as PostgreSQL rely on histogram-based estimators that assume attribute independence, often producing severe estimation errors for complex multi-join queries. CEDA-MLP introduces a correlation-aware neural architecture that significantly improves tail-error robustness and query execution efficiency.

This project evaluates PostgreSQL, an Independent MLP baseline, and the proposed CEDA-MLP model using the TPC-H benchmark.

---

# Key Features

* Correlation-aware cardinality estimation
* PostgreSQL workload integration
* TPC-H benchmark evaluation
* Q-error analysis and comparison
* Query execution time benchmarking
* Tail-error robustness improvements
* Lightweight neural network deployment
* Execution-time speedup evaluation
* Automated feature engineering pipeline
* Visualization and chart generation

---

# Final Experimental Results

## Q-Error Comparison

| Method                     | Median Q-Error | 90th Percentile | 95th Percentile | Worst-Case |
| -------------------------- | -------------- | --------------- | --------------- | ---------- |
| PostgreSQL (histogram)     | 1.55×          | 73.00×          | 188.05×         | 319.00×    |
| Independent MLP (no corr.) | 1.14×          | 12.69×          | 23.43×          | 1424.49×   |
| CEDA-MLP (proposed)        | 1.08×          | 4.27×           | 8.28×           | 98.20×     |

## Execution Time Results

| Query                 | PostgreSQL (s) | Indep. MLP (s) | CEDA-MLP (s) | Speedup |
| --------------------- | -------------- | -------------- | ------------ | ------- |
| Simple Predicate      | 0.30           | 0.26           | 0.23         | 1.30×   |
| Correlated Orders     | 0.25           | 0.22           | 0.19         | 1.32×   |
| Customer-Orders Join  | 1.01           | 0.88           | 0.77         | 1.31×   |
| Correlated Lineitem   | 1.16           | 1.01           | 0.88         | 1.32×   |
| Multi-Join Skewed     | 2.17           | 1.89           | 1.65         | 1.32×   |
| High-Selectivity Join | 0.59           | 0.51           | 0.45         | 1.31×   |
| Average               | 0.91           | 0.80           | 0.70         | 1.30×   |

---

# Architecture

CEDA-MLP uses:

* Correlation-aware feature engineering
* Selectivity analysis
* Query complexity encoding
* Join-aware workload modeling
* Multi-layer perceptron neural networks
* Tail-error stabilization techniques

Pipeline:

```text
SQL Query
   ↓
Feature Extraction
   ↓
Correlation Encoding
   ↓
CEDA-MLP Model
   ↓
Cardinality Prediction
   ↓
Improved Query Optimization
```

---

# Technologies Used

* Python 3.14
* PostgreSQL 16
* scikit-learn
* pandas
* NumPy
* matplotlib
* psycopg2
* TPC-H Benchmark
* VS Code
* Ubuntu / Windows

---

# Project Structure

```text
CEDA-MLP/
│
├── collect_data.py
├── improve_dataset_features.py
├── generate_qerror_table.py
├── compare_models_corr.py
├── compare_models_no_corr.py
├── execution_time_compare.py
├── cardinality_dataset.csv
├── cardinality_dataset_improved.csv
├── qerror_comparison_table.csv
├── execution_time_results.csv
├── model_comparison_corr.csv
├── charts/
├── figures/
├── README.md
└── requirements.txt
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/CEDA-MLP.git
cd CEDA-MLP
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

## 3. Activate Environment

### Windows

```powershell
venv\Scripts\activate
```

### Linux / Ubuntu

```bash
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# PostgreSQL Setup

Install PostgreSQL and load the TPC-H benchmark database.

Update database credentials inside:

```python
collect_data.py
```

Example:

```python
conn = psycopg2.connect(
    host="localhost",
    database="tpch",
    user="postgres",
    password="YOUR_PASSWORD"
)
```

---

# Running the Project

## Step 1 — Collect Query Workload Data

```bash
python collect_data.py
```

## Step 2 — Generate Additional Features

```bash
python improve_dataset_features.py
```

## Step 3 — Generate Q-Error Results

```bash
python generate_qerror_table.py
```

## Step 4 — Compare Models

```bash
python compare_models_corr.py
```

```bash
python compare_models_no_corr.py
```

## Step 5 — Execution-Time Benchmarking

```bash
python execution_time_compare.py
```

---

# Research Contributions

* Introduced a lightweight correlation-aware cardinality estimation framework
* Reduced catastrophic estimation failures on skewed workloads
* Improved tail-error robustness significantly
* Achieved lower query execution time than PostgreSQL and Independent MLP
* Demonstrated practical ML integration for database query optimization

---

# Limitations

* Current implementation models pairwise correlations only
* Requires retraining under heavy workload drift
* Evaluated primarily on TPC-H Scale Factor 1
* Not yet generalized to schema-independent learning

---

# Future Work

* Transformer-based query encoders
* Graph Neural Networks for join modeling
* Online adaptive learning
* Distributed database optimization
* Higher-order correlation modeling
* Larger benchmark evaluation (TPC-DS / JOB)

---

# Citation

If you use this project in research, please cite:

```bibtex
@article{CEDAMLP2026,
  title={CEDA-MLP: Correlation-Aware Cardinality Estimation Using Deep Neural Networks for Skewed Database Workloads},
  author={Mohammad Sohail Saleem and Ali Abu Foudeh},
  year={2026}
}
```

---

# Authors

## Mohammad Sohail Saleem

Princess Sumaya University for Technology
M.S. Computer Science

## Ali Abu Foudeh

Princess Sumaya University for Technology
M.S. Computer Science

---

# License

This project is intended for academic and research purposes.

---

# Acknowledgment

This research was conducted as part of the Master of Science program in Computer Science at Princess Sumaya University for Technology (PSUT).
