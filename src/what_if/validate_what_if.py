


from pathlib import Path
import pandas as pd

# ============================================================
# STOCKWISE AI - FEATURE 5 VALIDATION
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILE = (
    ROOT / "data" / "processed" / "what_if"
    / "what_if_inventory_results.csv"
)

TRANSFER_FILE = (
    ROOT / "data" / "processed" / "what_if"
    / "what_if_transfer_recommendations.csv"
)

REPORT_FILE = (
    ROOT / "reports" / "what_if"
    / "what_if_validation_report.txt"
)

print("=" * 65)
print("STOCKWISE AI - FEATURE 5 VALIDATION")
print("=" * 65)

inventory = pd.read_csv(INVENTORY_FILE)
transfers = pd.read_csv(TRANSFER_FILE)

print("\nDATA LOADED")
print("-" * 65)
print(f"Inventory records: {len(inventory)}")
print(f"Transfer recommendations: {len(transfers)}")

results = []


def check(name, condition):
    passed = bool(condition)
    results.append((name, passed))
    print(f"{name}: {'PASS' if passed else 'FAIL'}")


# ============================================================
# INVENTORY VALIDATION
# ============================================================

print("\nINVENTORY VALIDATION")
print("-" * 65)

inventory_columns = [
    "store_id",
    "product_id",
    "scenario_daily_demand",
    "scenario_target_inventory",
    "estimated_inventory",
    "estimated_surplus",
    "estimated_shortage",
    "inventory_status",
]

missing = [
    col for col in inventory_columns
    if col not in inventory.columns
]

check("Required inventory columns exist", len(missing) == 0)

if not missing:

    check(
        "No missing inventory values",
        not inventory[inventory_columns].isnull().any().any()
    )

    check(
        "Demand values are non-negative",
        (inventory["scenario_daily_demand"] >= 0).all()
    )

    check(
        "Target inventory is non-negative",
        (inventory["scenario_target_inventory"] >= 0).all()
    )

    check(
        "Estimated inventory is non-negative",
        (inventory["estimated_inventory"] >= 0).all()
    )

    check(
        "Estimated surplus is non-negative",
        (inventory["estimated_surplus"] >= 0).all()
    )

    check(
        "Estimated shortage is non-negative",
        (inventory["estimated_shortage"] >= 0).all()
    )

    check(
        "Surplus and shortage are not both positive",
        not (
            (inventory["estimated_surplus"] > 0)
            & (inventory["estimated_shortage"] > 0)
        ).any()
    )

    expected_surplus = (
        inventory["estimated_inventory"]
        - inventory["scenario_target_inventory"]
    ).clip(lower=0)

    expected_shortage = (
        inventory["scenario_target_inventory"]
        - inventory["estimated_inventory"]
    ).clip(lower=0)

    check(
        "Surplus calculation is correct",
        (
            inventory["estimated_surplus"] == expected_surplus
        ).all()
    )

    check(
        "Shortage calculation is correct",
        (
            inventory["estimated_shortage"] == expected_shortage
        ).all()
    )

    expected_status = pd.Series(
        "Balanced",
        index=inventory.index
    )

    expected_status.loc[
        inventory["estimated_surplus"] > 0
    ] = "Surplus"

    expected_status.loc[
        inventory["estimated_shortage"] > 0
    ] = "Shortage"

    check(
        "Inventory status is correct",
        (
            inventory["inventory_status"].astype(str)
            == expected_status
        ).all()
    )


# ============================================================
# TRANSFER VALIDATION
# ============================================================

print("\nTRANSFER VALIDATION")
print("-" * 65)

transfer_columns = [
    "product_id",
    "donor_store_id",
    "receiver_store_id",
    "recommended_transfer_quantity",
]

missing = [
    col for col in transfer_columns
    if col not in transfers.columns
]

check("Required transfer columns exist", len(missing) == 0)

if not missing:

    check(
        "No missing transfer values",
        not transfers[transfer_columns].isnull().any().any()
    )

    check(
        "No self-transfers",
        (
            transfers["donor_store_id"]
            != transfers["receiver_store_id"]
        ).all()
    )

    check(
        "All transfer quantities are positive",
        (
            transfers["recommended_transfer_quantity"] > 0
        ).all()
    )

    check(
        "No duplicate recommendations",
        not transfers.duplicated(
            subset=[
                "product_id",
                "donor_store_id",
                "receiver_store_id"
            ]
        ).any()
    )

    # --------------------------------------------------------
    # DONOR SURPLUS VALIDATION
    # --------------------------------------------------------

    donor_totals = (
        transfers.groupby(
            ["donor_store_id", "product_id"]
        )["recommended_transfer_quantity"]
        .sum()
        .reset_index()
    )

    donor_inventory = inventory[
        ["store_id", "product_id", "estimated_surplus"]
    ].rename(
        columns={
            "store_id": "donor_store_id",
            "estimated_surplus": "available_surplus"
        }
    )

    donor_check = donor_totals.merge(
        donor_inventory,
        on=["donor_store_id", "product_id"],
        how="left",
        validate="one_to_one"
    )

    donor_valid = (
        donor_check["available_surplus"].notna().all()
        and (
            donor_check["recommended_transfer_quantity"]
            <= donor_check["available_surplus"]
        ).all()
    )

    check(
        "Donor transfers do not exceed estimated surplus",
        donor_valid
    )

    # --------------------------------------------------------
    # RECEIVER SHORTAGE VALIDATION
    # --------------------------------------------------------

    receiver_totals = (
        transfers.groupby(
            ["receiver_store_id", "product_id"]
        )["recommended_transfer_quantity"]
        .sum()
        .reset_index()
    )

    receiver_inventory = inventory[
        ["store_id", "product_id", "estimated_shortage"]
    ].rename(
        columns={
            "store_id": "receiver_store_id",
            "estimated_shortage": "available_shortage"
        }
    )

    receiver_check = receiver_totals.merge(
        receiver_inventory,
        on=["receiver_store_id", "product_id"],
        how="left",
        validate="one_to_one"
    )

    receiver_valid = (
        receiver_check["available_shortage"].notna().all()
        and (
            receiver_check["recommended_transfer_quantity"]
            <= receiver_check["available_shortage"]
        ).all()
    )

    check(
        "Receiver transfers do not exceed estimated shortage",
        receiver_valid
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

passed = sum(status for _, status in results)
failed = len(results) - passed

overall = "PASSED" if failed == 0 else "FAILED"

print("\n" + "=" * 65)
print("VALIDATION SUMMARY")
print("=" * 65)

print(f"Total checks: {len(results)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"\nOVERALL VALIDATION: {overall}")

# ============================================================
# SAVE REPORT
# ============================================================

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT_FILE, "w", encoding="utf-8") as file:
    file.write("STOCKWISE AI - WHAT-IF VALIDATION REPORT\n")
    file.write("=" * 55 + "\n\n")

    for name, status in results:
        file.write(
            f"{name}: {'PASS' if status else 'FAIL'}\n"
        )

    file.write(f"\nTotal checks: {len(results)}\n")
    file.write(f"Passed: {passed}\n")
    file.write(f"Failed: {failed}\n")
    file.write(f"\nOVERALL VALIDATION: {overall}\n")

print(f"\nValidation report saved:\n{REPORT_FILE}")

print("\n" + "=" * 65)
print("WHAT-IF VALIDATION COMPLETED")
print("=" * 65)
