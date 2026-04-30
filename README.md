# Machine Learning-Based SQL Query Performance Prediction for Small Databases

## 📌 Overview

This project presents a lightweight machine learning framework for predicting SQL query execution time in small database environments. The system extracts structural features from SQL queries and uses multiple machine learning models to estimate query runtime efficiently.

The goal is to provide accurate performance prediction without requiring large datasets or complex database profiling tools.

---

## 🚀 Features

* Predicts SQL query execution time using machine learning
* Works effectively with **small datasets**
* Supports multiple models:

  * Linear Regression
  * Decision Tree
  * Random Forest
  * Gradient Boosting
* Includes **model comparison and evaluation**
* Provides **feature importance analysis**
* Implements a **hybrid model (SQP-HybridBoost)** based on query complexity
* Generates visualizations:

  * Model comparison
  * Prediction accuracy
  * Feature importance

---

## 🧠 Key Contributions

* Demonstrates that accurate prediction is possible with **limited data**
* Shows that SQL query performance is **non-linear**
* Identifies **JOIN operations as the most influential factor**
* Proposes a hybrid model and analyzes its performance under real conditions

---

## 🛠️ Technologies Used

* Python 3
* MySQL
* Pandas
* NumPy
* Scikit-learn
* Matplotlib

---

## 🗄️ Dataset

The dataset is generated dynamically by executing SQL queries on a MySQL database.

Each record includes:

* Number of JOIN operations
* Presence of WHERE clause
* GROUP BY usage
* ORDER BY usage
* Query length
* Execution time (ms)

---

## ⚙️ How It Works

1. Generate SQL queries with varying complexity
2. Execute queries on MySQL database
3. Measure execution time
4. Extract query features
5. Train machine learning models
6. Evaluate performance using:

   * MAE (Mean Absolute Error)
   * RMSE (Root Mean Squared Error)
   * R² Score

---

## 📊 Results Summary

* Best model: **Tree-based models (Random Forest / Gradient Boosting)**
* Achieved high accuracy:

  * R² ≈ 0.95 – 0.97
* Hybrid model (SQP-HybridBoost):

  * Demonstrated that performance depends on data distribution
  * Highlighted the impact of dataset imbalance

---

## 📈 Output Files

The system generates:

* `dataset.csv` → collected data
* `model_results.csv` → evaluation results
* `results.png` → predicted vs actual
* `model_comparison.png` → model performance
* `feature_importance.png` → feature analysis

---

## ▶️ How to Run

1. Ensure MySQL is running
2. Update database credentials in `main.py`
3. Install dependencies:

   ```bash
   pip install pandas numpy scikit-learn matplotlib mysql-connector-python
   ```
4. Run the script:

   ```bash
   python main.py
   ```

---

## 📌 Project Structure

```
.
├── main.py
├── dataset.csv
├── model_results.csv
├── results.png
├── model_comparison.png
├── feature_importance.png
├── README.md
```

---

## 📖 Future Work

* Use larger and more diverse datasets
* Improve hybrid model with balanced data
* Integrate real-time query optimization systems

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Mohammad Sohail Saleem & Ali
Computer Science Students
