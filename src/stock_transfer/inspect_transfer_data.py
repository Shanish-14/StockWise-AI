
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "demand" / "train.parquet"


def main():
    print("=" * 65)
    print("STOCKWISE AI - FEATURE 4")
    print("INTER-STORE STOCK TRANSFER DATA INSPECTION")
    print("=" * 65)

    if not DATA_PATH.exists():
        print(f"Dataset not found: {DATA_PATH}")
        return

    parquet_file = pq.ParquetFile(DATA_PATH)

    # Read selected columns from sampled row groups
    row_group_ids = list(range(0, parquet_file.num_row_groups, 250))

    required_columns = [
        "store_id",
        "product_id",
        "dt",
        "sale_amount",
        "stock_hour6_22_cnt",
    ]

    parts = [
        parquet_file.read_row_group(
            group_id,
            columns=required_columns
        ).to_pandas()
        for group_id in row_group_ids
    ]

    df = pd.concat(parts, ignore_index=True)

    # Basic inspection
    print(f"\nSample records: {len(df):,}")
    print(f"Unique stores: {df['store_id'].nunique():,}")
    print(f"Unique products: {df['product_id'].nunique():,}")
    print(f"Date range: {df['dt'].min()} to {df['dt'].max()}")

    # Find products appearing in multiple stores on the same date
    grouped = (
        df.groupby(["product_id", "dt"])
        .agg(
            store_count=("store_id", "nunique"),
            min_availability=("stock_hour6_22_cnt", "min"),
            max_availability=("stock_hour6_22_cnt", "max"),
        )
        .reset_index()
    )

    multi_store = grouped[grouped["store_count"] >= 2].copy()

    different_availability = multi_store[
        multi_store["max_availability"] >
        multi_store["min_availability"]
    ]

    print("\nMULTI-STORE ANALYSIS")
    print("-" * 65)
    print(f"Product-date groups: {len(grouped):,}")
    print(f"Products in multiple stores: {len(multi_store):,}")
    print(
        "Groups with different stock availability:",
        f"{len(different_availability):,}"
    )

    print("\nTOP TRANSFER CANDIDATE GROUPS")
    print("-" * 65)

    print(
        different_availability
        .sort_values("max_availability", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nNOTE:")
    print(
        "Availability hours are indicators, not actual inventory quantities."
    )
    print(
        "Transfer quantities will require a separately labelled "
        "simulated inventory layer."
    )

    print("\nInspection completed successfully.")


if __name__ == "__main__":
    main()
