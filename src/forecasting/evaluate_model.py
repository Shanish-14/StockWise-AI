
import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("Loading test dataset and trained model...")

test_df = pd.read_parquet(
    "data/processed/test_data.parquet"
)

model_package = joblib.load(
    "models/demand_forecasting_model.pkl"
)

model = model_package["model"]
features = model_package["features"]

X_test = test_df[features]
y_test = test_df["demand"]

print("Generating Random Forest predictions...")

rf_predictions = model.predict(X_test)

# Simple baseline: yesterday's demand
baseline_predictions = test_df["lag_1"]

def evaluate(name, actual, predicted):
    print(f"\n{name}")
    print("MAE:", round(mean_absolute_error(actual, predicted), 4))
    print(
        "RMSE:",
        round(np.sqrt(mean_squared_error(actual, predicted)), 4)
    )
    print("R2:", round(r2_score(actual, predicted), 4))


print("\n========== MODEL COMPARISON ==========")

evaluate("NAIVE BASELINE (Yesterday's demand)", y_test, baseline_predictions)

evaluate("RANDOM FOREST", y_test, rf_predictions)

# Feature importance
importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values(
    by="importance",
    ascending=False
)

print("\n========== FEATURE IMPORTANCE ==========")
print(importance.to_string(index=False))

# Save feature importance
importance.to_csv(
    "reports/feature_importance.csv",
    index=False
)

print("\nFeature importance saved to reports/feature_importance.csv")
