


import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report


# ==========================================
# 1. PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "data/raw/supplier_delay/supplier_orders_v2.csv"

MODEL_PATH = (
    ROOT / "models/supplier_delay/supplier_delay_v2_candidate.joblib"
)

REPORT_DIR = ROOT / "reports/supplier_delay"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD DATA AND MODEL
# ==========================================

print("\nSUPPLIER DELAY V2 - ERROR ANALYSIS")
print("=" * 65)

df = pd.read_csv(DATA_PATH)

df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values("order_date").reset_index(drop=True)

model = joblib.load(MODEL_PATH)

print("Dataset loaded:", df.shape)
print("Model loaded successfully.")


# ==========================================
# 3. SELECT VALIDATION DATA
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

validation_df = df.iloc[
    train_end:validation_end
].copy()

print("\nValidation records:", len(validation_df))


# ==========================================
# 4. GENERATE PREDICTIONS
# ==========================================

probabilities = model.predict_proba(X_val)[:, 1]

THRESHOLD = 0.35

predictions = (probabilities >= THRESHOLD).astype(int)

validation_df["predicted_probability"] = probabilities
validation_df["predicted_delay"] = predictions


# ==========================================
# 5. CLASSIFY PREDICTION RESULTS
# ==========================================

validation_df["result"] = np.select(
    [
        (validation_df["is_delayed"] == 1) &
        (validation_df["predicted_delay"] == 1),

        (validation_df["is_delayed"] == 0) &
        (validation_df["predicted_delay"] == 1),

        (validation_df["is_delayed"] == 1) &
        (validation_df["predicted_delay"] == 0),

        (validation_df["is_delayed"] == 0) &
        (validation_df["predicted_delay"] == 0)
    ],
    [
        "True Positive",
        "False Positive",
        "False Negative",
        "True Negative"
    ],
    default="Unknown"
)


# ==========================================
# 6. OVERALL ERROR SUMMARY
# ==========================================

print("\n1. OVERALL ERROR SUMMARY")
print("-" * 65)

print(validation_df["result"].value_counts())

tn, fp, fn, tp = confusion_matrix(
    y_val,
    predictions,
    labels=[0, 1]
).ravel()

print("\nTrue Positives:", tp)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Negatives:", tn)

print("\nClassification Report:")

print(
    classification_report(
        y_val,
        predictions,
        labels=[0, 1],
        target_names=["On Time", "Delayed"],
        zero_division=0
    )
)


# ==========================================
# 7. SUPPLIER-LEVEL ERROR ANALYSIS
# ==========================================

print("\n2. SUPPLIER-LEVEL ERROR ANALYSIS")
print("-" * 65)

supplier_analysis = validation_df.groupby(
    "supplier_id"
).agg(
    total_orders=("order_id", "count"),
    actual_delays=("is_delayed", "sum"),
    predicted_delays=("predicted_delay", "sum"),
    false_alarms=(
        "result",
        lambda x: (x == "False Positive").sum()
    ),
    missed_delays=(
        "result",
        lambda x: (x == "False Negative").sum()
    )
)

supplier_analysis["actual_delay_rate"] = (
    supplier_analysis["actual_delays"] /
    supplier_analysis["total_orders"]
)

supplier_analysis["false_alarm_rate"] = (
    supplier_analysis["false_alarms"] /
    supplier_analysis["total_orders"]
)

supplier_analysis = supplier_analysis.sort_values(
    "false_alarms",
    ascending=False
)

print(supplier_analysis.round(3).to_string())

supplier_analysis.to_csv(
    REPORT_DIR / "supplier_error_analysis_v2.csv"
)


# ==========================================
# 8. PRODUCT CATEGORY ERROR ANALYSIS
# ==========================================

print("\n3. PRODUCT CATEGORY ERROR ANALYSIS")
print("-" * 65)

category_analysis = validation_df.groupby(
    "product_category"
).agg(
    total_orders=("order_id", "count"),
    actual_delays=("is_delayed", "sum"),
    predicted_delays=("predicted_delay", "sum"),
    false_alarms=(
        "result",
        lambda x: (x == "False Positive").sum()
    ),
    missed_delays=(
        "result",
        lambda x: (x == "False Negative").sum()
    )
)

category_analysis["actual_delay_rate"] = (
    category_analysis["actual_delays"] /
    category_analysis["total_orders"]
)

print(category_analysis.round(3).to_string())

category_analysis.to_csv(
    REPORT_DIR / "category_error_analysis_v2.csv"
)


# ==========================================
# 9. HISTORICAL DELAY RATE ANALYSIS
# ==========================================

print("\n4. HISTORICAL DELAY RATE ANALYSIS")
print("-" * 65)

validation_df["history_group"] = pd.cut(
    validation_df["historical_delay_rate"],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    labels=[
        "0-20%",
        "20-40%",
        "40-60%",
        "60-80%",
        "80-100%"
    ],
    include_lowest=True
)

history_analysis = validation_df.groupby(
    "history_group",
    observed=False
).agg(
    total_orders=("order_id", "count"),
    actual_delays=("is_delayed", "sum"),
    predicted_delays=("predicted_delay", "sum"),
    false_alarms=(
        "result",
        lambda x: (x == "False Positive").sum()
    ),
    missed_delays=(
        "result",
        lambda x: (x == "False Negative").sum()
    )
)

history_analysis["actual_delay_rate"] = (
    history_analysis["actual_delays"] /
    history_analysis["total_orders"].replace(0, np.nan)
)

print(history_analysis.round(3).to_string())

history_analysis.to_csv(
    REPORT_DIR / "historical_error_analysis_v2.csv"
)


# ==========================================
# 10. FALSE ALARM EXAMPLES
# ==========================================

print("\n5. FALSE ALARM EXAMPLES")
print("-" * 65)

false_alarms = validation_df[
    validation_df["result"] == "False Positive"
]

print("Total false alarms:", len(false_alarms))

print(
    false_alarms[
        [
            "order_id",
            "supplier_id",
            "product_category",
            "supplier_reliability",
            "distance_km",
            "historical_delay_rate",
            "predicted_probability"
        ]
    ].head(10).round(3).to_string(index=False)
)


# ==========================================
# 11. MISSED DELAY EXAMPLES
# ==========================================

print("\n6. MISSED DELAY EXAMPLES")
print("-" * 65)

missed_delays = validation_df[
    validation_df["result"] == "False Negative"
]

print("Total missed delays:", len(missed_delays))

print(
    missed_delays[
        [
            "order_id",
            "supplier_id",
            "product_category",
            "supplier_reliability",
            "distance_km",
            "historical_delay_rate",
            "predicted_probability"
        ]
    ].head(10).round(3).to_string(index=False)
)


# ==========================================
# 12. SAVE COMPLETE ANALYSIS
# ==========================================

output_path = REPORT_DIR / "error_analysis_v2.csv"

validation_df.to_csv(
    output_path,
    index=False
)


# ==========================================
# 13. COMPLETION
# ==========================================

print("\n" + "=" * 65)
print("ERROR ANALYSIS COMPLETED")
print("=" * 65)

print("\nSaved reports:")

print("1.", output_path)

print(
    "2.",
    REPORT_DIR / "supplier_error_analysis_v2.csv"
)

print(
    "3.",
    REPORT_DIR / "category_error_analysis_v2.csv"
)

print(
    "4.",
    REPORT_DIR / "historical_error_analysis_v2.csv"
)

print("\nFinal test data was NOT used.")
