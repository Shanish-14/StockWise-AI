
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stock_transfer"
    / "store_product_inventory_simulated.csv"
)

RECOMMENDATION_PATH = (
    PROJECT_ROOT
    / "reports"
    / "stock_transfer"
    / "transfer_recommendations.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "stock_transfer"
    / "transfer_validation_report.txt"
)


def main():

    print("=" * 65)
    print("STOCKWISE AI - FEATURE 4 VALIDATION")
    print("=" * 65)

    inventory = pd.read_csv(INVENTORY_PATH)
    recommendations = pd.read_csv(RECOMMENDATION_PATH)

    checks = []

    # 1. Self-transfer check
    self_transfers = (
        recommendations["donor_store_id"]
        == recommendations["receiver_store_id"]
    ).sum()

    checks.append({
        "check": "No self-transfers",
        "failed": int(self_transfers),
    })

    # 2. Duplicate recommendation check
    duplicates = recommendations.duplicated(
        [
            "product_id",
            "donor_store_id",
            "receiver_store_id",
        ]
    ).sum()

    checks.append({
        "check": "No duplicate recommendations",
        "failed": int(duplicates),
    })

    # 3. Positive transfer quantity
    invalid_quantity = (
        recommendations[
            "transfer_quantity_simulated_units"
        ] <= 0
    ).sum()

    checks.append({
        "check": "All transfer quantities are positive",
        "failed": int(invalid_quantity),
    })

    # 4. Donor surplus validation
    donor_transfers = (
        recommendations.groupby(
            ["product_id", "donor_store_id"]
        )["transfer_quantity_simulated_units"]
        .sum()
        .reset_index()
    )

    donor_inventory = inventory[
        [
            "product_id",
            "store_id",
            "simulated_surplus_units",
        ]
    ].rename(
        columns={"store_id": "donor_store_id"}
    )

    donor_check = donor_transfers.merge(
        donor_inventory,
        on=["product_id", "donor_store_id"],
        how="left",
    )

    donor_check["excess_transfer"] = (
        donor_check["transfer_quantity_simulated_units"]
        > donor_check["simulated_surplus_units"]
    )

    donor_failures = donor_check[
        "excess_transfer"
    ].sum()

    checks.append({
        "check": "Donor transfers do not exceed surplus",
        "failed": int(donor_failures),
    })

    # 5. Receiver shortage validation
    receiver_transfers = (
        recommendations.groupby(
            ["product_id", "receiver_store_id"]
        )["transfer_quantity_simulated_units"]
        .sum()
        .reset_index()
    )

    receiver_inventory = inventory[
        [
            "product_id",
            "store_id",
            "simulated_shortage_units",
        ]
    ].rename(
        columns={"store_id": "receiver_store_id"}
    )

    receiver_check = receiver_transfers.merge(
        receiver_inventory,
        on=["product_id", "receiver_store_id"],
        how="left",
    )

    receiver_check["excess_received"] = (
        receiver_check["transfer_quantity_simulated_units"]
        > receiver_check["simulated_shortage_units"]
    )

    receiver_failures = receiver_check[
        "excess_received"
    ].sum()

    checks.append({
        "check": "Receiver transfers do not exceed shortage",
        "failed": int(receiver_failures),
    })

    # 6. Missing inventory reference check
    missing_donors = donor_check[
        "simulated_surplus_units"
    ].isna().sum()

    missing_receivers = receiver_check[
        "simulated_shortage_units"
    ].isna().sum()

    checks.append({
        "check": "All donor inventory records exist",
        "failed": int(missing_donors),
    })

    checks.append({
        "check": "All receiver inventory records exist",
        "failed": int(missing_receivers),
    })

    # Display results
    print("\nVALIDATION RESULTS")
    print("-" * 65)

    for check in checks:

        status = (
            "PASS" if check["failed"] == 0
            else "FAIL"
        )

        print(
            f"{check['check']}: {status} "
            f"(Failures: {check['failed']})"
        )

    total_failures = sum(
        check["failed"] for check in checks
    )

    overall_status = (
        "PASSED" if total_failures == 0
        else "FAILED"
    )

    print("\n" + "=" * 65)
    print(f"OVERALL VALIDATION: {overall_status}")
    print(f"Total recommendations: {len(recommendations)}")
    print(
        "Total simulated transfer quantity:",
        recommendations[
            "transfer_quantity_simulated_units"
        ].sum(),
    )
    print("=" * 65)

    # Save validation report
    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as file:

        file.write("STOCKWISE AI - FEATURE 4 VALIDATION REPORT\n")
        file.write("=" * 55 + "\n\n")

        for check in checks:

            status = (
                "PASS" if check["failed"] == 0
                else "FAIL"
            )

            file.write(
                f"{check['check']}: {status} "
                f"(Failures: {check['failed']})\n"
            )

        file.write(f"\nOVERALL VALIDATION: {overall_status}\n")
        file.write(
            f"Total recommendations: {len(recommendations)}\n"
        )

        file.write(
            "Total simulated transfer quantity: "
            f"{recommendations['transfer_quantity_simulated_units'].sum()}\n"
        )

        file.write(
            "\nNOTE: Inventory quantities are simulated, "
            "not actual supermarket stock records.\n"
        )

    print("\nReport saved:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
