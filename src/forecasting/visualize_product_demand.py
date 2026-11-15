
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Select one store and product
STORE_ID = 50
PRODUCT_ID = 267

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["store_id", "product_id", "dt", "sale_amount"]
)

# Filter selected store-product combination
df = df[
    (df["store_id"] == STORE_ID) &
    (df["product_id"] == PRODUCT_ID)
].copy()

# Convert date and sort records
df["dt"] = pd.to_datetime(df["dt"])
df = df.sort_values("dt").reset_index(drop=True)

# Calculate 7-day rolling average
df["rolling_average"] = (
    df["sale_amount"].rolling(window=7).mean()
)

# Display summary
print("\nPRODUCT DEMAND SUMMARY")
print("Store ID:", STORE_ID)
print("Product ID:", PRODUCT_ID)
print("Total records:", len(df))
print("Average normalized sales:", df["sale_amount"].mean())
print("Zero-sales days:", (df["sale_amount"] == 0).sum())

# Create output folder
Path("reports").mkdir(parents=True, exist_ok=True)

# Plot demand trend
plt.figure(figsize=(12, 5))

plt.plot(
    df["dt"],
    df["sale_amount"],
    label="Daily normalized sales",
    alpha=0.6
)

plt.plot(
    df["dt"],
    df["rolling_average"],
    label="7-day rolling average",
    linewidth=2
)

plt.title(
    f"Demand Trend - Store {STORE_ID}, Product {PRODUCT_ID}"
)
plt.xlabel("Date")
plt.ylabel("Normalized Sales")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)

plt.tight_layout()

plt.savefig("reports/sample_product_demand_trend.png")
plt.show()

print("\nProduct demand visualization completed!")
