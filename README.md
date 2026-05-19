# CEDA-MLP: Correlation-Aware Cardinality Estimation Using Deep Neural Networks for Skewed Database Workloads

> **IEEE Research Paper** | Princess Sumaya University for Technology, Amman, Jordan

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-MLPRegressor-orange?logo=scikit-learn)](https://scikit-learn.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Benchmark](https://img.shields.io/badge/Benchmark-TPC--H%20SF%3D1-green)](https://www.tpc.org/tpch/)
[![License](https://img.shields.io/badge/License-Academic-lightgrey)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Results](#-key-results)
- [Architecture](#-architecture)
- [Feature Engineering](#-feature-engineering)
- [Experimental Setup](#-experimental-setup)
- [Results](#-results)
- [Installation](#-installation)
- [Usage](#-usage)
- [PostgreSQL Integration](#-postgresql-integration)
- [Limitations & Future Work](#-limitations--future-work)
- [Authors](#-authors)
- [Citation](#-citation)
- [References](#-references)

---

## 🔍 Overview

**CEDA-MLP** (**C**orrelation-**E**nhanced **D**eep **A**rchitecture — **M**ulti-**L**ayer **P**erceptron) is a lightweight feedforward neural network designed to address one of the most persistent bottlenecks in relational query optimization: **cardinality estimation**.

Production databases like PostgreSQL rely on histogram-based estimators that assume **attribute independence**, which causes severe estimation errors on real-world correlated and skewed data. These errors propagate into the query planner, frequently causing the selection of suboptimal execution plans.

CEDA-MLP solves this by:
- **Explicitly encoding inter-attribute correlations** via a pairwise correlation-aware feature (`correlation_strength`)
- **Handling skewed data distributions** found in real-world and benchmark workloads (TPC-H)
- Remaining **lightweight and deployable** alongside an unmodified PostgreSQL instance via `pg_hint_plan`

### Why This Matters

| Failure Mode | Root Cause | Impact |
|---|---|---|
| **Attribute Correlation** | PostgreSQL multiplies independent per-column selectivities | Severe under-estimation on conjunctive predicates |
| **Data Skew** | Uniform-within-bucket assumption in histograms | 1–3 orders of magnitude error on skewed columns |
| **Error Propagation** | Small per-operator errors compound multiplicatively in join trees | Tail Q-errors exceeding 300× on multi-join queries |

---

## 🏆 Key Results

### Q-Error Comparison (TPC-H, SF = 1, 5,000 sub-plans)

| Method | Median Q-Error | 90th Pct. | 95th Pct. | Worst-Case |
|---|---|---|---|---|
| PostgreSQL (histogram) | 1.55× | 73.00× | 188.05× | 319.00× |
| Independent MLP (no corr.) | 1.14× | 12.69× | 23.43× | **1424.49×** |
| **CEDA-MLP (proposed)** | **1.08×** | **4.27×** | **8.28×** | **98.20×** |

### End-to-End Query Execution Time (seconds)

| Query Class | Joins | PostgreSQL | Indep. MLP | CEDA-MLP | Speedup |
|---|---|---|---|---|---|
| Simple Predicate | 0 | 0.30 | 0.26 | 0.23 | 1.30× |
| Correlated Orders | 0 | 0.25 | 0.22 | 0.19 | 1.32× |
| Customer–Orders Join | 1 | 1.01 | 0.88 | 0.77 | 1.31× |
| Correlated Lineitem | 0 | 1.16 | 1.01 | 0.88 | 1.32× |
| Multi-Join Skewed | 2 | 2.17 | 1.89 | 1.65 | 1.32× |
| High-Selectivity Join | 2 | 0.59 | 0.51 | 0.45 | 1.31× |
| **Average** | — | **0.91** | **0.80** | **0.70** | **1.30×** |

### Model Overhead

| Method | Training Time | Model Size | Inference Latency |
|---|---|---|---|
| Independent MLP | ~1.94 s | 0.09 MB | 0.0011 ms |
| **CEDA-MLP** | **~2.69 s** | **0.09 MB** | **0.0011 ms** |

> **No GPU required.** Trains in under 3 seconds on a single CPU core. Inference throughput exceeds **900,000 estimations/second**.

---

## 🏗️ Architecture

CEDA-MLP is a feedforward neural network implemented using `scikit-learn`'s `MLPRegressor`:

```
Input(10) → Dense(64, tanh) → Dense(32, tanh) → Dense(1, linear)
```

**Design Principles:**
1. **Explicit correlation encoding** — input representation captures joint attribute distributions, not only marginal statistics
2. **Practical deployability** — integrates with PostgreSQL without engine modification
3. **Efficient inference** — prediction latency < 2 ms per sub-plan (actual: ~0.0011 ms)

**Training Configuration:**

```python
MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation='tanh',
    solver='adam',
    learning_rate_init=0.0005,
    batch_size=64,
    alpha=0.01,           # L2 regularization
    validation_fraction=0.2,
    early_stopping=True,
    max_iter=2000         # Converges in 80–120 epochs in practice
)
```

The model predicts **log-transformed cardinality** `ln(1 + |Q|)`, with inverse transformation at inference. All features are **log-transformed and z-score normalized**.

---

## 🔧 Feature Engineering

Each training sample represents a **sub-plan** encoded as a 10-dimensional feature vector:

| # | Feature | Description |
|---|---|---|
| 1 | `estimated_rows` | Native PostgreSQL histogram row-count estimate |
| 2 | `startup_cost` | EXPLAIN startup cost |
| 3 | `total_cost` | EXPLAIN total cost |
| 4 | `execution_time_ms` | Actual runtime of previously executed plans (training only) |
| 5 | `join_count` | Number of join predicates in the sub-plan |
| 6 | `selectivity` | Cumulative product of per-predicate selectivities (independence assumption) |
| 7 | `predicate_count` | Total number of filter predicates |
| 8 | `estimated_selectivity` | Planner's row estimate ÷ leaf-level cardinality |
| 9 | `query_complexity` | Heuristic: number of relations and predicates relative to schema |
| **10** | **`correlation_strength`** | **⭐ Scalar summary of inter-attribute correlation statistics (key contribution)** |

### The `correlation_strength` Feature

The core innovation of CEDA-MLP. For each pair of columns `(cᵢ, cⱼ)` that may appear jointly in query predicates:

1. **Offline**: Compute the Pearson correlation coefficient `ρ(cᵢ, cⱼ)` and bivariate selectivity summaries from a representative data sample
2. **At feature-extraction time**: Aggregate per-pair statistics over the predicate pairs present in the query, **weighted by their marginal selectivities**
3. **Result**: A single, well-scaled scalar that is monotonic in the cumulative correlation effect for the sub-plan

This design keeps the input vector compact and uniform across queries of arbitrary shape, while allowing the network to learn that correlated predicates (e.g., `l_shipdate` and `l_receiptdate` in TPC-H LINEITEM) select fewer tuples than the product of independent selectivities would suggest.

---

## 🧪 Experimental Setup

### Benchmark

- **Dataset**: TPC-H at Scale Factor 1 (~1 GB)
- **Tables**: LINEITEM (6M tuples), ORDERS (1.5M), PARTSUPP (800K), PART (200K), CUSTOMER (150K), SUPPLIER (10K), NATION (25), REGION (5)

### Workload

- All **22 standard TPC-H queries**
- **5,000 sub-plan estimation tasks** generated by decomposing queries into constituent sub-plans
- Each sub-plan executed once to record ground-truth cardinality

### Baselines

| Baseline | Description |
|---|---|
| **PostgreSQL (histogram)** | Default estimator using ANALYZE; no extended statistics declared (out-of-the-box configuration) |
| **Independent MLP** | Identical architecture to CEDA-MLP, but without the correlation-aware `correlation_strength` feature — isolates the contribution of correlation encoding |

### Hardware

- Intel Core i7-12700, 32 GB RAM
- PostgreSQL 16 on Ubuntu 22.04
- Each query executed **5 times**; median wall-clock time reported

### Evaluation Metric

The **symmetric Q-error** (Moerkotte & Neumann):

```
Q-error = max(estimate / actual, actual / estimate)
```

- Q-error = 1.0 → perfect estimate
- Q-error > 10× → frequently causes suboptimal join orderings
- Q-error > 100× → widely associated with order-of-magnitude runtime regressions

---

## 📊 Results

### Key Finding: Tail Error Reduction

The most important improvement is in the **high-error tail**, where a single mis-estimated sub-plan can determine the plan choice for the entire query:

- **Worst-case** Q-error: 1424.49× → **98.20×** (14.5× reduction)
- **95th percentile** Q-error: 23.43× → **8.28×** (2.8× reduction)

> ⚠️ **Important counter-intuitive result**: The Independent MLP baseline produced a worst-case error of **1424.49×** — over 4× worse than PostgreSQL's 319×. Simply replacing the histogram with a generic neural network is **not sufficient** and can worsen tail behavior. The correlation-aware encoding is what makes the difference.

### Residual Error Sources

Analysis of the 50 worst remaining Q-errors in CEDA-MLP reveals three patterns:

1. **Three or more correlated attributes** simultaneously — pairwise summaries under-represent higher-order dependencies
2. **Extreme tail values** of skewed columns outside the MCV list — too few training examples for reliable bivariate statistics
3. **Near-zero true cardinality** (< 10 tuples) — Q-error metric amplifies small absolute differences

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/CEDA-MLP.git
cd CEDA-MLP

# Install dependencies
pip install -r requirements.txt
```

### Requirements

```
scikit-learn>=1.0
numpy>=1.21
pandas>=1.3
psycopg2-binary>=2.9      # PostgreSQL connector
sqlalchemy>=1.4
matplotlib>=3.4           # For result visualization
```

### TPC-H Setup

```bash
# Generate TPC-H data at Scale Factor 1
# Download TPC-H toolkit from https://www.tpc.org/tpch/
./dbgen -s 1

# Load into PostgreSQL
psql -U postgres -c "CREATE DATABASE tpch;"
psql -U postgres -d tpch -f load_tpch.sql

# Run ANALYZE to collect baseline statistics
psql -U postgres -d tpch -c "ANALYZE;"
```

---

## 💻 Usage

### 1. Generate Training Data

Collect sub-plan samples with ground-truth cardinalities from PostgreSQL:

```python
from ceda_mlp.data_collection import SubPlanCollector

collector = SubPlanCollector(
    connection_string="postgresql://postgres@localhost/tpch"
)

# Execute TPC-H queries and collect sub-plan statistics
samples = collector.collect(num_samples=5000)
samples.to_csv("data/tpch_subplans.csv", index=False)
```

### 2. Compute Correlation Statistics

```python
from ceda_mlp.correlation import CorrelationAnalyzer

analyzer = CorrelationAnalyzer(
    connection_string="postgresql://postgres@localhost/tpch"
)

# Compute pairwise Pearson correlations for all column pairs
correlation_map = analyzer.compute_pairwise_correlations()
analyzer.save("models/correlation_map.pkl")
```

### 3. Train CEDA-MLP

```python
from ceda_mlp.model import CEDAMLPEstimator
import pandas as pd

# Load training data
df = pd.read_csv("data/tpch_subplans.csv")

# Initialize and train
model = CEDAMLPEstimator(
    hidden_layer_sizes=(64, 32),
    activation='tanh',
    learning_rate_init=0.0005,
    alpha=0.01,
    max_iter=2000,
    early_stopping=True,
    validation_fraction=0.2,
    random_state=42
)

model.fit(df, target_column="true_cardinality")
model.save("models/ceda_mlp.pkl")

print(f"Training time: {model.training_time_:.2f}s")
print(f"Model size: {model.model_size_mb_:.2f} MB")
```

### 4. Evaluate

```python
from ceda_mlp.evaluation import QErrorEvaluator

evaluator = QErrorEvaluator()
results = evaluator.evaluate(
    model=model,
    test_data=df_test,
    baselines=["postgresql", "independent_mlp"]
)

evaluator.print_report(results)
# Outputs Q-error at median, 90th, 95th, and worst-case percentiles
```

### 5. Generate Cardinality Estimates

```python
# Estimate cardinality for a new sub-plan
subplan_features = {
    "estimated_rows": 15000,
    "startup_cost": 0.0,
    "total_cost": 412.5,
    "join_count": 2,
    "selectivity": 0.003,
    "predicate_count": 4,
    "estimated_selectivity": 0.01,
    "query_complexity": 0.6,
    "correlation_strength": 0.72
}

prediction = model.predict(subplan_features)
print(f"Estimated cardinality: {prediction:.0f} rows")
```

---

## 🔌 PostgreSQL Integration

CEDA-MLP is designed to integrate with an unmodified PostgreSQL instance via the [`pg_hint_plan`](https://github.com/ossc-db/pg_hint_plan) extension:

```sql
-- Install pg_hint_plan
CREATE EXTENSION pg_hint_plan;
```

The integration pathway (architectural design, not yet a deployed runtime component):

1. At query planning time, serialize candidate sub-plan descriptors into the 10-dimensional feature vector
2. Evaluate the trained CEDA-MLP model (< 0.0011 ms per sub-plan)
3. Supply resulting cardinality predictions to PostgreSQL via `pg_hint_plan` row-count hints

```sql
-- Example: injecting CEDA-MLP's estimate via pg_hint_plan
/*+ Rows(lineitem orders #42000) */
SELECT ...
FROM lineitem, orders
WHERE l_orderkey = o_orderkey
  AND l_shipdate BETWEEN '1994-01-01' AND '1994-12-31'
  AND o_orderpriority = '1-URGENT';
```

> This same pathway extends naturally to distributed engines (Citus, Greenplum) where per-shard cardinality estimates can be supplied to each worker.

---

## ⚠️ Limitations & Future Work

### Current Limitations

| Limitation | Description |
|---|---|
| **Pairwise correlations only** | Cannot capture dependencies emerging across 3+ attributes simultaneously |
| **No online learning** | Model must be retrained when workload or data distribution shifts significantly |
| **Per-schema training** | Trained weights are not portable across schemas without re-fitting |
| **TPC-H evaluation only** | Not yet validated on real-world production schemas or larger scale factors |

### Roadmap

- [ ] **Higher-order correlation encoding** — extend to attribute triplets or learned attention blocks for arbitrary-order correlations
- [ ] **Online learning** — lightweight replay buffer with periodic fine-tuning to track workload drift (cf. Ramadan et al. [12])
- [ ] **Schema-agnostic encoding** — type-based feature templates, learned column embeddings, or meta-learning across schemas
- [ ] **Distributed deployment** — augment feature vector with shard-level statistics; co-train with a cost-model adapter for network-aware optimization
- [ ] **Larger benchmarks** — validate at TPC-H SF = 100 and SF = 1000; evaluate on real-world analytical workloads

---

## 👥 Authors

| Name | Institution | Email |
|---|---|---|
| **Mohammad Sohail Saleem** | Dept. of Computer Science, Princess Sumaya University for Technology, Amman, Jordan | moh20258206@std.psut.edu.jo |
| **Ali Abu Foudeh** | Dept. of Computer Science, Princess Sumaya University for Technology, Amman, Jordan | ali20258096@std.psut.edu.jo |

*This work was completed as part of an undergraduate research project in partial fulfillment of the requirements for the Bachelor of Science degree in Computer Science.*

---

## 📄 Citation

If you use CEDA-MLP in your research, please cite:

```bibtex
@inproceedings{saleem2024ceda,
  title     = {CEDA-MLP: Correlation-Aware Cardinality Estimation Using Deep Neural Networks for Skewed Database Workloads},
  author    = {Saleem, Mohammad Sohail and Abu Foudeh, Ali},
  booktitle = {Proceedings of the IEEE},
  year      = {2024},
  institution = {Princess Sumaya University for Technology},
  address   = {Amman, Jordan}
}
```

---

## 📚 References

| # | Reference |
|---|---|
| [1] | G. Graefe, "The Cascades Framework for Query Optimization," *IEEE Data Eng. Bull.*, vol. 18, no. 3, pp. 19–29, 1995. |
| [2] | V. Leis et al., "How Good are Query Optimizers, Really?" *Proc. VLDB Endowment*, vol. 9, no. 3, pp. 204–215, 2015. |
| [3] | A. Kipf et al., "Learned Cardinalities: Estimating Correlated Joins with Deep Learning," in *Proc. CIDR*, 2019. |
| [4] | P. Li et al., "ALECE: An Attention-based Learned Cardinality Estimator for SPJ Queries on Dynamic Workloads," *Proc. VLDB Endowment*, vol. 17, no. 2, 2023. |
| [5] | B. Hilprecht et al., "DeepDB: Learn from Data, not from Queries!" *Proc. VLDB Endowment*, vol. 13, no. 7, pp. 992–1005, 2020. |
| [8] | R. Marcus et al., "Bao: Making Learned Query Optimization Practical," in *Proc. ACM SIGMOD*, 2021, pp. 1275–1288. |
| [9] | R. Marcus et al., "Neo: A Learned Query Optimizer," *Proc. VLDB Endowment*, vol. 12, no. 11, pp. 1705–1718, 2019. |
| [16] | Z. Yang et al., "NeuroCard: One Cardinality Estimator for All Tables," *Proc. VLDB Endowment*, vol. 14, no. 1, pp. 61–73, 2020. |
| [17] | Z. Yang et al., "Deep Unsupervised Cardinality Estimation," *Proc. VLDB Endowment*, vol. 13, no. 3, 2019. (Naru) |

---

<div align="center">

**Princess Sumaya University for Technology — Department of Computer Science**

*Amman, Jordan*

</div>
