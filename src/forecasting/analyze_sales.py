
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load dataset
file_path = "data/raw/demand/train.parquet"

df = pd.read_parquet(
    file_path,
    columns=["dt", "sale_amount"]
)

# Convert date column into datetime format
df["dt"] = pd.to_datetime(df["dt"])

# Calculate average normalized sales for each date
daily_sales = df.groupby("dt", as_index=False).agg(
    average_sales=("sale_amount", "mean")
)

# Create output folders if they don't exist
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("reports").mkdir(parents=True, exist_ok=True)

# Save daily sales summary
daily_sales.to_csv(
    "data/processed/daily_sales_summary.csv",
    index=False
)

# Visualize daily sales patterns
plt.figure(figsize=(12, 5))

plt.plot(
    daily_sales["dt"],
    daily_sales["average_sales"],
    marker="o",
    markersize=3
)

plt.title("Average Daily Normalized Sales")
plt.xlabel("Date")
plt.ylabel("Average Normalized Sales")
plt.xticks(rotation=45)
plt.grid(True)

plt.tight_layout()

# Save chart
plt.savefig("reports/daily_sales_trend.png")

plt.show()

# Display results
print("\nDAILY SALES ANALYSIS")
print(daily_sales.head())

print("\nTotal dates analyzed:", len(daily_sales))
print("\nAverage normalized sales:", daily_sales["average_sales"].mean())

print("\nDaily sales analysis completed successfully!")
