
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score

# Load dataset
df = pd.read_csv(
    "data/processed/supplier_delay/supplier_delay_prepared.csv"
)

X = df.drop(columns=["is_delayed"])
y = df["is_delayed"]

categorical_features = [
    "supplier_id",
    "product_category"
]

numerical_features = [
    col for col in X.columns
    if col not in categorical_features
]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Preprocessing
preprocessor = ColumnTransformer([
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
])

# Build model
model = Pipeline([
    ("preprocessor", preprocessor),
    (
        "classifier",
        RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
    )
])

# Train
print("Training Random Forest...")
model.fit(X_train, y_train)

# Evaluate ROC AUC
probabilities = model.predict_proba(X_test)[:, 1]

print(
    "\nTest ROC AUC:",
    round(roc_auc_score(y_test, probabilities), 4)
)

# Calculate permutation importance
print("\nCalculating permutation importance...")

result = permutation_importance(
    model,
    X_test,
    y_test,
    scoring="roc_auc",
    n_repeats=5,
    random_state=42,
    n_jobs=-1
)

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": result.importances_mean,
    "Std": result.importances_std
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\nPERMUTATION IMPORTANCE")
print(importance_df.to_string(index=False))

importance_df.to_csv(
    "reports/supplier_delay/permutation_importance.csv",
    index=False
)

print("\nPermutation importance saved!")
