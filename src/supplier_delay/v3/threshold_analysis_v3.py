
import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# --------------------------------------------------
# 1. PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    ROOT / "reports/supplier_delay/v3/"
    "validation_predictions_v3.csv"
)

OUTPUT_PATH = (
    ROOT / "reports/supplier_delay/v3/"
    "threshold_analysis_v3.csv"
)

# --------------------------------------------------
# 2. LOAD VALIDATION PREDICTIONS
# --------------------------------------------------

print("\nSTOCKWISE AI - V3 THRESHOLD ANALYSIS")
print("=" * 65)

df = pd.read_csv(INPUT_PATH)

y_true = df["is_delayed"].astype(int)
y_prob = df["predicted_probability"].astype(float)

print("\nValidation records:", len(df))
print("Actual delay rate:", round(y_true.mean(), 4))

# --------------------------------------------------
# 3. TEST DIFFERENT THRESHOLDS
# --------------------------------------------------

thresholds = np.arange(0.10, 0.91, 0.05)

results = []

for threshold in thresholds:

    y_pred = (y_prob >= threshold).astype(int)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(
        y_true, y_pred, zero_division=0
    )
    recall = recall_score(
        y_true, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_true, y_pred, zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1]
    ).ravel()

    results.append({
        "threshold": round(float(threshold), 2),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "predicted_delayed": int(y_pred.sum()),
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp
    })

results_df = pd.DataFrame(results)

# --------------------------------------------------
# 4. BEST F1 THRESHOLD
# --------------------------------------------------

best_index = results_df["f1_score"].idxmax()
best_result = results_df.loc[best_index]

print("\nTHRESHOLD COMPARISON")
print("-" * 65)

print(
    results_df[
        [
            "threshold",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "predicted_delayed"
        ]
    ].round(4).to_string(index=False)
)

print("\nBEST F1 THRESHOLD")
print("-" * 65)

print("Threshold:", best_result["threshold"])
print("Accuracy:", round(best_result["accuracy"], 4))
print("Precision:", round(best_result["precision"], 4))
print("Recall:", round(best_result["recall"], 4))
print("F1 Score:", round(best_result["f1_score"], 4))

print("\nCONFUSION MATRIX AT BEST F1 THRESHOLD")
print("-" * 65)
print("TN:", int(best_result["TN"]))
print("FP:", int(best_result["FP"]))
print("FN:", int(best_result["FN"]))
print("TP:", int(best_result["TP"]))

# --------------------------------------------------
# 5. BASELINE COMPARISON
# --------------------------------------------------

baseline_on_time = np.zeros(len(y_true), dtype=int)
baseline_delayed = np.ones(len(y_true), dtype=int)

print("\nBASELINE COMPARISON")
print("-" * 65)

print(
    "Always On Time Accuracy:",
    round(accuracy_score(y_true, baseline_on_time), 4)
)

print(
    "Always Delayed Accuracy:",
    round(accuracy_score(y_true, baseline_delayed), 4)
)

print(
    "Always Delayed F1:",
    round(f1_score(y_true, baseline_delayed), 4)
)

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

results_df.to_csv(OUTPUT_PATH, index=False)

print("\nSaved:", OUTPUT_PATH)
print("\nThreshold analysis completed.")
print("=" * 65)
