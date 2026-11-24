

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "demand" / "train.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "stock_transfer"
REPORT_DIR = PROJECT_ROOT / "reports" / "stock_transfer"

RANDOM_SEED = 42

# Simulation assumptions, not real inventory values.
SALES_TO_SIMULATED_UNITS = 10
TARGET_COVER_DAYS = 2
DONOR_MIN_AVAILABILITY_HOURS = 4
RECEIVER_MAX_AVAILABILITY_HOURS = 6


def load_sample_data():

    parquet_file = pq.ParquetFile(DATA_PATH)

    row_group_ids = list(
        range(0, parquet_file.num_row_groups, 250)
    )

    columns = [
        "store_id",
        "product_id",
        "dt",
        "sale_amount",
        "stock_hour6_22_cnt",
    ]

    parts = [
        parquet_file.read_row_group(
            group_id,
            columns=columns
        ).to_pandas()
        for group_id in row_group_ids
    ]

    return pd.concat(parts, ignore_index=True)


def create_store_product_summary(df):

    summary = (
        df.groupby(["store_id", "product_id"])
        .agg(
            average_daily_sales=("sale_amount", "mean"),
            average_availability_hours=(
                "stock_hour6_22_cnt", "mean"
            ),
            observed_days=("dt", "nunique"),
        )
        .reset_index()
    )

    summary["average_daily_sales"] = (
        summary["average_daily_sales"].clip(lower=0)
    )

    return summary


def add_simulated_inventory(summary):

    rng = np.random.default_rng(RANDOM_SEED)

    summary = summary.copy()

    summary["estimated_daily_demand_units"] = (
        summary["average_daily_sales"]
        * SALES_TO_SIMULATED_UNITS
    )

    simulated_cover_days = rng.uniform(
        0.5, 5.0, size=len(summary)
    )

    summary["simulated_inventory_units"] = np.ceil(
        summary["estimated_daily_demand_units"]
        * simulated_cover_days
    ).astype(int)

    summary["target_inventory_units"] = np.ceil(
        summary["estimated_daily_demand_units"]
        * TARGET_COVER_DAYS
    ).astype(int)

    summary["simulated_surplus_units"] = (
        summary["simulated_inventory_units"]
        - summary["target_inventory_units"]
    ).clip(lower=0)

    summary["simulated_shortage_units"] = (
        summary["target_inventory_units"]
        - summary["simulated_inventory_units"]
    ).clip(lower=0)

    return summary


def generate_recommendations(summary):

    recommendations = []

    for product_id, group in summary.groupby("product_id"):

        donors = group[
            (
                group["average_availability_hours"]
                >= DONOR_MIN_AVAILABILITY_HOURS
            )
            & (group["simulated_surplus_units"] > 0)
        ].copy()

        receivers = group[
            (
                group["average_availability_hours"]
                <= RECEIVER_MAX_AVAILABILITY_HOURS
            )
            & (group["simulated_shortage_units"] > 0)
            & (group["estimated_daily_demand_units"] > 0)
        ].copy()

        if donors.empty or receivers.empty:
            continue

        # Track remaining simulated stock for every donor.
        remaining_surplus = {
            int(row["store_id"]): int(row["simulated_surplus_units"])
            for _, row in donors.iterrows()
        }

        # Track remaining simulated shortage for every receiver.
        remaining_shortage = {
            int(row["store_id"]): int(row["simulated_shortage_units"])
            for _, row in receivers.iterrows()
        }

        # Prioritize receivers with lower availability.
        receivers = receivers.sort_values(
            by=[
                "average_availability_hours",
                "simulated_shortage_units",
            ],
            ascending=[True, False],
        )

        for _, receiver in receivers.iterrows():

            receiver_id = int(receiver["store_id"])

            if remaining_shortage[receiver_id] <= 0:
                continue

            possible_donors = donors[
                donors["store_id"] != receiver_id
            ].copy()

            possible_donors["remaining_surplus"] = (
                possible_donors["store_id"]
                .map(remaining_surplus)
            )

            possible_donors = possible_donors[
                possible_donors["remaining_surplus"] > 0
            ]

            if possible_donors.empty:
                continue

            possible_donors = possible_donors.sort_values(
                by=[
                    "average_availability_hours",
                    "remaining_surplus",
                ],
                ascending=False,
            )

            donor = possible_donors.iloc[0]
            donor_id = int(donor["store_id"])

            transfer_quantity = min(
                remaining_surplus[donor_id],
                remaining_shortage[receiver_id],
            )

            if transfer_quantity <= 0:
                continue

            # Update remaining quantities immediately.
            remaining_surplus[donor_id] -= transfer_quantity
            remaining_shortage[receiver_id] -= transfer_quantity

            recommendations.append({
                "product_id": int(product_id),
                "donor_store_id": donor_id,
                "receiver_store_id": receiver_id,
                "transfer_quantity_simulated_units": int(
                    transfer_quantity
                ),
                "donor_availability_hours": round(
                    donor["average_availability_hours"], 2
                ),
                "receiver_availability_hours": round(
                    receiver["average_availability_hours"], 2
                ),
                "donor_simulated_inventory": int(
                    donor["simulated_inventory_units"]
                ),
                "receiver_simulated_inventory": int(
                    receiver["simulated_inventory_units"]
                ),
                "receiver_estimated_daily_demand": round(
                    receiver["estimated_daily_demand_units"], 2
                ),
                "recommendation_basis": (
                    "Real sales and availability indicators "
                    "+ simulated inventory"
                ),
            })

    return pd.DataFrame(recommendations)


def main():

    print("=" * 65)
    print("STOCKWISE AI - INTER-STORE STOCK TRANSFER ENGINE")
    print("=" * 65)

    if not DATA_PATH.exists():
        print(f"Dataset not found: {DATA_PATH}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n1. Loading retail dataset sample...")
    df = load_sample_data()
    print(f"Loaded records: {len(df):,}")

    print("\n2. Calculating store-product statistics...")
    summary = create_store_product_summary(df)
    print(f"Store-product combinations: {len(summary):,}")

    print("\n3. Creating simulated inventory layer...")
    summary = add_simulated_inventory(summary)
    print(f"Simulated inventory records: {len(summary):,}")

    print("\n4. Generating transfer recommendations...")
    recommendations = generate_recommendations(summary)

    summary_path = (
        OUTPUT_DIR / "store_product_inventory_simulated.csv"
    )

    recommendation_path = (
        REPORT_DIR / "transfer_recommendations.csv"
    )

    summary.to_csv(summary_path, index=False)

    recommendations.to_csv(
        recommendation_path, index=False
    )

    print("\n" + "=" * 65)
    print("TRANSFER ENGINE RESULTS")
    print("=" * 65)

    print(f"Store-product records: {len(summary):,}")
    print(f"Transfer recommendations: {len(recommendations):,}")

    if not recommendations.empty:

        print("\nTOP 10 TRANSFER RECOMMENDATIONS")
        print("-" * 65)

        print(
            recommendations
            .sort_values(
                "transfer_quantity_simulated_units",
                ascending=False,
            )
            .head(10)
            .to_string(index=False)
        )

        print("\nTOTAL SIMULATED TRANSFER QUANTITY:")
        print(
            recommendations[
                "transfer_quantity_simulated_units"
            ].sum()
        )

    else:
        print("\nNo transfer recommendations found.")

    print("\nFILES SAVED")
    print(summary_path)
    print(recommendation_path)

    print("\nIMPORTANT:")
    print("Inventory quantities are simulated, not real stock counts.")
    print("Transfer quantities cannot exceed tracked simulated donor surplus.")
    print("This is an experimental recommendation prototype.")

    print("\nTransfer engine completed.")


if __name__ == "__main__":
    main()
