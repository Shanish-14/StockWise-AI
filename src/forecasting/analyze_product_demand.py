
import pandas as pd
import matplotlib.pyplot as plt

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["product_id", "sale_amount"]
)

# Calculate average sales for each product
product_demand = (
    df.groupby("product_id")["sale_amount"]
    .agg(["mean", "count"])
    .reset_index()
)

# Sort products by average normalized sales
top_products = product_demand.sort_values(
    by="mean",
    ascending=False
).head(10)

print("\nTOP 10 PRODUCTS BY AVERAGE NORMALIZED SALES")
print(top_products.to_string(index=False))

# Visualize top 10 products
plt.figure(figsize=(12, 6))

plt.bar(
    top_products["product_id"].astype(str),
    top_products["mean"]
)

plt.title("Top 10 Products by Average Normalized Sales")
plt.xlabel("Product ID")
plt.ylabel("Average Normalized Sales")
plt.xticks(rotation=45)
plt.grid(axis="y")

plt.tight_layout()

# Save chart
plt.savefig("reports/top_products_demand.png")

plt.show()

print("\nProduct demand analysis completed successfully!")
