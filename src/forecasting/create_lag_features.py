
import pandas as pd
from pathlib import Path

print("Loading prepared forecasting dataset...")

df = pd.read_parquet(
    "data/processed/forecasting_data.parquet"
)

print("Creating lag features...")

group_columns = ["store_id", "product_id"]

# Previous day demand
df["lag_1"] = (
    df.groupby(group_columns)["demand"].shift(1)
)

# Demand 7 days ago
df["lag_7"] = (
    df.groupby(group_columns)["demand"].shift(7)
)

# Demand 14 days ago
df["lag_14"] = (
    df.groupby(group_columns)["demand"].shift(14)
)

# Average demand over the previous 7 days
df["rolling_mean_7"] = (
    df.groupby(group_columns)["demand"]
    .transform(lambda x: x.shift(1).rolling(7).mean())
)

print("Removing rows without sufficient demand history...")

df = df.dropna().reset_index(drop=True)

output_path = "data/processed/forecasting_features.parquet"

df.to_parquet(output_path, index=False)

print("\nLAG FEATURE CREATION COMPLETED!")
print("Dataset shape:", df.shape)

print("\nFirst five records:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nSaved to:", output_path)
