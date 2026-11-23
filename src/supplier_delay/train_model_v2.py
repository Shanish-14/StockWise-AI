
import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)


# ==========================================
# 1. PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "data/raw/supplier_delay/supplier_orders_v2.csv"
MODEL_DIR = ROOT / "models/supplier_delay"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD DATA
# ==========================================

print("\n========================================")
print("SUPPLIER DELAY MODEL V2")
print("========================================")

df = pd.read_csv(DATA_PATH)

df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values("order_date").reset_index(drop=True)

print("Dataset loaded:", df.shape)


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
target = "is_delayed"

X = df[features]
y = df[target]


# ==========================================
# 4. CHRONOLOGICAL SPLIT
# ==========================================

total = len(df)

train_end = int(total * 0.70)
validation_end = int(total * 0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_val = X.iloc[train_end:validation_end]
y_val = y.iloc[train_end:validation_end]

X_test = X.iloc[validation_end:]
y_test = y.iloc[validation_end:]

print("\nDATA SPLIT")
print("----------------------------------------")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Final testing:", len(X_test))

print("\nTraining period:")
print(df["order_date"].iloc[0], "to",
      df["order_date"].iloc[train_end - 1])

print("\nValidation period:")
print(df["order_date"].iloc[train_end], "to",
      df["order_date"].iloc[validation_end - 1])

print("\nFinal testing period:")
print(df["order_date"].iloc[validation_end], "to",
      df["order_date"].iloc[-1])


# ==========================================
# 5. PREPROCESSING
# ==========================================

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numerical_features),
    ("cat", categorical_transformer, categorical_features)
])


# ==========================================
# 6. DEFINE MODELS
# ==========================================

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=250,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesClassifier(
        n_estimators=250,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
}


# ==========================================
# 7. TRAIN AND VALIDATE
# ==========================================

results = []
trained_models = {}

for model_name, model in models.items():

    print("\n========================================")
    print("Training:", model_name)
    print("========================================")

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_val)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

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
    roc_auc = roc_auc_score(y_val, probabilities)
    pr_auc = average_precision_score(y_val, probabilities)

    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))
    print("ROC AUC:", round(roc_auc, 4))
    print("PR AUC:", round(pr_auc, 4))

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC AUC": roc_auc,
        "PR AUC": pr_auc
    })

    trained_models[model_name] = pipeline


# ==========================================
# 8. COMPARE MODELS
# ==========================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="ROC AUC",
    ascending=False
)

print("\n========================================")
print("VALIDATION MODEL COMPARISON")
print("========================================")

print(results_df.to_string(index=False))


# ==========================================
# 9. SAVE BEST CANDIDATE
# ==========================================

best_model_name = results_df.iloc[0]["Model"]
best_model = trained_models[best_model_name]

model_path = MODEL_DIR / "supplier_delay_v2_candidate.joblib"

joblib.dump(best_model, model_path)

print("\n========================================")
print("BEST VALIDATION MODEL")
print("========================================")

print("Selected model:", best_model_name)
print("Selection metric: ROC AUC")
print("Saved to:", model_path)

print("\nFinal test data has NOT been used.")
print("Model training and validation completed.")
