
import pandas as pd
from pathlib import Path

# ==========================================
# STOCKWISE AI - DATASET V2 INSPECTION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

FILE_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "supplier_delay"
    / "supplier_orders_v2.csv"
)

df = pd.read_csv(FILE_PATH, parse_dates=["order_date"])

df = df.sort_values("order_date").reset_index(drop=True)

print("\n" + "=" * 55)
print("SUPPLIER DATASET V2 - INSPECTION")
print("=" * 55)

# 1. Basic information

print("\n1. DATASET INFORMATION")
print("Shape:", df.shape)
print("Suppliers:", df["supplier_id"].nunique())
print("Products categories:", df["product_category"].nunique())

print("\n2. MISSING VALUES")
print(df.isnull().sum())

print("\n3. DUPLICATE RECORDS")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate order IDs:", df["order_id"].duplicated().sum())

# 4. Target distribution

print("\n4. TARGET DISTRIBUTION")

print(df["is_delayed"].value_counts())

print("\nTarget percentages:")

print(
    (df["is_delayed"].value_counts(normalize=True) * 100)
    .round(2)
)

# 5. Historical delay rate relationship

print("\n5. HISTORICAL DELAY RATE")

df["history_group"] = pd.cut(
    df["historical_delay_rate"],
    bins=[-0.001, 0.20, 0.40, 0.60, 0.80, 1.00],
    labels=["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
)

print(
    df.groupby(
        "history_group",
        observed=False
    )["is_delayed"].agg(["count", "mean"]).round(3)
)

# 6. Check delivery dates

print("\n6. DELIVERY DATE VALIDATION")

calculated_days = (
    df["actual_delivery_date"]
    if "actual_delivery_date" not in df.columns
    else pd.to_datetime(df["actual_delivery_date"])
)

actual_days = (
    calculated_days - df["order_date"]
).dt.days

print(
    "Rows where actual delivery was late:",
    (actual_days > df["promised_delivery_days"]).sum()
)

print(
    "Rows where target disagrees with delivery dates:",
    (
        (actual_days > df["promised_delivery_days"]).astype(int)
        != df["is_delayed"]
    ).sum()
)

# 7. Chronological split

print("\n7. CHRONOLOGICAL TRAIN/TEST SPLIT")

split_index = int(len(df) * 0.80)

train = df.iloc[:split_index].copy()
test = df.iloc[split_index:].copy()

print("Training records:", len(train))
print("Testing records:", len(test))

print("\nTraining date range:")
print(train["order_date"].min(), "to", train["order_date"].max())

print("\nTesting date range:")
print(test["order_date"].min(), "to", test["order_date"].max())

print("\nTraining delay distribution:")
print(train["is_delayed"].value_counts(normalize=True).round(3))

print("\nTesting delay distribution:")
print(test["is_delayed"].value_counts(normalize=True).round(3))

# 8. Feature leakage check

print("\n8. FEATURE LEAKAGE CHECK")

excluded_columns = [
    "order_id",
    "order_date",
    "promised_delivery_date",
    "actual_delivery_date",
    "actual_delivery_days",
    "is_delayed"
]

features = [
    col for col in df.columns
    if col not in excluded_columns
    and col != "history_group"
]

print("Potential model features:")
print(features)

print("\nExcluded columns:")
print(excluded_columns)

# 9. Final validation

print("\n9. FINAL VALIDATION")

print("Chronological order:", df["order_date"].is_monotonic_increasing)

print("Missing values:", df.isnull().sum().sum())

print("Duplicate rows:", df.duplicated().sum())

print("Training date before testing date:",
      train["order_date"].max() < test["order_date"].min())

print("\n" + "=" * 55)
print("INSPECTION COMPLETED")
print("=" * 55)
