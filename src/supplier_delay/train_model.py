
import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

data_path = Path(
    "data/processed/supplier_delay/supplier_delay_prepared.csv"
)

df = pd.read_csv(data_path)

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# --------------------------------------------------
# 2. SEPARATE FEATURES AND TARGET
# --------------------------------------------------

X = df.drop(columns=["is_delayed"])

y = df["is_delayed"]

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
    "order_day_of_week",
    "order_month"
]


# --------------------------------------------------
# 3. TRAIN-TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# 4. PREPROCESSING
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            StandardScaler(),
            numerical_features
        )
    ]
)


# --------------------------------------------------
# 5. DEFINE MODELS
# --------------------------------------------------

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
}


# --------------------------------------------------
# 6. TRAIN AND EVALUATE
# --------------------------------------------------

results = []

best_model = None
best_f1 = -1
best_model_name = None

for name, model in models.items():

    print("\n================================")
    print("Training:", name)
    print("================================")

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

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

    roc_auc = roc_auc_score(
        y_test, probabilities
    )

    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))
    print("ROC AUC:", round(roc_auc, 4))

    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC AUC": roc_auc
    })

    if f1 > best_f1:

        best_f1 = f1
        best_model = pipeline
        best_model_name = name


# --------------------------------------------------
# 7. MODEL COMPARISON
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n================================")
print("MODEL COMPARISON")
print("================================")

print(
    results_df.round(4).to_string(index=False)
)


# --------------------------------------------------
# 8. SAVE BEST MODEL
# --------------------------------------------------

model_path = Path(
    "models/supplier_delay/supplier_delay_model.joblib"
)

model_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(best_model, model_path)

print("\n================================")
print("BEST MODEL")
print("================================")

print("Selected model:", best_model_name)
print("Best F1 Score:", round(best_f1, 4))

print("\nModel saved successfully!")
print("Location:", model_path.resolve())
