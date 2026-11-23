

import numpy as np
import pandas as pd
from pathlib import Path

# ============================================================
# STOCKWISE AI - SUPPLIER DELAY PREDICTION V3
# Grocery / Supermarket Supply Chain Simulation
# Synthetic data - NOT real supermarket records
# ============================================================

RANDOM_STATE = 42
TOTAL_ORDERS = 50000

rng = np.random.default_rng(RANDOM_STATE)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supplier_delay"
    / "v3"
    / "grocery_supplier_orders_v3.csv"
)

# ============================================================
# 1. SUPERMARKET NETWORK
# ============================================================

stores = [f"STORE_{i:03d}" for i in range(1, 21)]
suppliers = [f"SUP_{i:03d}" for i in range(1, 31)]
products = [f"PROD_{i:03d}" for i in range(1, 201)]

categories = [
    "Dairy",
    "Fruits",
    "Vegetables",
    "Bakery",
    "Packaged Food",
    "Beverages",
    "Frozen Food",
    "Household Essentials"
]

category_weights = {
    "Dairy": 0.75,
    "Fruits": 0.80,
    "Vegetables": 0.85,
    "Bakery": 0.55,
    "Packaged Food": 0.20,
    "Beverages": 0.25,
    "Frozen Food": 0.65,
    "Household Essentials": 0.15
}

# ============================================================
# 2. SUPPLIER PROFILES
# ============================================================

supplier_profiles = {}

for supplier in suppliers:
    supplier_profiles[supplier] = {
        "reliability": rng.uniform(0.72, 0.99),
        "capacity_baseline": rng.uniform(0.35, 0.85),
        "distance_factor": rng.uniform(0.50, 1.50)
    }

product_categories = {
    product: rng.choice(categories)
    for product in products
}

# ============================================================
# 3. ORDER DATES
# ============================================================

start_date = pd.Timestamp("2024-01-01")
end_date = pd.Timestamp("2025-12-31")

total_days = (end_date - start_date).days + 1

random_days = rng.integers(
    0,
    total_days,
    TOTAL_ORDERS
)

order_dates = (
    start_date
    + pd.to_timedelta(random_days, unit="D")
)

order_dates = (
    pd.Series(order_dates)
    .sort_values()
    .reset_index(drop=True)
)

# ============================================================
# 4. HISTORICAL SUPPLIER PERFORMANCE
# ============================================================

supplier_history = {
    supplier: []
    for supplier in suppliers
}

records = []

# Prior strength prevents extreme historical rates
# when a supplier has only a few previous orders.
PRIOR_STRENGTH = 10

# ============================================================
# 5. GENERATE ORDERS
# ============================================================

for i in range(TOTAL_ORDERS):

    order_date = order_dates.iloc[i]

    supplier = rng.choice(suppliers)
    store = rng.choice(stores)
    product = rng.choice(products)

    category = product_categories[product]
    profile = supplier_profiles[supplier]

    reliability = profile["reliability"]

    order_quantity = int(
        rng.integers(20, 1201)
    )

    distance = float(
        np.clip(
            rng.gamma(shape=2.5, scale=55)
            * profile["distance_factor"],
            5,
            600
        )
    )

    capacity_utilization = float(
        np.clip(
            rng.normal(
                profile["capacity_baseline"],
                0.10
            ),
            0.20,
            0.98
        )
    )

    # --------------------------------------------------------
    # PROMISED DELIVERY TIME
    # --------------------------------------------------------

    promised_days = int(
        np.clip(
            1 + distance / 180 + rng.integers(0, 3),
            1,
            7
        )
    )

    # --------------------------------------------------------
    # HISTORICAL DELAY RATE
    # Uses only previous orders from this supplier.
    # Recent history is smoothed using supplier reliability.
    # --------------------------------------------------------

    history = supplier_history[supplier]
    previous_orders = history[-20:]

    historical_prior = 1 - reliability

    historical_delay_rate = (
        sum(previous_orders)
        + historical_prior * PRIOR_STRENGTH
    ) / (
        len(previous_orders) + PRIOR_STRENGTH
    )

    # --------------------------------------------------------
    # CALENDAR FEATURES
    # --------------------------------------------------------

    day_of_week = order_date.day_of_week
    month = order_date.month

    is_festival_period = int(
        month in [8, 9, 10, 11, 12]
    )

    # --------------------------------------------------------
    # TRANSPORT RISK
    # Known estimated risk at order placement.
    # --------------------------------------------------------

    transport_risk = float(
        np.clip(
            rng.beta(2, 5)
            + (distance / 600) * 0.20
            + is_festival_period * 0.10,
            0,
            1
        )
    )

    # --------------------------------------------------------
    # UNEXPECTED DISRUPTIONS
    # Hidden events affecting actual delivery.
    # --------------------------------------------------------

    vehicle_breakdown = int(
        rng.binomial(1, 0.025)
    )

    unexpected_congestion = int(
        rng.binomial(1, 0.08)
    )

    # --------------------------------------------------------
    # RISK FEATURES
    # --------------------------------------------------------

    reliability_risk = 1 - reliability
    distance_risk = distance / 600
    quantity_risk = order_quantity / 1200
    short_lead_time_risk = 1 / promised_days

    category_risk_value = category_weights[category]

    # --------------------------------------------------------
    # REVISED DELAY PROBABILITY
    # Lower baseline risk and more balanced contributions.
    # --------------------------------------------------------

    risk_score = (
        -2.80
        + 1.50 * reliability_risk
        + 0.55 * distance_risk
        + 0.30 * quantity_risk
        + 0.55 * capacity_utilization
        + 0.45 * category_risk_value
        + 0.75 * historical_delay_rate
        + 0.25 * short_lead_time_risk
        + 0.15 * is_festival_period
        + 0.45 * transport_risk
        + 1.10 * vehicle_breakdown
        + 0.70 * unexpected_congestion
    )

    delay_probability = 1 / (
        1 + np.exp(-risk_score)
    )

    delay_probability = float(
        np.clip(delay_probability, 0.02, 0.90)
    )

    is_delayed = int(
        rng.binomial(1, delay_probability)
    )

    # --------------------------------------------------------
    # ACTUAL DELIVERY
    # --------------------------------------------------------

    if is_delayed == 1:
        extra_days = int(
            rng.integers(1, 6)
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

    # Save current result only AFTER calculating its
    # historical feature and prediction outcome.
    supplier_history[supplier].append(is_delayed)

    # --------------------------------------------------------
    # STORE RECORD
    # --------------------------------------------------------

    records.append({
        "order_id": f"ORD_{i + 1:06d}",
        "supplier_id": supplier,
        "store_id": store,
        "product_id": product,
        "product_category": category,
        "order_quantity": order_quantity,
        "distance_km": round(distance, 2),
        "supplier_reliability": round(reliability, 3),
        "capacity_utilization": round(
            capacity_utilization, 3
        ),
        "order_date": order_date,
        "promised_delivery_date": promised_date,
        "actual_delivery_date": actual_date,
        "promised_delivery_days": promised_days,
        "actual_delivery_days": actual_days,
        "historical_delay_rate": round(
            historical_delay_rate, 3
        ),
        "order_day_of_week": day_of_week,
        "order_month": month,
        "is_festival_period": is_festival_period,
        "transport_risk": round(transport_risk, 3),
        "is_delayed": is_delayed,
        "delay_days": extra_days
    })

# ============================================================
# 6. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)

date_columns = [
    "order_date",
    "promised_delivery_date",
    "actual_delivery_date"
]

for column in date_columns:
    df[column] = pd.to_datetime(df[column])

# ============================================================
# 7. VALIDATE TARGET
# ============================================================

expected_target = (
    df["actual_delivery_date"]
    > df["promised_delivery_date"]
).astype(int)

assert (
    df["is_delayed"] == expected_target
).all(), "Target/date mismatch detected!"

assert (
    df.loc[df["is_delayed"] == 0, "delay_days"] == 0
).all()

assert (
    df.loc[df["is_delayed"] == 1, "delay_days"] > 0
).all()

# ============================================================
# 8. SAVE DATASET
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

# ============================================================
# 9. GENERATION SUMMARY
# ============================================================

print("\nSTOCKWISE AI - SUPPLIER DELAY V3")
print("=" * 60)

print("\nDATASET INFORMATION")
print("-" * 60)

print("Dataset type: Synthetic grocery supply-chain simulation")
print("Total orders:", len(df))
print("Total suppliers:", df["supplier_id"].nunique())
print("Total stores:", df["store_id"].nunique())
print("Total products:", df["product_id"].nunique())
print("Total categories:", df["product_category"].nunique())

print("\nDATE RANGE")
print("-" * 60)
print("Start:", df["order_date"].min())
print("End:", df["order_date"].max())

print("\nDELAY DISTRIBUTION")
print("-" * 60)

print(
    df["is_delayed"]
    .value_counts()
    .sort_index()
)

print("\nDelay percentage:")
print(
    round(df["is_delayed"].mean() * 100, 2),
    "%"
)

print("\nDELAY RATE BY CATEGORY")
print("-" * 60)

print(
    df.groupby("product_category")["is_delayed"]
    .mean()
    .sort_values(ascending=False)
    .round(3)
)

print("\nDELAY RATE BY RELIABILITY")
print("-" * 60)

df["reliability_group"] = pd.cut(
    df["supplier_reliability"],
    bins=[0, 0.80, 0.90, 1.00],
    labels=["Low", "Medium", "High"],
    include_lowest=True
)

print(
    df.groupby("reliability_group", observed=False)[
        "is_delayed"
    ].mean().round(3)
)

print("\nDATA QUALITY")
print("-" * 60)

print("Missing values:", df.isnull().sum().sum())
print("Duplicate order IDs:", df["order_id"].duplicated().sum())
print("Duplicate rows:", df.duplicated().sum())

print("\nOUTPUT FILE")
print("-" * 60)
print(OUTPUT_PATH)

print("\nV3 DATASET GENERATION COMPLETED!")
