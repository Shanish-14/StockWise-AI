

import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)


# ============================================================
# STOCKWISE AI - SUPPLIER DELAY PREDICTION V3
# MODEL TRAINING AND VALIDATION
# Synthetic grocery supply-chain simulation
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

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "supplier_delay"
    / "v3"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "supplier_delay"
    / "v3"
)

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("\nSTOCKWISE AI - SUPPLIER DELAY V3")
print("=" * 70)

print("\n1. LOADING DATASET")
print("-" * 70)

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["order_date"]
)

df = df.sort_values(
    "order_date",
    kind="stable"
).reset_index(drop=True)

print("Dataset shape:", df.shape)
print("Dataset loaded successfully.")


# ============================================================
# 2. SELECT FEATURES
# ============================================================

print("\n2. FEATURE SELECTION")
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

target = "is_delayed"

X = df[features].copy()
y = df[target].copy()

print("Total features:", len(features))
print("Categorical features:", len(categorical_features))
print("Numeric features:", len(numeric_features))
print("Target:", target)


# ============================================================
# 3. CHRONOLOGICAL SPLIT BY UNIQUE DATES
# ============================================================

print("\n3. CHRONOLOGICAL DATA SPLIT BY UNIQUE DATES")
print("-" * 70)

# Get all unique dates in chronological order.
unique_dates = np.sort(
    df["order_date"].dropna().unique()
)

total_dates = len(unique_dates)

# Split using dates instead of individual rows.
train_date_end = int(total_dates * 0.70)
validation_date_end = int(total_dates * 0.85)

train_dates = unique_dates[:train_date_end]

validation_dates = unique_dates[
    train_date_end:validation_date_end
]

test_dates = unique_dates[
    validation_date_end:
]

# Assign every order on a particular date to the same dataset.
train_mask = df["order_date"].isin(train_dates)

validation_mask = df["order_date"].isin(
    validation_dates
)

test_mask = df["order_date"].isin(test_dates)

X_train = X.loc[train_mask].copy()
y_train = y.loc[train_mask].copy()

X_validation = X.loc[validation_mask].copy()
y_validation = y.loc[validation_mask].copy()

# Final test data is reserved.
X_test = X.loc[test_mask].copy()
y_test = y.loc[test_mask].copy()

df_train = df.loc[train_mask].copy()
df_validation = df.loc[validation_mask].copy()
df_test = df.loc[test_mask].copy()

print("Total unique dates:", total_dates)

print("\nTraining records:", len(X_train))
print("Validation records:", len(X_validation))
print("Reserved final test records:", len(X_test))

print("\nTraining date range:")
print(
    df_train["order_date"].min(),
    "to",
    df_train["order_date"].max()
)

print("\nValidation date range:")
print(
    df_validation["order_date"].min(),
    "to",
    df_validation["order_date"].max()
)

print("\nFinal test date range:")
print(
    df_test["order_date"].min(),
    "to",
    df_test["order_date"].max()
)

print("\nActual row distribution:")
print(
    "Training:",
    round(len(X_train) / len(df) * 100, 2),
    "%"
)

print(
    "Validation:",
    round(len(X_validation) / len(df) * 100, 2),
    "%"
)

print(
    "Final test:",
    round(len(X_test) / len(df) * 100, 2),
    "%"
)

# Confirm that no dates overlap.
train_date_set = set(train_dates)
validation_date_set = set(validation_dates)
test_date_set = set(test_dates)

assert train_date_set.isdisjoint(validation_date_set)
assert train_date_set.isdisjoint(test_date_set)
assert validation_date_set.isdisjoint(test_date_set)

print("\nDate overlap check: PASSED")

# Confirm chronological ordering.
assert df_train["order_date"].max() < (
    df_validation["order_date"].min()
)

assert df_validation["order_date"].max() < (
    df_test["order_date"].min()
)

print("Chronological ordering check: PASSED")

print("\nClass distribution:")

print(
    "Training delay rate:",
    round(y_train.mean(), 4)
)

print(
    "Validation delay rate:",
    round(y_validation.mean(), 4)
)

print(
    "Reserved test delay rate:",
    round(y_test.mean(), 4)
)


# ============================================================
# 4. BUILD PREPROCESSING PIPELINE
# ============================================================

print("\n4. BUILDING PREPROCESSING PIPELINE")
print("-" * 70)

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_transformer,
            numeric_features
        ),
        (
            "categorical",
            categorical_transformer,
            categorical_features
        )
    ]
)


# ============================================================
# 5. DEFINE MODELS
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=250,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        min_samples_leaf=10,
        random_state=RANDOM_STATE
    )
}


# ============================================================
# 6. TRAIN AND VALIDATE MODELS
# ============================================================

print("\n5. MODEL TRAINING AND VALIDATION")
print("=" * 70)

results = []
trained_models = {}

for model_name, classifier in models.items():

    print(f"\nTraining: {model_name}")
    print("-" * 50)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ]
    )

    pipeline.fit(
        X_train,
        y_train
    )

    probabilities = pipeline.predict_proba(
        X_validation
    )[:, 1]

    predictions = (
        probabilities >= 0.50
    ).astype(int)

    accuracy = accuracy_score(
        y_validation,
        predictions
    )

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_validation,
        probabilities
    )

    pr_auc = average_precision_score(
        y_validation,
        probabilities
    )

    tn, fp, fn, tp = confusion_matrix(
        y_validation,
        predictions,
        labels=[0, 1]
    ).ravel()

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC AUC": roc_auc,
        "PR AUC": pr_auc,
        "True Positives": tp,
        "False Positives": fp,
        "False Negatives": fn,
        "True Negatives": tn
    })

    trained_models[model_name] = pipeline

    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))
    print("ROC AUC:", round(roc_auc, 4))
    print("PR AUC:", round(pr_auc, 4))


# ============================================================
# 7. MODEL COMPARISON
# ============================================================

print("\n6. MODEL COMPARISON")
print("=" * 70)

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="ROC AUC",
    ascending=False
).reset_index(drop=True)

print(
    results_df.round(4).to_string(index=False)
)

results_path = (
    REPORT_DIR
    / "model_comparison_v3.csv"
)

results_df.to_csv(
    results_path,
    index=False
)


# ============================================================
# 8. SELECT BEST MODEL
# ============================================================

print("\n7. SELECTING BEST MODEL")
print("-" * 70)

best_model_name = results_df.iloc[0]["Model"]

best_model = trained_models[best_model_name]

best_model_path = (
    MODEL_DIR
    / "supplier_delay_v3_candidate.joblib"
)

joblib.dump(
    best_model,
    best_model_path
)

print("Selected model:", best_model_name)
print("Selection criterion: Highest validation ROC AUC")
print("Candidate model saved:")
print(best_model_path)


# ============================================================
# 9. VALIDATION CONFUSION MATRIX
# ============================================================

print("\n8. BEST MODEL VALIDATION CONFUSION MATRIX")
print("-" * 70)

best_probabilities = best_model.predict_proba(
    X_validation
)[:, 1]

best_predictions = (
    best_probabilities >= 0.50
).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_validation,
    best_predictions,
    labels=[0, 1]
).ravel()

print("Threshold: 0.50")
print("True Positives:", tp)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Negatives:", tn)


# ============================================================
# 10. SAVE VALIDATION PREDICTIONS
# ============================================================

validation_output = df_validation[
    [
        "order_id",
        "order_date",
        "supplier_id",
        "store_id",
        "product_category",
        "is_delayed"
    ]
].copy()

validation_output["predicted_probability"] = (
    best_probabilities
)

validation_output["predicted_class"] = (
    best_predictions
)

validation_output["prediction_correct"] = (
    validation_output["is_delayed"]
    == validation_output["predicted_class"]
)

validation_output_path = (
    REPORT_DIR
    / "validation_predictions_v3.csv"
)

validation_output.to_csv(
    validation_output_path,
    index=False
)


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n9. TRAINING SUMMARY")
print("=" * 70)

print("Training completed successfully.")

print("Best model:", best_model_name)

print(
    "Validation ROC AUC:",
    round(results_df.iloc[0]["ROC AUC"], 4)
)

print("\nDate overlap check: PASSED")

print("\nFinal test records remain untouched.")
print("No final test evaluation has been performed.")

print("\nSaved files:")
print(results_path)
print(best_model_path)
print(validation_output_path)

print("\nV3 MODEL TRAINING COMPLETED!")
