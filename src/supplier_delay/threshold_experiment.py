
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

# Load prepared dataset
df = pd.read_csv(
    "data/processed/supplier_delay/supplier_delay_prepared.csv"
)

X = df.drop(columns=["is_delayed"])
y = df["is_delayed"]

# Recreate the original test split
_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Load trained model
model = joblib.load(
    "models/supplier_delay/supplier_delay_model.joblib"
)

# Get probability of delay
probabilities = model.predict_proba(X_test)[:, 1]

print("\nSUPPLIER DELAY - THRESHOLD EXPERIMENT")
print("-" * 65)
print(
    f"{'Threshold':<12}"
    f"{'Precision':<14}"
    f"{'Recall':<14}"
    f"{'F1 Score':<12}"
)
print("-" * 65)

for threshold in [0.50, 0.40, 0.30, 0.20, 0.10]:
    predictions = (probabilities >= threshold).astype(int)

    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, zero_division=0
    )

    print(
        f"{threshold:<12.2f}"
        f"{precision:<14.4f}"
        f"{recall:<14.4f}"
        f"{f1:<12.4f}"
    )

print("-" * 65)
