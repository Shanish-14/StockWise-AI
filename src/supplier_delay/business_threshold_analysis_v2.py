

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
# PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT / "data/raw/supplier_delay/supplier_orders_v2.csv"
)

MODEL_PATH = (
    ROOT / "models/supplier_delay/supplier_delay_v2_candidate.joblib"
)

OUTPUT_PATH = (
    ROOT / "reports/supplier_delay/business_threshold_results_v2.csv"
)

# ==========================================
# SETTINGS
# ==========================================

MINIMUM_RECALL = 0.80

FEATURE_COLUMNS = [
    "supplier_id",
    "product_category",
    "order_quantity",
    "distance_km",
    "supplier_reliability",
    "capacity_utilization",
    "promised_delivery_days",
    "historical_delay_rate",
    "order_day_of_week",
    "order_month"
]

# ==========================================
# LOAD DATA AND MODEL
# ==========================================

print("\nBUSINESS THRESHOLD ANALYSIS - V2")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)

print("Dataset loaded:", df.shape)
print("Model loaded successfully.")

# ==========================================
# CHRONOLOGICAL VALIDATION SPLIT
# ==========================================

df = df.sort_values("order_date").reset_index(drop=True)

n = len(df)

train_end = int(n * 0.70)
validation_end = int(n * 0.85)

validation_df = df.iloc[train_end:validation_end].copy()

X_validation = validation_df[FEATURE_COLUMNS]
y_validation = validation_df["is_delayed"]

print("\nValidation records:", len(validation_df))

# ==========================================
# PREDICT VALIDATION PROBABILITIES
# ==========================================

probabilities = model.predict_proba(X_validation)[:, 1]

# ==========================================
# TEST THRESHOLDS
# ==========================================

results = []

for threshold in np.arange(0.20, 0.801, 0.01):

    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_validation,
        predictions,
        labels=[0, 1]
    ).ravel()

    actual_on_time = tn + fp

    false_positive_rate = (
        fp / actual_on_time
        if actual_on_time > 0
        else 0
    )

    results.append({
        "Threshold": round(threshold, 2),
        "Accuracy": accuracy_score(
            y_validation, predictions
        ),
        "Precision": precision_score(
            y_validation, predictions, zero_division=0
        ),
        "Recall": recall_score(
            y_validation, predictions, zero_division=0
        ),
        "F1 Score": f1_score(
            y_validation, predictions, zero_division=0
        ),
        "True Positives": tp,
        "False Positives": fp,
        "False Negatives": fn,
        "True Negatives": tn,
        "False Alarm Rate": false_positive_rate
    })

results_df = pd.DataFrame(results)

# ==========================================
# SELECT BUSINESS THRESHOLD
# ==========================================

eligible = results_df[
    results_df["Recall"] >= MINIMUM_RECALL
]

if eligible.empty:

    selected_threshold = None

    print("\nNo threshold meets the minimum recall requirement.")

else:

    # Select the highest threshold that maintains
    # at least 80% recall to reduce false alarms.

    selected_row = eligible.sort_values(
        "Threshold",
        ascending=False
    ).iloc[0]

    selected_threshold = selected_row["Threshold"]

# ==========================================
# DISPLAY THRESHOLD COMPARISON
# ==========================================

print("\nTHRESHOLD COMPARISON")
print("=" * 100)

comparison_thresholds = [0.35, 0.40, 0.45, 0.50]

comparison = results_df[
    results_df["Threshold"].isin(comparison_thresholds)
]

print(comparison.round(4).to_string(index=False))

# ==========================================
# DISPLAY SELECTED BUSINESS THRESHOLD
# ==========================================

print("\nBUSINESS THRESHOLD ANALYSIS")
print("=" * 60)

if selected_threshold is not None:

    selected = results_df[
        results_df["Threshold"] == selected_threshold
    ].iloc[0]

    print(f"Minimum required recall: {MINIMUM_RECALL:.0%}")
    print(f"Selected threshold: {selected_threshold:.2f}")

    print(f"Accuracy: {selected['Accuracy']:.4f}")
    print(f"Precision: {selected['Precision']:.4f}")
    print(f"Recall: {selected['Recall']:.4f}")
    print(f"F1 Score: {selected['F1 Score']:.4f}")

    print(f"True Positives: {int(selected['True Positives'])}")
    print(f"False Positives: {int(selected['False Positives'])}")
    print(f"False Negatives: {int(selected['False Negatives'])}")
    print(f"True Negatives: {int(selected['True Negatives'])}")

    print(
        f"False Alarm Rate: "
        f"{selected['False Alarm Rate']:.2%}"
    )

# ==========================================
# SAVE RESULTS
# ==========================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

results_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nAll threshold results saved to:")
print(OUTPUT_PATH)

print("\nAnalysis completed successfully!")
