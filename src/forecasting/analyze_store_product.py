
import pandas as pd

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["store_id", "product_id", "dt", "sale_amount"]
)

# Convert date
df["dt"] = pd.to_datetime(df["dt"])

# Analyze each store-product combination
series_analysis = (
    df.groupby(["store_id", "product_id"])
    .agg(
        total_records=("dt", "count"),
        unique_dates=("dt", "nunique"),
        average_sales=("sale_amount", "mean")
    )
    .reset_index()
)

print("\nSTORE-PRODUCT ANALYSIS")

print(
    "\nTotal store-product combinations:",
    len(series_analysis)
)

print("\nRecords per combination:")
print(series_analysis["total_records"].describe())

print("\nUnique dates per combination:")
print(series_analysis["unique_dates"].describe())

# Identify combinations with complete 90-day coverage
complete_series = series_analysis[
    series_analysis["unique_dates"] == 90
]

print(
    "\nCombinations with 90 days of records:",
    len(complete_series)
)

print("\nTop 10 combinations by average sales:")
print(
    series_analysis.sort_values(
        "average_sales",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\nStore-product analysis completed successfully!")
