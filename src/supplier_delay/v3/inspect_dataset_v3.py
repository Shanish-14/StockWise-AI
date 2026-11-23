
import pandas as pd
from pathlib import Path

# ============================================================
# STOCKWISE AI - SUPPLIER DELAY V3
# DATASET INSPECTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supplier_delay"
    / "v3"
    / "grocery_supplier_orders_v3.csv"
)

df = pd.read_csv(DATA_PATH, parse_dates=[
    "order_date",
    "promised_delivery_date",
    "actual_delivery_date"
])

print("\nSTOCKWISE AI - V3 DATASET INSPECTION")
print("=" * 65)

# 1. Basic information
print("\n1. DATASET SHAPE")
print("-" * 65)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n2. COLUMN NAMES")
print("-" * 65)
print(df.columns.tolist())

# 2. Target distribution
print("\n3. TARGET DISTRIBUTION")
print("-" * 65)

target_counts = df["is_delayed"].value_counts().sort_index()

for label, count in target_counts.items():
    name = "On time" if label == 0 else "Delayed"
    print(f"{name}: {count:,} ({count / len(df) * 100:.2f}%)")

# 3. Category analysis
print("\n4. DELAY RATE BY GROCERY CATEGORY")
print("-" * 65)

category_analysis = (
    df.groupby("product_category")
    .agg(
        total_orders=("order_id", "count"),
        delayed_orders=("is_delayed", "sum"),
        average_quantity=("order_quantity", "mean"),
        average_distance=("distance_km", "mean")
    )
)

category_analysis["delay_rate"] = (
    category_analysis["delayed_orders"]
    / category_analysis["total_orders"]
)

print(
    category_analysis.sort_values(
        "delay_rate", ascending=False
    ).round(3)
)

# 4. Supplier analysis
print("\n5. DELAY RATE BY SUPPLIER")
print("-" * 65)

supplier_analysis = (
    df.groupby("supplier_id")
    .agg(
        total_orders=("order_id", "count"),
        delayed_orders=("is_delayed", "sum"),
        reliability=("supplier_reliability", "first"),
        average_capacity=("capacity_utilization", "mean")
    )
)

supplier_analysis["delay_rate"] = (
    supplier_analysis["delayed_orders"]
    / supplier_analysis["total_orders"]
)

print(
    supplier_analysis.sort_values(
        "delay_rate", ascending=False
    ).round(3)
)

# 5. Historical delay rate groups
print("\n6. DELAY RATE BY HISTORICAL PERFORMANCE")
print("-" * 65)

df["history_group"] = pd.cut(
    df["historical_delay_rate"],
    bins=[-0.001, 0.20, 0.40, 0.60, 0.80, 1.001],
    labels=[
        "0-20%",
        "20-40%",
        "40-60%",
        "60-80%",
        "80-100%"
    ]
)

history_analysis = (
    df.groupby("history_group", observed=False)
    .agg(
        total_orders=("order_id", "count"),
        delayed_orders=("is_delayed", "sum")
    )
)

history_analysis["delay_rate"] = (
    history_analysis["delayed_orders"]
    / history_analysis["total_orders"]
)

print(history_analysis.round(3))

# 6. Reliability groups
print("\n7. DELAY RATE BY SUPPLIER RELIABILITY")
print("-" * 65)

df["reliability_group"] = pd.cut(
    df["supplier_reliability"],
    bins=[0, 0.80, 0.90, 1.00],
    labels=["Low", "Medium", "High"],
    include_lowest=True
)

reliability_analysis = (
    df.groupby("reliability_group", observed=False)
    .agg(
        total_orders=("order_id", "count"),
        delayed_orders=("is_delayed", "sum")
    )
)

reliability_analysis["delay_rate"] = (
    reliability_analysis["delayed_orders"]
    / reliability_analysis["total_orders"]
)

print(reliability_analysis.round(3))

# 7. Delay days
print("\n8. DELAY DAYS SUMMARY")
print("-" * 65)
print(df["delay_days"].describe().round(2))

# 8. Delay rate by month
print("\n9. DELAY RATE BY MONTH")
print("-" * 65)

monthly_analysis = (
    df.groupby("order_month")
    .agg(
        total_orders=("order_id", "count"),
        delayed_orders=("is_delayed", "sum")
    )
)

monthly_analysis["delay_rate"] = (
    monthly_analysis["delayed_orders"]
    / monthly_analysis["total_orders"]
)

print(monthly_analysis.round(3))

# 9. Date and target validation
print("\n10. DATE VALIDATION")
print("-" * 65)

expected_target = (
    df["actual_delivery_date"]
    > df["promised_delivery_date"]
).astype(int)

print(
    "Target/date disagreements:",
    (expected_target != df["is_delayed"]).sum()
)

print(
    "On-time orders with positive delay days:",
    ((df["is_delayed"] == 0) & (df["delay_days"] > 0)).sum()
)

print(
    "Delayed orders without positive delay days:",
    ((df["is_delayed"] == 1) & (df["delay_days"] <= 0)).sum()
)

# 10. Missing and duplicate checks
print("\n11. DATA QUALITY")
print("-" * 65)

print("Missing values:", df.isnull().sum().sum())
print("Duplicate order IDs:", df["order_id"].duplicated().sum())
print("Duplicate rows:", df.duplicated().sum())

print("\n12. NUMERIC FEATURE SUMMARY")
print("-" * 65)

numeric_columns = [
    "order_quantity",
    "distance_km",
    "supplier_reliability",
    "capacity_utilization",
    "promised_delivery_days",
    "historical_delay_rate",
    "transport_risk"
]

print(df[numeric_columns].describe().round(3))

print("\nV3 DATASET INSPECTION COMPLETED!")
