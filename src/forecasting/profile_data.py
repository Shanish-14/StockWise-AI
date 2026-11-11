
import pandas as pd

# Load dataset
df = pd.read_parquet("data/raw/demand/train.parquet")

print("========== DATASET ANALYSIS ==========")

# 1. Unique cities, stores and products
print("\nUnique cities:", df["city_id"].nunique())
print("Unique stores:", df["store_id"].nunique())
print("Unique products:", df["product_id"].nunique())

# 2. Date range
df["dt"] = pd.to_datetime(df["dt"])

print("\nStarting date:", df["dt"].min())
print("Ending date:", df["dt"].max())

# 3. Sales analysis
print("\nSales statistics:")
print(df["sale_amount"].describe())

# 4. Zero sales records
print("\nZero sales records:",
      (df["sale_amount"] == 0).sum())

# 5. Hourly sales examples
print("\nHourly sales examples:")
print(df["hours_sale"].head(3).to_string())

# 6. Stock status examples
print("\nStock status examples:")
print(df["hours_stock_status"].head(3).to_string())

# 7. Duplicate records
# Check duplicates using columns without array values
duplicate_columns = [
    col for col in df.columns
    if col not in ["hours_sale", "hours_stock_status"]
]

print(
    "\nDuplicate records:",
    df.duplicated(subset=duplicate_columns).sum()
)

print("\n========== ANALYSIS COMPLETED ==========")
