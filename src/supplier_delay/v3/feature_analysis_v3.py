
import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    confusion_matrix,
    classification_report
)


# ============================================================
# STOCKWISE AI - SUPPLIER DELAY V3
# FEATURE IMPORTANCE AND ERROR ANALYSIS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supplier_delay"
    / "v3"
    / "grocery_supplier_orders_v3.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "supplier_delay"
    / "v3"
    / "supplier_delay_v3_candidate.joblib"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "supplier_delay"
    / "v3"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD DATA AND MODEL
# ============================================================

print("\nSTOCKWISE AI - FEATURE ANALYSIS V3")
print("=" * 70)

print("\n1. LOADING DATA AND MODEL")
print("-" * 70)

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["order_date"]
)

df = df.sort_values(
    "order_date",
    kind="stable"
).reset_index(drop=True)

model = joblib.load(MODEL_PATH)

print("Dataset loaded:", df.shape)
print("Candidate model loaded successfully.")


# ============================================================
# 2. RECREATE VALIDATION SPLIT BY UNIQUE DATES
# ============================================================

print("\n2. RECREATING VALIDATION DATA")
print("-" * 70)

unique_dates = np.sort(
    df["order_date"].dropna().unique()
)

total_dates = len(unique_dates)

train_date_end = int(total_dates * 0.70)
validation_date_end = int(total_dates * 0.85)

validation_dates = unique_dates[
    train_date_end:validation_date_end
]

validation_mask = df["order_date"].isin(
    validation_dates
)

validation_df = df.loc[
    validation_mask
].copy()

print("Validation records:", len(validation_df))

print(
    "Validation period:",
    validation_df["order_date"].min(),
    "to",
    validation_df["order_date"].max()
)


# ============================================================
# 3. SELECT FEATURES
# ============================================================

print("\n3. SELECTING FEATURES")
print("-" * 70)

categorical_features = [
    "supplier_id",
    "store_id",
    "product_id",
    "product_category"
]

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

features = categorical_features + numeric_features

X_validation = validation_df[features].copy()

y_validation = validation_df["is_delayed"].copy()

print("Total features:", len(features))


# ============================================================
# 4. MODEL FEATURE IMPORTANCE
# ============================================================

print("\n4. RANDOM FOREST FEATURE IMPORTANCE")
print("-" * 70)

preprocessor = model.named_steps["preprocessor"]

classifier = model.named_steps["classifier"]

feature_names = preprocessor.get_feature_names_out()

importance_values = classifier.feature_importances_

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importance_values
})

importance_df = importance_df.sort_values(
    "Importance",
    ascending=False
).reset_index(drop=True)

importance_path = (
    REPORT_DIR
    / "feature_importance_v3.csv"
)

importance_df.to_csv(
    importance_path,
    index=False
)

print("\nTOP 20 ENCODED FEATURES")
print(
    importance_df.head(20).round(5).to_string(index=False)
)


# ============================================================
# 5. GROUP IMPORTANCE BY ORIGINAL FEATURE
# ============================================================

print("\n5. ORIGINAL FEATURE IMPORTANCE")
print("-" * 70)

grouped_importance = {}

for feature in features:

    matching_rows = importance_df[
        importance_df["Feature"].str.contains(
            feature,
            regex=False
        )
    ]

    grouped_importance[feature] = (
        matching_rows["Importance"].sum()
    )

grouped_df = pd.DataFrame({
    "Feature": list(grouped_importance.keys()),
    "Importance": list(grouped_importance.values())
})

grouped_df = grouped_df.sort_values(
    "Importance",
    ascending=False
).reset_index(drop=True)

grouped_path = (
    REPORT_DIR
    / "grouped_feature_importance_v3.csv"
)

grouped_df.to_csv(
    grouped_path,
    index=False
)

print(
    grouped_df.round(5).to_string(index=False)
)


# ============================================================
# 6. PERMUTATION IMPORTANCE
# ============================================================

print("\n6. PERMUTATION IMPORTANCE")
print("-" * 70)

print("Calculating permutation importance...")
print("This may take some time.")

permutation_result = permutation_importance(
    model,
    X_validation,
    y_validation,
    scoring="roc_auc",
    n_repeats=5,
    random_state=42,
    n_jobs=-1
)

permutation_df = pd.DataFrame({
    "Feature": features,
    "Importance_Mean": permutation_result.importances_mean,
    "Importance_Std": permutation_result.importances_std
})

permutation_df = permutation_df.sort_values(
    "Importance_Mean",
    ascending=False
).reset_index(drop=True)

permutation_path = (
    REPORT_DIR
    / "permutation_importance_v3.csv"
)

permutation_df.to_csv(
    permutation_path,
    index=False
)

print("\nPERMUTATION IMPORTANCE RESULTS")

print(
    permutation_df.round(5).to_string(index=False)
)


# ============================================================
# 7. VALIDATION PREDICTIONS
# ============================================================

print("\n7. VALIDATION PREDICTIONS")
print("-" * 70)

probabilities = model.predict_proba(
    X_validation
)[:, 1]

threshold = 0.50

predictions = (
    probabilities >= threshold
).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_validation,
    predictions,
    labels=[0, 1]
).ravel()

print("Threshold:", threshold)

print("True Positives:", tp)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Negatives:", tn)

print("\nCLASSIFICATION REPORT")

print(
    classification_report(
        y_validation,
        predictions,
        target_names=["On Time", "Delayed"],
        zero_division=0
    )
)


# ============================================================
# 8. ERROR ANALYSIS
# ============================================================

print("\n8. ERROR ANALYSIS")
print("-" * 70)

error_df = validation_df[
    [
        "order_id",
        "order_date",
        "supplier_id",
        "store_id",
        "product_id",
        "product_category",
        "order_quantity",
        "distance_km",
        "supplier_reliability",
        "capacity_utilization",
        "promised_delivery_days",
        "transport_risk",
        "is_delayed"
    ]
].copy()

error_df["predicted_probability"] = probabilities

error_df["predicted_class"] = predictions

error_df["prediction_result"] = np.select(
    [
        (error_df["is_delayed"] == 1)
        & (error_df["predicted_class"] == 1),

        (error_df["is_delayed"] == 0)
        & (error_df["predicted_class"] == 0),

        (error_df["is_delayed"] == 0)
        & (error_df["predicted_class"] == 1),

        (error_df["is_delayed"] == 1)
        & (error_df["predicted_class"] == 0)
    ],
    [
        "True Positive",
        "True Negative",
        "False Positive",
        "False Negative"
    ],
    default="Unknown"
)

error_path = (
    REPORT_DIR
    / "validation_error_analysis_v3.csv"
)

error_df.to_csv(
    error_path,
    index=False
)

print("\nERROR COUNTS")

print(
    error_df["prediction_result"].value_counts()
)


# ============================================================
# 9. ERROR ANALYSIS BY CATEGORY
# ============================================================

print("\n9. ERROR ANALYSIS BY PRODUCT CATEGORY")
print("-" * 70)

category_errors = error_df.groupby(
    "product_category"
).agg(
    Total_Orders=("order_id", "count"),
    Actual_Delays=("is_delayed", "sum"),
    Predicted_Delays=("predicted_class", "sum"),
    False_Positives=(
        "prediction_result",
        lambda x: (x == "False Positive").sum()
    ),
    False_Negatives=(
        "prediction_result",
        lambda x: (x == "False Negative").sum()
    )
).reset_index()

category_errors["Actual_Delay_Rate"] = (
    category_errors["Actual_Delays"]
    / category_errors["Total_Orders"]
)

category_errors["Predicted_Delay_Rate"] = (
    category_errors["Predicted_Delays"]
    / category_errors["Total_Orders"]
)

category_path = (
    REPORT_DIR
    / "category_error_analysis_v3.csv"
)

category_errors.to_csv(
    category_path,
    index=False
)

print(
    category_errors.round(4).to_string(index=False)
)


# ============================================================
# 10. ERROR ANALYSIS BY SUPPLIER
# ============================================================

print("\n10. ERROR ANALYSIS BY SUPPLIER")
print("-" * 70)

supplier_errors = error_df.groupby(
    "supplier_id"
).agg(
    Total_Orders=("order_id", "count"),
    Actual_Delays=("is_delayed", "sum"),
    Predicted_Delays=("predicted_class", "sum"),
    False_Positives=(
        "prediction_result",
        lambda x: (x == "False Positive").sum()
    ),
    False_Negatives=(
        "prediction_result",
        lambda x: (x == "False Negative").sum()
    )
).reset_index()

supplier_errors["Actual_Delay_Rate"] = (
    supplier_errors["Actual_Delays"]
    / supplier_errors["Total_Orders"]
)

supplier_errors["Predicted_Delay_Rate"] = (
    supplier_errors["Predicted_Delays"]
    / supplier_errors["Total_Orders"]
)

supplier_path = (
    REPORT_DIR
    / "supplier_error_analysis_v3.csv"
)

supplier_errors.to_csv(
    supplier_path,
    index=False
)

print(
    supplier_errors.round(4).to_string(index=False)
)


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n11. ANALYSIS SUMMARY")
print("=" * 70)

print("Feature analysis completed successfully.")

print("\nGenerated reports:")

print(importance_path)
print(grouped_path)
print(permutation_path)
print(error_path)
print(category_path)
print(supplier_path)

print("\nFinal test data was NOT used.")

print("\nSUPPLIER DELAY V3 FEATURE ANALYSIS COMPLETED!")
