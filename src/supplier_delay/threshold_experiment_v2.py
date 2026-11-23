
import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==========================================
# 1. PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "data/raw/supplier_delay/supplier_orders_v2.csv"

MODEL_PATH = (
    ROOT / "models/supplier_delay/supplier_delay_v2_candidate.joblib"
)


# ==========================================
# 2. LOAD DATA AND MODEL
# ==========================================

df = pd.read_csv(DATA_PATH)

df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values("order_date").reset_index(drop=True)

model = joblib.load(MODEL_PATH)

print("\nSUPPLIER DELAY V2 - THRESHOLD EXPERIMENT")
print("=" * 55)


# ==========================================
# 3. RECREATE VALIDATION DATA
# ==========================================

categorical_features = [
    "supplier_id",
    "product_category"
]

numerical_features = [
    "order_quantity",
    "distance_km",
    "supplier_reliability",
    "capacity_utilization",
    "promised_delivery_days",
    "historical_delay_rate",
    "order_day_of_week",
    "order_month"
]

features = categorical_features + numerical_features

X = df[features]
y = df["is_delayed"]

train_end = int(len(df) * 0.70)
validation_end = int(len(df) * 0.85)

X_val = X.iloc[train_end:validation_end]
y_val = y.iloc[train_end:validation_end]


# ==========================================
# 4. GET PREDICTION PROBABILITIES
# ==========================================

probabilities = model.predict_proba(X_val)[:, 1]


# ==========================================
# 5. TEST DIFFERENT THRESHOLDS
# ==========================================

thresholds = np.arange(0.20, 0.81, 0.05)

results = []

print("\nTHRESHOLD COMPARISON")
print("=" * 85)

for threshold in thresholds:

    predictions = (probabilities >= threshold).astype(int)

    accuracy = accuracy_score(y_val, predictions)

    precision = precision_score(
        y_val, predictions, zero_division=0
    )

    recall = recall_score(
        y_val, predictions, zero_division=0
    )

    f1 = f1_score(
        y_val, predictions, zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_val, predictions, labels=[0, 1]
    ).ravel()

    results.append({
        "Threshold": round(threshold, 2),
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "True Positives": tp,
        "False Positives": fp,
        "False Negatives": fn,
        "True Negatives": tn
    })


results_df = pd.DataFrame(results)

print(results_df.round(4).to_string(index=False))


# ==========================================
# 6. BEST THRESHOLD BY F1
# ==========================================

best_row = results_df.loc[
    results_df["F1 Score"].idxmax()
]

print("\n" + "=" * 55)
print("BEST THRESHOLD BY F1 SCORE")
print("=" * 55)

for column, value in best_row.items():
    print(f"{column}: {value:.4f}")


# ==========================================
# 7. SAVE VALIDATION RESULTS
# ==========================================

REPORT_DIR = ROOT / "reports/supplier_delay"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

report_path = REPORT_DIR / "threshold_results_v2.csv"

results_df.to_csv(report_path, index=False)

print("\nResults saved to:")
print(report_path)

print("\nFinal test data was NOT used.")
