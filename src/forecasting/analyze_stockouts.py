
import pandas as pd
import matplotlib.pyplot as plt

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["stock_hour6_22_cnt", "sale_amount"]
)

# Group records based on out-of-stock hours
df["stockout_group"] = pd.cut(
    df["stock_hour6_22_cnt"],
    bins=[-1, 0, 4, 8, 12, 16],
    labels=[
        "0 hours",
        "1-4 hours",
        "5-8 hours",
        "9-12 hours",
        "13-16 hours"
    ]
)

# Calculate average normalized sales
stockout_analysis = df.groupby(
    "stockout_group",
    observed=False
)["sale_amount"].agg(["mean", "count"])

print("\nSTOCKOUT HOURS VS SALES")
print(stockout_analysis)

# Create visualization
plt.figure(figsize=(10, 5))

stockout_analysis["mean"].plot(kind="bar")

plt.title("Out-of-Stock Hours vs Average Normalized Sales")
plt.xlabel("Out-of-Stock Hours")
plt.ylabel("Average Normalized Sales")
plt.xticks(rotation=30)
plt.grid(axis="y")

plt.tight_layout()

# Save chart
plt.savefig("reports/stockout_sales_analysis.png")

plt.show()

print("\nStockout analysis completed successfully!")
