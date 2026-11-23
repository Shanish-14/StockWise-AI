
import numpy as np
import pandas as pd
from pathlib import Path

# ==========================================
# STOCKWISE AI
# SUPPLIER DELAY DATASET V2
# ==========================================

SEED = 42
N_ORDERS = 20000
N_SUPPLIERS = 30

rng = np.random.default_rng(SEED)

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "data" / "raw" / "supplier_delay"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "supplier_orders_v2.csv"


# ==========================================
# 1. SUPPLIER INFORMATION
# ==========================================

supplier_ids = [
    f"SUP_{i:03d}"
    for i in range(1, N_SUPPLIERS + 1)
]

supplier_reliability = {
    supplier: round(float(rng.uniform(0.72, 0.98)), 3)
    for supplier in supplier_ids
}


# ==========================================
# 2. PRODUCT CATEGORIES
# ==========================================

categories = [
    "Dairy",
    "Bakery",
    "Fruits",
    "Vegetables",
    "Beverages",
    "Packaged Food",
    "Frozen Food"
]

# Simulation assumptions, not measured industry statistics.
category_risk = {
    "Dairy": 0.75,
    "Bakery": 0.40,
    "Fruits": 0.80,
    "Vegetables": 0.85,
    "Beverages": 0.25,
    "Packaged Food": 0.15,
    "Frozen Food": 0.65
}


# ==========================================
# 3. GENERATE ORDER DATES
# ==========================================

order_dates = pd.to_datetime(
    rng.integers(
        pd.Timestamp("2023-01-01").value // 10**9,
        pd.Timestamp("2025-12-31").value // 10**9,
        size=N_ORDERS
    ),
    unit="s"
)

# Sort chronologically.
order_dates = pd.Series(order_dates).sort_values().reset_index(drop=True)


# ==========================================
# 4. GENERATE SUPPLIER ORDERS
# ==========================================

historical_orders = {
    supplier: []
    for supplier in supplier_ids
}

records = []

for i in range(N_ORDERS):

    order_date = order_dates.iloc[i]

    supplier = rng.choice(supplier_ids)

    reliability = supplier_reliability[supplier]

    category = rng.choice(categories)

    quantity = int(rng.integers(10, 1001))

    distance = round(float(rng.uniform(5, 500)), 2)

    capacity = round(float(rng.uniform(0.30, 1.00)), 3)

    promised_days = int(rng.integers(1, 8))

    weekday = int(order_date.dayofweek)

    month = int(order_date.month)

    # ======================================
    # 5. HISTORICAL SUPPLIER PERFORMANCE
    # ======================================

    previous_delays = historical_orders[supplier][-20:]

    if len(previous_delays) > 0:
        historical_delay_rate = float(
            np.mean(previous_delays)
        )
    else:
        # Initial estimate before any supplier history exists.
        historical_delay_rate = 1 - reliability

    # ======================================
    # 6. CALCULATE DELIVERY RISK
    # ======================================

    reliability_risk = (0.95 - reliability) / 0.20

    distance_risk = distance / 500

    quantity_risk = quantity / 1000

    capacity_risk = (capacity - 0.30) / 0.70

    category_risk_value = category_risk[category]

    previous_performance_risk = (
        historical_delay_rate - 0.25
    )

    short_lead_time_risk = (
        7 - promised_days
    ) / 6

    weekend_risk = int(weekday >= 5)

    seasonal_risk = int(month in [6, 7, 8, 9])

    # ======================================
    # 7. DELAY PROBABILITY
    # ======================================

    risk_score = (
        -2.0
        + 0.95 * reliability_risk
        + 0.65 * distance_risk
        + 0.45 * quantity_risk
        + 0.75 * capacity_risk
        + 0.45 * category_risk_value
        + 1.20 * previous_performance_risk
        + 0.25 * short_lead_time_risk
        + 0.20 * weekend_risk
        + 0.15 * seasonal_risk
    )

    # Convert risk score into probability.
    probability = 1 / (1 + np.exp(-risk_score))

    probability = float(
        np.clip(probability, 0.03, 0.90)
    )

    # ======================================
    # 8. GENERATE DELIVERY OUTCOME
    # ======================================

    is_delayed = int(
        rng.random() < probability
    )

    if is_delayed:
        extra_days = int(rng.integers(1, 6))
    else:
        extra_days = 0

    actual_delivery_days = (
        promised_days + extra_days
    )

    promised_delivery_date = (
        order_date + pd.Timedelta(days=promised_days)
    )

    actual_delivery_date = (
        order_date + pd.Timedelta(days=actual_delivery_days)
    )

    # ======================================
    # 9. SAVE ORDER RECORD
    # ======================================

    records.append({

        "order_id": f"ORD_{i + 1:06d}",

        "supplier_id": supplier,

        "product_category": category,

        "order_quantity": quantity,

        "distance_km": distance,

        "supplier_reliability": reliability,

        "capacity_utilization": capacity,

        "order_date": order_date,

        "promised_delivery_date": promised_delivery_date,

        "actual_delivery_date": actual_delivery_date,

        "promised_delivery_days": promised_days,

        "actual_delivery_days": actual_delivery_days,

        "historical_delay_rate": round(
            historical_delay_rate, 4
        ),

        "order_day_of_week": weekday,

        "order_month": month,

        "is_delayed": is_delayed

    })

    # Update history only AFTER generating this order.
    historical_orders[supplier].append(is_delayed)


# ==========================================
# 10. CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(records)

df = df.sort_values(
    "order_date"
).reset_index(drop=True)


# ==========================================
# 11. SAVE DATASET
# ==========================================

df.to_csv(OUTPUT_FILE, index=False)


# ==========================================
# 12. DATASET VALIDATION REPORT
# ==========================================

print("\n" + "=" * 55)
print("STOCKWISE AI - SUPPLIER DATASET V2")
print("=" * 55)

print("\nDataset saved successfully!")

print("File:", OUTPUT_FILE)

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nDelay distribution:")
print(df["is_delayed"].value_counts())

print("\nDelay percentage:")
print(
    (df["is_delayed"].value_counts(normalize=True) * 100)
    .round(2)
)

print("\nDelay rate by supplier reliability:")

df["reliability_group"] = pd.cut(
    df["supplier_reliability"],
    bins=[0.70, 0.80, 0.90, 1.00],
    labels=["Low", "Medium", "High"],
    include_lowest=True
)

print(
    df.groupby(
        "reliability_group",
        observed=False
    )["is_delayed"].mean().round(3)
)

print("\nDelay rate by distance:")

df["distance_group"] = pd.cut(
    df["distance_km"],
    bins=[0, 150, 300, 500],
    labels=["Short", "Medium", "Long"]
)

print(
    df.groupby(
        "distance_group",
        observed=False
    )["is_delayed"].mean().round(3)
)

print("\nDelay rate by product category:")

print(
    df.groupby("product_category")["is_delayed"]
    .mean()
    .sort_values(ascending=False)
    .round(3)
)

print("\nMissing values:", df.isnull().sum().sum())

print("Duplicate rows:", df.duplicated().sum())

print(
    "\nDate range:",
    df["order_date"].min(),
    "to",
    df["order_date"].max()
)

print("\n" + "=" * 55)
print("DATASET GENERATION COMPLETED")
print("=" * 55)
