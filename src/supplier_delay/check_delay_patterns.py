
import pandas as pd

# Load the original synthetic dataset
df = pd.read_csv("data/raw/supplier_delay/supplier_orders.csv")

print("\nDELAY RATE BY SUPPLIER RELIABILITY")
print(
    df.groupby(
        pd.cut(df["supplier_reliability"], bins=5),
        observed=True
    )["is_delayed"].mean()
)

print("\nDELAY RATE BY DISTANCE")
print(
    df.groupby(
        pd.cut(df["distance_km"], bins=5),
        observed=True
    )["is_delayed"].mean()
)

print("\nDELAY RATE BY CAPACITY UTILIZATION")
print(
    df.groupby(
        pd.cut(df["capacity_utilization"], bins=5),
        observed=True
    )["is_delayed"].mean()
)

print("\nDELAY RATE BY ORDER QUANTITY")
print(
    df.groupby(
        pd.cut(df["order_quantity"], bins=5),
        observed=True
    )["is_delayed"].mean()
)
