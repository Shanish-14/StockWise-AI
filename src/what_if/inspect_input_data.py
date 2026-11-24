
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

RECOMMENDATIONS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "stock_transfer"
    / "transfer_recommendations.csv"
)


def inspect_file(file_path, file_name):

    print("\n" + "=" * 65)
    print(file_name)
    print("=" * 65)

    if not file_path.exists():
        print("ERROR: File not found:", file_path)
        return

    df = pd.read_csv(file_path)

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumn names:")
    for column in df.columns:
        print("-", column)

    print("\nFirst 5 records:")
    print(df.head().to_string(index=False))

    print("\nMissing values:")
    print(df.isnull().sum().to_string())

    print("\nData types:")
    print(df.dtypes.to_string())


if __name__ == "__main__":

    inspect_file(
        INVENTORY_PATH,
        "STORE-PRODUCT INVENTORY DATA"
    )

    inspect_file(
        RECOMMENDATIONS_PATH,
        "STOCK TRANSFER RECOMMENDATIONS"
    )

    print("\n" + "=" * 65)
    print("DATA INSPECTION COMPLETED")
    print("=" * 65)
