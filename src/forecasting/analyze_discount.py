
import pandas as pd
import matplotlib.pyplot as plt

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["discount", "sale_amount"]
)

# Group discount values into ranges
df["discount_group"] = pd.cut(
    df["discount"],
    bins=[-float("inf"), 0, 0.1, 0.2, 0.3, 0.5, float("inf")],
    labels=[
        "No Discount",
        "0-10%",
        "10-20%",
        "20-30%",
        "30-50%",
        "Above 50%"
    ],
    include_lowest=True
)

# Calculate average normalized sales
discount_sales = (
    df.groupby("discount_group", observed=False)["sale_amount"]
    .mean()
)

print("\nAVERAGE SALES BY DISCOUNT GROUP")
print(discount_sales)

# Create visualization
plt.figure(figsize=(10, 5))

discount_sales.plot(kind="bar")

plt.title("Impact of Discounts on Average Normalized Sales")
plt.xlabel("Discount Group")
plt.ylabel("Average Normalized Sales")
plt.xticks(rotation=30)
plt.grid(axis="y")

plt.tight_layout()

# Save chart
plt.savefig("reports/discount_sales_analysis.png")

plt.show()

print("\nDiscount analysis completed successfully!")
