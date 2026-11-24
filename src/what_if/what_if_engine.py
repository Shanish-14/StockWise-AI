
from pathlib import Path
import pandas as pd
import numpy as np


# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stock_transfer"
    / "store_product_inventory_simulated.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "what_if"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "what_if"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. DEFAULT SCENARIO SETTINGS
# ==================================================

# These values will later become interactive dashboard controls.

DEMAND_CHANGE_PERCENT = 0
TARGET_COVER_DAYS = 3

DONOR_MIN_AVAILABILITY_HOURS = 4
RECEIVER_MAX_AVAILABILITY_HOURS = 6


# ==================================================
# 3. LOAD INVENTORY DATA
# ==================================================

def load_inventory():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"Inventory file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "store_id",
        "product_id",
        "average_daily_sales",
        "average_availability_hours",
        "estimated_daily_demand_units",
        "simulated_inventory_units"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return df


# ==================================================
# 4. CALCULATE WHAT-IF INVENTORY
# ==================================================

def calculate_scenario(
    df,
    demand_change_percent,
    target_cover_days
):

    if demand_change_percent < -100:

        raise ValueError(
            "Demand change cannot be below -100%."
        )

    if target_cover_days <= 0:

        raise ValueError(
            "Target cover days must be greater than zero."
        )

    result = df.copy()

    demand_multiplier = (
        1 + demand_change_percent / 100
    )

    # Calculate adjusted daily demand

    result["scenario_daily_demand"] = (
        result["estimated_daily_demand_units"]
        * demand_multiplier
    )

    # Calculate target inventory

    result["scenario_target_inventory"] = np.ceil(
        result["scenario_daily_demand"]
        * target_cover_days
    ).astype(int)

    # Use the existing estimated inventory quantity

    result["estimated_inventory"] = (
        result["simulated_inventory_units"]
    )

    # Calculate surplus

    result["estimated_surplus"] = (
        result["estimated_inventory"]
        - result["scenario_target_inventory"]
    ).clip(lower=0)

    # Calculate shortage

    result["estimated_shortage"] = (
        result["scenario_target_inventory"]
        - result["estimated_inventory"]
    ).clip(lower=0)

    # Inventory status

    result["inventory_status"] = np.select(
        [
            result["estimated_shortage"] > 0,
            result["estimated_surplus"] > 0
        ],
        [
            "Shortage",
            "Surplus"
        ],
        default="Balanced"
    )

    return result


# ==================================================
# 5. GENERATE TRANSFER RECOMMENDATIONS
# ==================================================

def generate_transfers(inventory):

    recommendations = []

    products = inventory["product_id"].unique()

    for product_id in products:

        product_data = inventory[
            inventory["product_id"] == product_id
        ].copy()

        # Donor stores

        donors = product_data[
            (
                product_data["average_availability_hours"]
                >= DONOR_MIN_AVAILABILITY_HOURS
            )
            & (
                product_data["estimated_surplus"] > 0
            )
        ].copy()

        # Receiver stores

        receivers = product_data[
            (
                product_data["average_availability_hours"]
                <= RECEIVER_MAX_AVAILABILITY_HOURS
            )
            & (
                product_data["estimated_shortage"] > 0
            )
            & (
                product_data["scenario_daily_demand"] > 0
            )
        ].copy()

        if donors.empty or receivers.empty:
            continue

        # Prioritize receivers with lower availability

        receivers = receivers.sort_values(
            by=[
                "average_availability_hours",
                "estimated_shortage"
            ],
            ascending=[True, False]
        )

        # Prioritize donors with greater surplus

        donors = donors.sort_values(
            by=[
                "estimated_surplus",
                "average_availability_hours"
            ],
            ascending=[False, False]
        )

        donor_remaining = {
            int(row["store_id"]): int(row["estimated_surplus"])
            for _, row in donors.iterrows()
        }

        receiver_remaining = {
            int(row["store_id"]): int(row["estimated_shortage"])
            for _, row in receivers.iterrows()
        }

        for _, receiver in receivers.iterrows():

            receiver_id = int(receiver["store_id"])

            for _, donor in donors.iterrows():

                donor_id = int(donor["store_id"])

                if donor_id == receiver_id:
                    continue

                available_surplus = donor_remaining[donor_id]

                required_quantity = receiver_remaining[
                    receiver_id
                ]

                if (
                    available_surplus <= 0
                    or required_quantity <= 0
                ):
                    continue

                transfer_quantity = min(
                    available_surplus,
                    required_quantity
                )

                if transfer_quantity <= 0:
                    continue

                recommendations.append({

                    "product_id": int(product_id),

                    "donor_store_id": donor_id,

                    "receiver_store_id": receiver_id,

                    "recommended_transfer_quantity":
                        int(transfer_quantity),

                    "donor_estimated_surplus":
                        int(available_surplus),

                    "receiver_estimated_shortage":
                        int(required_quantity),

                    "donor_availability_hours":
                        float(
                            donor["average_availability_hours"]
                        ),

                    "receiver_availability_hours":
                        float(
                            receiver["average_availability_hours"]
                        )

                })

                # Update remaining quantities

                donor_remaining[donor_id] -= transfer_quantity

                receiver_remaining[receiver_id] -= transfer_quantity

    return pd.DataFrame(recommendations)


# ==================================================
# 6. GENERATE SCENARIO SUMMARY
# ==================================================

def generate_summary(inventory, transfers):

    total_products = len(inventory)

    shortage_count = int(
        (inventory["inventory_status"] == "Shortage").sum()
    )

    surplus_count = int(
        (inventory["inventory_status"] == "Surplus").sum()
    )

    balanced_count = int(
        (inventory["inventory_status"] == "Balanced").sum()
    )

    total_shortage = int(
        inventory["estimated_shortage"].sum()
    )

    total_surplus = int(
        inventory["estimated_surplus"].sum()
    )

    total_transfer_units = (
        int(transfers["recommended_transfer_quantity"].sum())
        if not transfers.empty
        else 0
    )

    summary = {

        "demand_change_percent": DEMAND_CHANGE_PERCENT,

        "target_cover_days": TARGET_COVER_DAYS,

        "total_store_product_records": total_products,

        "stores_products_with_shortage": shortage_count,

        "stores_products_with_surplus": surplus_count,

        "stores_products_balanced": balanced_count,

        "total_estimated_shortage_units": total_shortage,

        "total_estimated_surplus_units": total_surplus,

        "transfer_recommendations": len(transfers),

        "total_recommended_transfer_units":
            total_transfer_units

    }

    return summary


# ==================================================
# 7. SAVE RESULTS
# ==================================================

def save_results(inventory, transfers, summary):

    inventory_path = (
        OUTPUT_DIR
        / "what_if_inventory_results.csv"
    )

    transfers_path = (
        OUTPUT_DIR
        / "what_if_transfer_recommendations.csv"
    )

    summary_path = (
        REPORT_DIR
        / "what_if_scenario_summary.csv"
    )

    inventory.to_csv(
        inventory_path,
        index=False
    )

    transfers.to_csv(
        transfers_path,
        index=False
    )

    pd.DataFrame([summary]).to_csv(
        summary_path,
        index=False
    )

    print("\nFILES SAVED")
    print("-" * 55)

    print(inventory_path)
    print(transfers_path)
    print(summary_path)


# ==================================================
# 8. MAIN EXECUTION
# ==================================================

if __name__ == "__main__":

    print("=" * 65)
    print("STOCKWISE AI - WHAT-IF ANALYSIS ENGINE")
    print("=" * 65)

    print("\nSCENARIO SETTINGS")
    print("-" * 55)

    print(
        f"Demand change: {DEMAND_CHANGE_PERCENT}%"
    )

    print(
        f"Target stock coverage: {TARGET_COVER_DAYS} days"
    )

    # Load inventory

    inventory_data = load_inventory()

    print("\nInventory records loaded:", len(inventory_data))

    # Calculate scenario

    scenario_inventory = calculate_scenario(
        inventory_data,
        DEMAND_CHANGE_PERCENT,
        TARGET_COVER_DAYS
    )

    # Generate transfers

    scenario_transfers = generate_transfers(
        scenario_inventory
    )

    # Generate summary

    summary = generate_summary(
        scenario_inventory,
        scenario_transfers
    )

    # Save files

    save_results(
        scenario_inventory,
        scenario_transfers,
        summary
    )

    # Display summary

    print("\nSCENARIO RESULTS")
    print("=" * 65)

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\nTRANSFER RECOMMENDATIONS")

    if scenario_transfers.empty:

        print("No transfer recommendations generated.")

    else:

        print(
            scenario_transfers.to_string(index=False)
        )

    print("\n" + "=" * 65)
    print("WHAT-IF ANALYSIS COMPLETED")
    print("=" * 65)
