

import pandas as pd
import joblib
import matplotlib.pyplot as plt
from pathlib import Path

print("Loading model and test data...")

test_df = pd.read_parquet(
    "data/processed/test_data.parquet"
)

model_package = joblib.load(
    "models/demand_forecasting_model.pkl"
)

model = model_package["model"]
features = model_package["features"]

Path("reports").mkdir(exist_ok=True)

# Generate predictions for the test dataset
test_df["predicted_demand"] = model.predict(
    test_df[features]
)

# Graph 1: Actual vs Predicted
sample = test_df.sample(
    n=min(5000, len(test_df)),
    random_state=42
)

plt.figure(figsize=(9, 6))

plt.scatter(
    sample["demand"],
    sample["predicted_demand"],
    alpha=0.3
)

# Perfect prediction reference line
minimum = min(
    sample["demand"].min(),
    sample["predicted_demand"].min()
)

maximum = max(
    sample["demand"].max(),
    sample["predicted_demand"].max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    linestyle="--",
    label="Perfect Prediction"
)

plt.xlabel("Actual Demand")
plt.ylabel("Predicted Demand")
plt.title("Actual vs Predicted Demand")
plt.legend()

plt.tight_layout()
plt.savefig("reports/actual_vs_predicted.png")
plt.close()

# Graph 2: One store-product combination
series = test_df[
    (test_df["store_id"] == 50) &
    (test_df["product_id"] == 267)
].sort_values("dt")

plt.figure(figsize=(12, 6))

plt.plot(
    series["dt"],
    series["demand"],
    marker="o",
    label="Actual Demand"
)

plt.plot(
    series["dt"],
    series["predicted_demand"],
    marker="o",
    label="Predicted Demand"
)

plt.xlabel("Date")
plt.ylabel("Normalized Demand")
plt.title("Demand Forecast: Store 50, Product 267")
plt.xticks(rotation=45)
plt.legend()

plt.tight_layout()
plt.savefig("reports/demand_prediction_comparison.png")
plt.close()

print("\nUPDATED VISUALIZATIONS COMPLETED!")
print("Saved both graphs in reports/")
print("\nSelected series records:", len(series))
