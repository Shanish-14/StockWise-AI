
import pandas as pd
from pathlib import Path

# Load raw dataset
input_path = Path(
    "data/raw/supplier_delay/supplier_orders.csv"
)

df = pd.read_csv(input_path)

# Convert date columns
df["order_date"] = pd.to_datetime(df["order_date"])
df["promised_delivery_date"] = pd.to_datetime(
    df["promised_delivery_date"]
)

# Calculate order weekday
df["order_day_of_week"] = df["order_date"].dt.dayofweek

# Calculate order month
df["order_month"] = df["order_date"].dt.month

# Select features available when order is placed
features = [
    "supplier_id",
    "product_category",
    "order_quantity",
    "distance_km",
    "supplier_reliability",
    "capacity_utilization",
    "promised_delivery_days",
    "order_day_of_week",
    "order_month"
]

target = "is_delayed"

# Create ML dataset
X = df[features].copy()
y = df[target].copy()

# Combine features and target
prepared_df = X.copy()
prepared_df[target] = y

# Save prepared dataset
output_path = Path(
    "data/processed/supplier_delay/supplier_delay_prepared.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

prepared_df.to_csv(output_path, index=False)

print("Data preparation completed!")

print("\nFeature shape:", X.shape)
print("Target shape:", y.shape)

print("\nSelected features:")
print(X.columns.tolist())

print("\nTarget distribution:")
print(y.value_counts())

print("\nMissing values:")
print(prepared_df.isnull().sum())

print("\nSaved to:", output_path.resolve())
