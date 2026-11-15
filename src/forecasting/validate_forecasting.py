
import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error

print("Loading test data and trained model...")

test_df = pd.read_parquet(
    "data/processed/test_data.parquet"
)

model_package = joblib.load(
    "models/demand_forecasting_model.pkl"
)

model = model_package["model"]
features = model_package["features"]

print("Generating predictions...")

test_df["predicted_demand"] = model.predict(
    test_df[features]
)

# Calculate daily performance
daily_results = []

for date, group in test_df.groupby("dt"):

    actual = group["demand"]
    predicted = group["predicted_demand"]

    baseline = group["lag_1"]

    daily_results.append({
        "date": date,
        "records": len(group),
        "model_mae": mean_absolute_error(actual, predicted),
        "baseline_mae": mean_absolute_error(actual, baseline),
        "model_rmse": np.sqrt(
            mean_squared_error(actual, predicted)
        )
    })

results = pd.DataFrame(daily_results)

print("\n========== DAILY FORECASTING PERFORMANCE ==========")
print(results.round(4).to_string(index=False))

# Save results
results.to_csv(
    "reports/daily_forecasting_validation.csv",
    index=False
)

print("\n========== OVERALL VALIDATION ==========")

print("Average daily model MAE:",
      round(results["model_mae"].mean(), 4))

print("Average daily baseline MAE:",
      round(results["baseline_mae"].mean(), 4))

better_days = (
    results["model_mae"] < results["baseline_mae"]
).sum()

print(
    "Days Random Forest outperformed baseline:",
    better_days,
    "out of",
    len(results)
)

print("\nValidation report saved successfully!")
