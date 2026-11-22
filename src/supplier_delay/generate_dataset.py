
import numpy as np
import pandas as pd
from pathlib import Path

# Reproducible random data
np.random.seed(42)

# Dataset size
N = 10000

# Supplier information
supplier_ids = [f"SUP_{i:03d}" for i in range(1, 21)]

supplier_reliability = {
    supplier: np.random.uniform(0.65, 0.98)
    for supplier in supplier_ids
}

categories = [
    "Dairy",
    "Bakery",
    "Fruits",
    "Vegetables",
    "Beverages",
    "Packaged Food",
    "Frozen Food"
]

# Generate order information
data = []

start_date = pd.Timestamp("2024-01-01")

for i in range(N):

    supplier = np.random.choice(supplier_ids)

    category = np.random.choice(categories)

    order_date = start_date + pd.Timedelta(
        days=int(np.random.randint(0, 900))
    )

    quantity = int(np.random.randint(10, 1001))

    distance = round(
        np.random.uniform(5, 500), 2
    )

    reliability = supplier_reliability[supplier]

    capacity = round(
        np.random.uniform(0.30, 1.00), 2
    )

    promised_days = int(
        np.random.randint(1, 8)
    )

    # Calculate probability of delay
    delay_probability = (
        0.05
        + (1 - reliability) * 0.65
        + (distance / 500) * 0.12
        + (quantity / 1000) * 0.10
        + capacity * 0.12
    )

    delay_probability = np.clip(
        delay_probability, 0.05, 0.90
    )

    # Simulate delivery delay
    is_delayed = int(
        np.random.random() < delay_probability
    )

    if is_delayed:
        extra_days = int(
            np.random.randint(1, 6)
        )
    else:
        extra_days = 0

    actual_days = promised_days + extra_days

    promised_date = (
        order_date
        + pd.Timedelta(days=promised_days)
    )

    actual_date = (
        order_date
        + pd.Timedelta(days=actual_days)
    )

    data.append({
        "order_id": f"ORD_{i + 1:05d}",
        "supplier_id": supplier,
        "product_category": category,
        "order_quantity": quantity,
        "distance_km": distance,
        "supplier_reliability": round(reliability, 2),
        "capacity_utilization": capacity,
        "order_date": order_date,
        "promised_delivery_date": promised_date,
        "actual_delivery_date": actual_date,
        "promised_delivery_days": promised_days,
        "actual_delivery_days": actual_days,
        "is_delayed": is_delayed
    })


# Convert to DataFrame
df = pd.DataFrame(data)

# Save dataset
output_path = Path(
    "data/raw/supplier_delay/supplier_orders.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(output_path, index=False)

# Display results
print("Dataset generated successfully!")

print("Shape:", df.shape)

print("\nFirst 5 records:")
print(df.head())

print("\nDelay distribution:")
print(df["is_delayed"].value_counts())

print("\nSaved to:", output_path.resolve())
