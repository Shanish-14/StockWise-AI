
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

# --------------------------------------------------
# 1. PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    ROOT / "data/raw/supplier_delay/v3/"
    "grocery_supplier_orders_v3.csv"
)

MODEL_PATH = (
    ROOT / "models/supplier_delay/v3/"
    "supplier_delay_v3_candidate.joblib"
)

REPORT_DIR = ROOT / "reports/supplier_delay/v3"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD DATA AND MODEL
# --------------------------------------------------

print("\nSTOCKWISE AI - V3 FINAL TEST EVALUATION")
print("=" * 65)

df = pd.read_csv(DATA_PATH)
df["order_date"] = pd.to_datetime(df["order_date"])

model = joblib.load(MODEL_PATH)

print("\nDataset loaded:", df.shape)
print("Model loaded:", type(model).__name__)

# --------------------------------------------------
# 3. RECREATE THE ORIGINAL DATE-BASED TEST SPLIT
# --------------------------------------------------

test_start = pd.Timestamp("2025-09-13")
test_end = pd.Timestamp("2025-12-31")

test_df = df[
    (df["order_date"] >= test_start) &
    (df["order_date"] <= test_end)
].copy()

test_df = test_df.sort_values("order_date").reset_index(drop=True)

print("\nTEST DATASET")
print("-" * 65)
print("Rows:", len(test_df))
print("Start date:", test_df["order_date"].min().date())
print("End date:", test_df["order_date"].max().date())

# Confirm this is the same test partition used during training.
if len(test_df) != 7456:
    raise ValueError(
        f"Expected 7456 final test rows, found {len(test_df)}. "
        "Stop here and verify the original training split."
    )

# --------------------------------------------------
# 4. SELECT FEATURES
# --------------------------------------------------

numeric_features = [
    "order_quantity",
    "distance_km",
    "supplier_reliability",
    "capacity_utilization",
    "promised_delivery_days",
    "order_day_of_week",
    "order_month",
    "is_festival_period",
    "transport_risk"
]

categorical_features = [
    "supplier_id",
    "store_id",
    "product_id",
    "product_category"
]

features = numeric_features + categorical_features
target = "is_delayed"

X_test = test_df[features]
y_test = test_df[target].astype(int)

print("\nActual delay rate:", round(y_test.mean(), 4))

# --------------------------------------------------
# 5. PREDICTIONS
# --------------------------------------------------

THRESHOLD = 0.50

probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= THRESHOLD).astype(int)

# --------------------------------------------------
# 6. EVALUATION METRICS
# --------------------------------------------------

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, zero_division=0)
recall = recall_score(y_test, predictions, zero_division=0)
f1 = f1_score(y_test, predictions, zero_division=0)
roc_auc = roc_auc_score(y_test, probabilities)
pr_auc = average_precision_score(y_test, probabilities)

cm = confusion_matrix(y_test, predictions, labels=[0, 1])
tn, fp, fn, tp = cm.ravel()

print("\nFINAL TEST RESULTS")
print("=" * 65)
print(f"Threshold:  {THRESHOLD:.2f}")
print(f"Accuracy:   {accuracy:.4f}")
print(f"Precision:  {precision:.4f}")
print(f"Recall:     {recall:.4f}")
print(f"F1 Score:   {f1:.4f}")
print(f"ROC AUC:    {roc_auc:.4f}")
print(f"PR AUC:     {pr_auc:.4f}")

print("\nCONFUSION MATRIX")
print("-" * 65)
print("TN:", tn)
print("FP:", fp)
print("FN:", fn)
print("TP:", tp)

print("\nCLASSIFICATION REPORT")
print("-" * 65)
print(
    classification_report(
        y_test,
        predictions,
        target_names=["On Time", "Delayed"],
        zero_division=0
    )
)

# --------------------------------------------------
# 7. SAVE METRICS
# --------------------------------------------------

metrics = pd.DataFrame([{
    "model": "Random Forest",
    "threshold": THRESHOLD,
    "test_rows": len(test_df),
    "actual_delay_rate": y_test.mean(),
    "accuracy": accuracy,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "roc_auc": roc_auc,
    "pr_auc": pr_auc,
    "TN": tn,
    "FP": fp,
    "FN": fn,
    "TP": tp
}])

metrics_path = REPORT_DIR / "final_test_metrics_v3.csv"
metrics.to_csv(metrics_path, index=False)

# --------------------------------------------------
# 8. SAVE RECORD-LEVEL PREDICTIONS
# --------------------------------------------------

predictions_df = pd.DataFrame({
    "order_id": test_df["order_id"],
    "order_date": test_df["order_date"],
    "actual_is_delayed": y_test,
    "predicted_delay_probability": probabilities,
    "predicted_is_delayed": predictions,
    "prediction_correct": (y_test.to_numpy() == predictions)
})

predictions_path = REPORT_DIR / "final_test_predictions_v3.csv"
predictions_df.to_csv(predictions_path, index=False)

# --------------------------------------------------
# 9. COMPLETION
# --------------------------------------------------

print("\nSAVED FILES")
print("-" * 65)
print(metrics_path)
print(predictions_path)

print("\nFinal test evaluation completed.")
print("The model was not trained or tuned on final test data.")
print("=" * 65)
