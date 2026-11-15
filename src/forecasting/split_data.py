
import pandas as pd
from pathlib import Path

print("Loading forecasting features...")

df = pd.read_parquet(
    "data/processed/forecasting_features.parquet"
)

df["dt"] = pd.to_datetime(df["dt"])

# Find the final date in the dataset
last_date = df["dt"].max()

# Reserve the final 14 days for testing
test_start_date = last_date - pd.Timedelta(days=13)

print("\nLast date:", last_date.date())
print("Testing starts:", test_start_date.date())

# Chronological split
train_df = df[df["dt"] < test_start_date].copy()
test_df = df[df["dt"] >= test_start_date].copy()

# Save both datasets
Path("data/processed").mkdir(parents=True, exist_ok=True)

train_df.to_parquet(
    "data/processed/train_data.parquet",
    index=False
)

test_df.to_parquet(
    "data/processed/test_data.parquet",
    index=False
)

print("\nDATA SPLITTING COMPLETED!")

print("\nTraining dataset:", train_df.shape)
print("Testing dataset:", test_df.shape)

print("\nTraining date range:")
print(train_df["dt"].min(), "to", train_df["dt"].max())

print("\nTesting date range:")
print(test_df["dt"].min(), "to", test_df["dt"].max())

print("\nSaved successfully!")
