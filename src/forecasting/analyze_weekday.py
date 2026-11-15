
import pandas as pd
import matplotlib.pyplot as plt

# Load required columns
df = pd.read_parquet(
    "data/raw/demand/train.parquet",
    columns=["dt", "sale_amount"]
)

# Convert date column
df["dt"] = pd.to_datetime(df["dt"])

# Calculate total normalized sales for each date
daily_sales = df.groupby("dt")["sale_amount"].sum().reset_index()

# Extract weekday name
daily_sales["weekday"] = daily_sales["dt"].dt.day_name()

# Calculate average daily normalized sales for each weekday
weekday_sales = (
    daily_sales.groupby("weekday")["sale_amount"]
    .mean()
    .reindex([
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ])
)

print("\nAVERAGE DAILY NORMALIZED SALES BY WEEKDAY")
print(weekday_sales)

# Visualize results
plt.figure(figsize=(10, 5))

weekday_sales.plot(kind="bar")

plt.title("Average Daily Normalized Sales by Weekday")
plt.xlabel("Weekday")
plt.ylabel("Average Daily Normalized Sales")
plt.xticks(rotation=45)
plt.grid(axis="y")

plt.tight_layout()

# Save chart
plt.savefig("reports/weekday_sales_analysis.png")

plt.show()

print("\nWeekday analysis completed successfully!")
