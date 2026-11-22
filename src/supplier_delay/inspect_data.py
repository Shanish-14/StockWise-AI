
import pandas as pd
from pathlib import Path

# Load dataset
file_path = Path(
    "data/raw/supplier_delay/supplier_orders.csv"
)

df = pd.read_csv(file_path)

# 1. Basic information
print("\n========== DATASET INFORMATION ==========")

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

# 2. Missing values
print("\n========== MISSING VALUES ==========")

print(df.isnull().sum())

# 3. Duplicate records
print("\n========== DUPLICATES ==========")

print("Duplicate rows:", df.duplicated().sum())

# 4. Statistical summary
print("\n========== STATISTICAL SUMMARY ==========")

print(df.describe())

# 5. Target distribution
print("\n========== DELAY DISTRIBUTION ==========")

print(df["is_delayed"].value_counts())

print("\nDelay percentage:")
print(
    (df["is_delayed"].value_counts(normalize=True) * 100)
    .round(2)
)

# 6. Supplier information
print("\n========== SUPPLIER INFORMATION ==========")

print("Number of suppliers:", df["supplier_id"].nunique())

print("\nOrders per supplier:")
print(df["supplier_id"].value_counts())

# 7. Delivery performance
print("\n========== DELIVERY PERFORMANCE ==========")

print(
    df.groupby("is_delayed")[
        ["promised_delivery_days", "actual_delivery_days"]
    ].mean().round(2)
)

print("\nDataset inspection completed!")
