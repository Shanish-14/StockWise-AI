
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


# ==========================================
# 1. PATHS AND SETTINGS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "data/raw/supplier_delay/supplier_orders_v2.csv"

MODEL_PATH = (
    ROOT / "models/supplier_delay/supplier_delay_v2_candidate.joblib"
)

REPORT_DIR = ROOT / "reports/supplier_delay"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLD = 0.35


# ==========================================
# 2. LOAD DATA AND MODEL
# ==========================================

print("\nSUPPLIER DELAY V2 - FINAL TEST")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values("order_date").reset_index(drop=True)

model = joblib.load(MODEL_PATH)

print("Dataset loaded:", df.shape)
print("Model loaded successfully.")


# ==========================================
# 3. SELECT FEATURES
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


# ==========================================
# 4. RECREATE CHRONOLOGICAL TEST SPLIT
# ==========================================

total = len(df)

validation_end = int(total * 0.85)

X_test = X.iloc[validation_end:]
y_test = y.iloc[validation_end:]

test_orders = df.iloc[validation_end:].copy()

print("\nFINAL TEST DATA")
print("-" * 60)

print("Testing records:", len(X_test))
print("Start date:", test_orders["order_date"].min())
print("End date:", test_orders["order_date"].max())

print("\nActual target distribution:")
print(y_test.value_counts())


# ==========================================
# 5. GENERATE PREDICTIONS
# ==========================================

probabilities = model.predict_proba(X_test)[:, 1]

predictions = (probabilities >= THRESHOLD).astype(int)


# ==========================================
# 6. EVALUATE MODEL
# ==========================================

accuracy = accuracy_score(y_test, predictions)

precision = precision_score(
    y_test, predictions, zero_division=0
)

recall = recall_score(
    y_test, predictions, zero_division=0
)

f1 = f1_score(
    y_test, predictions, zero_division=0
)

roc_auc = roc_auc_score(y_test, probabilities)

pr_auc = average_precision_score(y_test, probabilities)

tn, fp, fn, tp = confusion_matrix(
    y_test, predictions, labels=[0, 1]
).ravel()


# ==========================================
# 7. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 60)
print("FINAL TEST RESULTS")
print("=" * 60)

print("Selected threshold:", THRESHOLD)
print("Accuracy:", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1 Score:", round(f1, 4))
print("ROC AUC:", round(roc_auc, 4))
print("PR AUC:", round(pr_auc, 4))

print("\nCONFUSION MATRIX")
print("-" * 60)

print("True Positives:", tp)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Negatives:", tn)

print("\nCLASSIFICATION REPORT")
print("-" * 60)

print(
    classification_report(
        y_test,
        predictions,
        target_names=["On Time", "Delayed"],
        zero_division=0
    )
)


# ==========================================
# 8. SAVE FINAL TEST PREDICTIONS
# ==========================================

test_orders["delay_probability"] = probabilities
test_orders["predicted_delay"] = predictions
test_orders["prediction_threshold"] = THRESHOLD

prediction_path = (
    REPORT_DIR / "supplier_delay_v2_final_predictions.csv"
)

test_orders.to_csv(prediction_path, index=False)


# ==========================================
# 9. SAVE METRICS
# ==========================================

metrics = pd.DataFrame([{
    "threshold": THRESHOLD,
    "accuracy": accuracy,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "roc_auc": roc_auc,
    "pr_auc": pr_auc,
    "true_positives": tp,
    "false_positives": fp,
    "false_negatives": fn,
    "true_negatives": tn
}])

metrics_path = REPORT_DIR / "supplier_delay_v2_final_metrics.csv"

metrics.to_csv(metrics_path, index=False)


# ==========================================
# 10. COMPLETION
# ==========================================

print("\n" + "=" * 60)
print("FINAL EVALUATION COMPLETED")
print("=" * 60)

print("Predictions saved:", prediction_path)
print("Metrics saved:", metrics_path)

print("\nThe final test data was evaluated only once.")
