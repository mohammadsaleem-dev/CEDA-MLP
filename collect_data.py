import psycopg2
import pandas as pd
import re
import numpy as np
import time

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="tpch",
    user="postgres",
    password="Moody5ds*"
)

cur = conn.cursor()

# Prevent infinite query execution (30 sec timeout)
cur.execute("SET statement_timeout = 30000;")

queries = []

# Reduced workload for testing
# Large research workload
prices = list(range(1000, 600000, 2500))

statuses = ['F', 'O', 'P']

dates = [
    '1992-01-01',
    '1993-01-01',
    '1994-01-01',
    '1995-01-01',
    '1996-01-01',
    '1997-01-01'
]

# Generate workload
for p in prices:

    # Simple query
    query1 = f"""
    SELECT *
    FROM orders
    WHERE o_totalprice > {p};
    """

    queries.append(query1)

    for s in statuses:

        # Correlated orders query
        query2 = f"""
        SELECT *
        FROM orders
        WHERE o_orderstatus = '{s}'
        AND o_totalprice > {p};
        """

        queries.append(query2)

        # Join query
        query3 = f"""
        SELECT *
        FROM customer c
        JOIN orders o
        ON c.c_custkey = o.o_custkey
        WHERE o.o_orderstatus = '{s}'
        AND o.o_totalprice > {p};
        """

        queries.append(query3)

        for d in dates:

            # Correlated lineitem query
            query4 = f"""
            SELECT *
            FROM lineitem
            WHERE l_shipdate < '{d}'
            AND l_commitdate < '{d}'
            AND l_discount > 0.04;
            """

            queries.append(query4)

            # Multi-join skewed query
            query5 = f"""
            SELECT *
            FROM customer c
            JOIN orders o
            ON c.c_custkey = o.o_custkey
            JOIN lineitem l
            ON o.o_orderkey = l.l_orderkey
            WHERE o.o_totalprice > {p}
            AND l.l_discount > 0.04
            AND l.l_shipdate < '{d}';
            """

            queries.append(query5)

results = []

# Real correlations
lineitem_correlation = 0.9984
orders_correlation = 0.0258

print(f"\nTotal Queries: {len(queries)}\n")
overall_start = time.time()

for i, q in enumerate(queries):

    query_start = time.time()

    print(f"\nRunning Query {i+1}/{len(queries)}")

    try:

        explain_query = "EXPLAIN ANALYZE " + q

        cur.execute(explain_query)

        plan = cur.fetchall()

        plan_text = "\n".join(row[0] for row in plan)

        # Estimated rows
        est_match = re.search(r'rows=(\d+)', plan_text)
        estimated_rows = int(est_match.group(1)) if est_match else 0

        # Actual rows
        actual_match = re.search(r'actual time=.* rows=(\d+)', plan_text)
        actual_rows = int(actual_match.group(1)) if actual_match else 0

        # Execution time
        exec_match = re.search(r'Execution Time: ([0-9.]+)', plan_text)
        execution_time = float(exec_match.group(1)) if exec_match else 0

        # Costs
        cost_match = re.search(r'cost=([0-9.]+)\.\.([0-9.]+)', plan_text)

        startup_cost = 0
        total_cost = 0

        if cost_match:
            startup_cost = float(cost_match.group(1))
            total_cost = float(cost_match.group(2))

        # Q-error
        q_error = max(
            estimated_rows / max(actual_rows, 1),
            actual_rows / max(estimated_rows, 1)
        )

        # Join count
        join_count = q.lower().count("join")

        # Selectivity
        total_rows_orders = 1500000
        total_rows_lineitem = 6001215

        if "lineitem" in q.lower():
            total_rows = total_rows_lineitem
        else:
            total_rows = total_rows_orders

        selectivity = actual_rows / max(total_rows, 1)

        # Correlation feature
        correlation_feature = (
            lineitem_correlation
            if "lineitem" in q.lower()
            else orders_correlation
        )
        query_runtime = round(time.time() - query_start, 2)

        print(f"Finished in {query_runtime} sec | Q-error = {round(q_error, 2)}")

        results.append({

            "query": q.strip(),

            "estimated_rows": estimated_rows,

            "actual_rows": actual_rows,

            "startup_cost": startup_cost,

            "total_cost": total_cost,

            "execution_time_ms": execution_time,

            "q_error": q_error,

            "correlation_feature": correlation_feature,

            "join_count": join_count,

            "selectivity": selectivity
        })

    except Exception as e:

        print(f"Skipped query بسبب timeout/error: {e}")

        conn.rollback()

df = pd.DataFrame(results)

print("\nDataset Preview:")
print(df.head())

df.to_csv("cardinality_dataset.csv", index=False)

cur.close()
conn.close()

overall_runtime = round(time.time() - overall_start, 2)

print("\nDataset saved to cardinality_dataset.csv")

print(f"\nTotal Runtime: {overall_runtime} sec")