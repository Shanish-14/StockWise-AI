

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Load dataset
df = pd.read_csv(
    "data/processed/supplier_delay/supplier_delay_prepared.csv"
)

X = df.drop(columns=["is_delayed"])
y = df["is_delayed"]

# Identify columns
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

# Create Random Forest pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    (
        "model",
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

# Train model
print("Training Random Forest...")
model.fit(X_train, y_train)

# Get feature importance
preprocessor_fitted = model.named_steps["preprocessor"]
classifier = model.named_steps["model"]

feature_names = preprocessor_fitted.get_feature_names_out()
importance = classifier.feature_importances_

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importance
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

# Display top 15
print("\nTOP 15 IMPORTANT FEATURES")
print(importance_df.head(15).to_string(index=False))

# Plot
top_features = importance_df.head(15).sort_values(
    by="Importance"
)

plt.figure(figsize=(10, 7))
plt.barh(
    top_features["Feature"],
    top_features["Importance"]
)

plt.xlabel("Feature Importance")
plt.ylabel("Features")
plt.title("Supplier Delay Prediction - Feature Importance")
plt.tight_layout()

plt.savefig(
    "reports/supplier_delay/feature_importance.png",
    dpi=300
)

plt.show()

print("\nFeature importance report saved!")
