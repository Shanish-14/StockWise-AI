
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["holiday_flag", "sale_amount"]
)

# Calculate average normalized sales
holiday_sales = df.groupby("holiday_flag")["sale_amount"].agg(
    ["mean", "count"]
)

print("\nHOLIDAY VS NON-HOLIDAY SALES")
print(holiday_sales)

# Create labels for visualization
holiday_sales.index = [
    "Non-Holiday" if value == 0 else "Holiday"
    for value in holiday_sales.index
]

# Plot results
plt.figure(figsize=(8, 5))

holiday_sales["mean"].plot(kind="bar")

plt.title("Average Normalized Sales: Holiday vs Non-Holiday")
plt.xlabel("Day Type")
plt.ylabel("Average Normalized Sales")
plt.xticks(rotation=0)
plt.grid(axis="y")

plt.tight_layout()

# Save chart
plt.savefig("reports/holiday_sales_analysis.png")

plt.show()

print("\nHoliday analysis completed successfully!")
