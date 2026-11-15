
import pandas as pd
from pathlib import Path

print("Loading dataset...")

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=[
        "store_id",
        "product_id",
        "dt",
        "sale_amount",
        "discount",
        "holiday_flag"
    ]
)

# Convert date
df["dt"] = pd.to_datetime(df["dt"])

# Sort records
df = df.sort_values(
    ["store_id", "product_id", "dt"]
).reset_index(drop=True)

# Extract date features
df["day_of_week"] = df["dt"].dt.day_of_week
df["month"] = df["dt"].dt.month
df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)

# Rename target column
df = df.rename(
    columns={"sale_amount": "demand"}
)

# Select final columns
final_columns = [
    "store_id",
    "product_id",
    "dt",
    "demand",
    "day_of_week",
    "month",
    "is_weekend",
    "holiday_flag",
    "discount"
]

df = df[final_columns]

# Create output folder
Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# Save processed dataset
output_path = "data/processed/forecasting_data.parquet"

df.to_parquet(output_path, index=False)

print("\nDATA PREPARATION COMPLETED!")

print("\nDataset shape:", df.shape)

print("\nFirst five records:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nSaved to:", output_path)
