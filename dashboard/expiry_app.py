




import streamlit as st
import pandas as pd
import easyocr
import re
import sys
import math
import numpy as np

from pathlib import Path
from datetime import date, datetime
from PIL import Image


# ==================================================
# 1. PROJECT PATH AND DATABASE
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.expiry.database import (
    add_product,
    get_products,
    delete_product
)


# ==================================================
# 2. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="StockWise AI - Inventory Management",
    page_icon="📦",
    layout="wide"
)

st.title("📦 StockWise AI")
st.subheader("Intelligent Grocery Inventory Management System")


# ==================================================
# 3. SESSION STATE
# ==================================================

if "ocr_candidates" not in st.session_state:
    st.session_state.ocr_candidates = []

if "last_scan" not in st.session_state:
    st.session_state.last_scan = None

if "expiry_date_input" not in st.session_state:
    st.session_state.expiry_date_input = date.today()


# ==================================================
# 4. DATABASE FUNCTIONS
# ==================================================

def load_inventory():
    return get_products()


# ==================================================
# 5. EXPIRY STATUS CLASSIFICATION
# ==================================================

def calculate_status(expiry_date):

    expiry = datetime.strptime(
        str(expiry_date),
        "%Y-%m-%d"
    ).date()

    days_remaining = (
        expiry - date.today()
    ).days

    if days_remaining < 0:
        status = "Expired"

    elif days_remaining <= 7:
        status = "Expiring Soon"

    else:
        status = "Safe"

    return days_remaining, status


# ==================================================
# 6. OCR READER
# ==================================================

@st.cache_resource
def load_ocr_reader():

    return easyocr.Reader(
        ["en"],
        gpu=False
    )


# ==================================================
# 7. SMART EXPIRY DATE DETECTION
# ==================================================

def extract_dates(ocr_results):

    date_patterns = [
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b"
    ]

    expiry_keywords = [
        "EXPIRY",
        "EXPIRES",
        "EXP",
        "USE BY",
        "BEST BEFORE",
        "BBE"
    ]

    manufacturing_keywords = [
        "MFG",
        "MFD",
        "MANUFACTURED",
        "MANUFACTURING",
        "PACKED ON",
        "PKD",
        "PROD DATE",
        "DATE OF MANUFACTURE"
    ]

    candidates = []
    expiry_boxes = []
    manufacturing_boxes = []

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y"
    ]

    for result in ocr_results:

        bbox, text, confidence = result

        text_upper = text.upper()

        center_x = sum(
            point[0] for point in bbox
        ) / 4

        center_y = sum(
            point[1] for point in bbox
        ) / 4

        position = (
            center_x,
            center_y
        )

        for keyword in expiry_keywords:

            pattern = (
                r"(?<![A-Z])"
                + re.escape(keyword)
                + r"(?![A-Z])"
            )

            if re.search(pattern, text_upper):

                expiry_boxes.append(position)
                break

        for keyword in manufacturing_keywords:

            pattern = (
                r"(?<![A-Z])"
                + re.escape(keyword)
                + r"(?![A-Z])"
            )

            if re.search(pattern, text_upper):

                manufacturing_boxes.append(position)
                break

        for pattern in date_patterns:

            matches = re.findall(
                pattern,
                text
            )

            for item in matches:

                parsed_date = None

                for fmt in formats:

                    try:

                        parsed_date = datetime.strptime(
                            item,
                            fmt
                        ).date()

                        break

                    except ValueError:
                        continue

                if parsed_date:

                    candidates.append({
                        "date": parsed_date,
                        "position": position,
                        "confidence": float(confidence),
                        "score": 0
                    })

    for candidate in candidates:

        x1, y1 = candidate["position"]

        for x2, y2 in expiry_boxes:

            distance = math.sqrt(
                (x1 - x2) ** 2
                + (y1 - y2) ** 2
            )

            if distance < 250:
                candidate["score"] += 10

            elif distance < 450:
                candidate["score"] += 3

        for x2, y2 in manufacturing_boxes:

            distance = math.sqrt(
                (x1 - x2) ** 2
                + (y1 - y2) ** 2
            )

            if distance < 250:
                candidate["score"] -= 15

            elif distance < 450:
                candidate["score"] -= 5

    unique_candidates = {}

    for candidate in candidates:

        current_date = candidate["date"]

        if (
            current_date not in unique_candidates
            or candidate["score"]
            > unique_candidates[current_date]["score"]
        ):

            unique_candidates[current_date] = candidate

    ranked_candidates = sorted(
        unique_candidates.values(),
        key=lambda item: (
            -item["score"],
            -item["confidence"]
        )
    )

    return ranked_candidates


# ==================================================
# 8. PRODUCT IMAGE SCANNING
# ==================================================

st.header("1. Scan Product Image")

uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image_token = (
        uploaded_file.name,
        uploaded_file.size
    )

    if st.session_state.last_scan != image_token:

        with st.spinner("Analyzing product image..."):

            reader = load_ocr_reader()

            image = Image.open(
                uploaded_file
            ).convert("RGB")

            image_array = np.array(image)

            ocr_results = reader.readtext(
                image_array
            )

            ranked_dates = extract_dates(
                ocr_results
            )

            st.session_state.ocr_candidates = ranked_dates
            st.session_state.last_scan = image_token

    if st.session_state.ocr_candidates:

        st.success(
            "Date candidates detected successfully!"
        )

        st.write("Ranked date candidates:")

        for index, candidate in enumerate(
            st.session_state.ocr_candidates,
            start=1
        ):

            st.write(
                f"{index}. "
                f"{candidate['date'].strftime('%Y-%m-%d')} "
                f"| Score: {candidate['score']} "
                f"| OCR confidence: "
                f"{candidate['confidence']:.2f}"
            )

        selected_date = st.selectbox(
            "Select the correct expiry date",
            options=[
                candidate["date"]
                for candidate in st.session_state.ocr_candidates
            ],
            format_func=lambda x: x.strftime("%Y-%m-%d")
        )

        if st.button("Use selected OCR date"):

            st.session_state.expiry_date_input = selected_date

            st.success(
                "Date selected! Confirm it in the registration form."
            )

    else:

        st.warning(
            "No valid date detected. "
            "Please enter the expiry date manually."
        )


# ==================================================
# 9. PRODUCT REGISTRATION
# ==================================================

st.header("2. Register Product")

with st.form("product_form"):

    product_name = st.text_input(
        "Product Name"
    )

    batch_number = st.text_input(
        "Batch Number"
    )

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        step=1
    )

    expiry_date = st.date_input(
        "Expiry Date",
        value=st.session_state.expiry_date_input,
        key="expiry_date_input"
    )

    submitted = st.form_submit_button(
        "Save Product"
    )

    if submitted:

        if (
            not product_name.strip()
            or not batch_number.strip()
        ):

            st.error(
                "Please enter product name and batch number."
            )

        else:

            add_product(
                product_name.strip(),
                batch_number.strip(),
                int(quantity),
                expiry_date.strftime("%Y-%m-%d")
            )

            st.success(
                "Product saved successfully!"
            )

            st.rerun()


# ==================================================
# 10. INVENTORY DASHBOARD
# ==================================================

st.header("3. Inventory Dashboard")

products = load_inventory()

if products:

    inventory = []

    for product in products:

        days, status = calculate_status(
            product["expiry_date"]
        )

        inventory.append({

            "ID": product["id"],
            "Product": product["product_name"],
            "Batch Number": product["batch_number"],
            "Quantity": product["quantity"],
            "Expiry Date": product["expiry_date"],
            "Days Remaining": days,
            "Status": status

        })

    df = pd.DataFrame(inventory)

    expired_count = (
        df["Status"] == "Expired"
    ).sum()

    expiring_count = (
        df["Status"] == "Expiring Soon"
    ).sum()

    safe_count = (
        df["Status"] == "Safe"
    ).sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Expired Products",
        int(expired_count)
    )

    col2.metric(
        "Expiring Soon",
        int(expiring_count)
    )

    col3.metric(
        "Safe Products",
        int(safe_count)
    )

    st.subheader("Product Inventory")

    st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("4. Expiry Alerts")

    alerts = df[
        df["Status"] != "Safe"
    ]

    if not alerts.empty:

        st.dataframe(
            alerts.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No expiry alerts!"
        )

    st.subheader("5. Delete Product")

    product_options = {

        f'{p["product_name"]} - '
        f'{p["batch_number"]} '
        f'(ID: {p["id"]})': p["id"]

        for p in products

    }

    selected_product = st.selectbox(
        "Select product to delete",
        options=list(product_options.keys())
    )

    if st.button("Delete Selected Product"):

        delete_product(
            product_options[selected_product]
        )

        st.success(
            "Product deleted successfully!"
        )

        st.rerun()

else:

    st.info(
        "No products registered yet. "
        "Add your first product above."
    )


# ==================================================
# 11. INTER-STORE STOCK TRANSFER OPTIMIZATION
# ==================================================

st.header("6. Inter-Store Stock Transfer Optimization")

TRANSFER_INVENTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stock_transfer"
    / "store_product_inventory_simulated.csv"
)

TRANSFER_RECOMMENDATIONS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "stock_transfer"
    / "transfer_recommendations.csv"
)

if (
    TRANSFER_INVENTORY_PATH.exists()
    and TRANSFER_RECOMMENDATIONS_PATH.exists()
):

    try:

        transfer_inventory = pd.read_csv(
            TRANSFER_INVENTORY_PATH
        )

        transfer_recommendations = pd.read_csv(
            TRANSFER_RECOMMENDATIONS_PATH
        )

        st.warning(
            "Inventory quantities are estimated using historical "
            "sales and product availability data. Actual physical "
            "stock counts are not available in the source dataset."
        )

        total_recommendations = len(
            transfer_recommendations
        )

        total_estimated_units = int(
            transfer_recommendations[
                "transfer_quantity_simulated_units"
            ].sum()
        ) if total_recommendations else 0

        unique_products = (
            transfer_recommendations["product_id"].nunique()
            if total_recommendations else 0
        )

        unique_store_pairs = (
            transfer_recommendations[
                ["donor_store_id", "receiver_store_id"]
            ].drop_duplicates().shape[0]
            if total_recommendations else 0
        )

        transfer_col1, transfer_col2, transfer_col3, transfer_col4 = (
            st.columns(4)
        )

        transfer_col1.metric(
            "Recommendations",
            total_recommendations
        )

        transfer_col2.metric(
            "Estimated Transfer Units",
            total_estimated_units
        )

        transfer_col3.metric(
            "Products",
            unique_products
        )

        transfer_col4.metric(
            "Store Pairs",
            unique_store_pairs
        )

        st.subheader("Recommended Stock Transfers")

        if not transfer_recommendations.empty:

            display_recommendations = (
                transfer_recommendations.rename(
                    columns={
                        "product_id": "Product ID",
                        "donor_store_id": "Donor Store",
                        "receiver_store_id": "Receiver Store",
                        "transfer_quantity_simulated_units":
                            "Suggested Transfer Quantity",
                        "donor_availability_hours":
                            "Donor Availability Hours",
                        "receiver_availability_hours":
                            "Receiver Availability Hours",
                        "donor_simulated_inventory":
                            "Donor Estimated Inventory",
                        "receiver_simulated_inventory":
                            "Receiver Estimated Inventory",
                        "receiver_estimated_daily_demand":
                            "Receiver Estimated Daily Demand",
                        "recommendation_basis":
                            "Recommendation Basis",
                    }
                )
            )

            st.dataframe(
                display_recommendations,
                use_container_width=True,
                hide_index=True
            )

            recommendation_csv = (
                transfer_recommendations.to_csv(index=False)
            )

            st.download_button(
                label="Download Transfer Recommendations",
                data=recommendation_csv,
                file_name="stockwise_transfer_recommendations.csv",
                mime="text/csv"
            )

        else:

            st.info(
                "No transfer recommendations are currently available."
            )

        st.subheader("Store-Product Inventory Overview")

        inventory_columns = [
            "store_id",
            "product_id",
            "average_daily_sales",
            "average_availability_hours",
            "estimated_daily_demand_units",
            "simulated_inventory_units",
            "target_inventory_units",
            "simulated_surplus_units",
            "simulated_shortage_units",
        ]

        available_inventory_columns = [
            column
            for column in inventory_columns
            if column in transfer_inventory.columns
        ]

        display_inventory = transfer_inventory[
            available_inventory_columns
        ].rename(
            columns={
                "store_id": "Store ID",
                "product_id": "Product ID",
                "average_daily_sales": "Average Daily Sales",
                "average_availability_hours":
                    "Average Availability Hours",
                "estimated_daily_demand_units":
                    "Estimated Daily Demand",
                "simulated_inventory_units":
                    "Estimated Inventory",
                "target_inventory_units":
                    "Target Inventory",
                "simulated_surplus_units":
                    "Estimated Surplus",
                "simulated_shortage_units":
                    "Estimated Shortage",
            }
        )

        st.dataframe(
            display_inventory,
            use_container_width=True,
            hide_index=True
        )

        inventory_csv = transfer_inventory.to_csv(index=False)

        st.download_button(
            label="Download Inventory Data",
            data=inventory_csv,
            file_name="stockwise_inventory_data.csv",
            mime="text/csv"
        )

    except Exception as error:

        st.error(
            "Unable to load the stock transfer data. "
            f"Details: {error}"
        )

else:

    st.info(
        "Stock transfer files were not found. Run the transfer "
        "generation script first: "
        "python src/stock_transfer/generate_transfer_candidates.py"
    )


# ==================================================
# 12. WHAT-IF ANALYSIS ENGINE
# ==================================================

def calculate_what_if_scenario(
    source_inventory,
    demand_change_percent,
    target_cover_days
):

    scenario = source_inventory.copy()

    demand_multiplier = (
        1 + demand_change_percent / 100
    )

    scenario["scenario_daily_demand"] = (
        scenario["estimated_daily_demand_units"]
        * demand_multiplier
    )

    scenario["scenario_target_inventory"] = np.ceil(
        scenario["scenario_daily_demand"]
        * target_cover_days
    )

    scenario["estimated_inventory"] = (
        scenario["simulated_inventory_units"]
    )

    scenario["estimated_surplus"] = (
        scenario["estimated_inventory"]
        - scenario["scenario_target_inventory"]
    ).clip(lower=0)

    scenario["estimated_shortage"] = (
        scenario["scenario_target_inventory"]
        - scenario["estimated_inventory"]
    ).clip(lower=0)

    scenario["inventory_status"] = "Balanced"

    scenario.loc[
        scenario["estimated_surplus"] > 0,
        "inventory_status"
    ] = "Surplus"

    scenario.loc[
        scenario["estimated_shortage"] > 0,
        "inventory_status"
    ] = "Shortage"

    return scenario


# ==================================================
# 13. WHAT-IF TRANSFER GENERATION
# ==================================================

def generate_what_if_transfers(scenario):

    recommendations = []

    for product_id, group in scenario.groupby("product_id"):

        donors = group[
            (group["average_availability_hours"] >= 4)
            & (group["estimated_surplus"] > 0)
        ].copy()

        receivers = group[
            (group["average_availability_hours"] <= 6)
            & (group["estimated_shortage"] > 0)
            & (group["scenario_daily_demand"] > 0)
        ].copy()

        donors = donors.sort_values(
            by=[
                "estimated_surplus",
                "average_availability_hours"
            ],
            ascending=[False, False]
        )

        receivers = receivers.sort_values(
            by=[
                "average_availability_hours",
                "estimated_shortage"
            ],
            ascending=[True, False]
        )

        donor_remaining = {
            index: int(row["estimated_surplus"])
            for index, row in donors.iterrows()
        }

        receiver_remaining = {
            index: int(row["estimated_shortage"])
            for index, row in receivers.iterrows()
        }

        for receiver_index, receiver in receivers.iterrows():

            for donor_index, donor in donors.iterrows():

                if receiver_remaining[receiver_index] <= 0:
                    break

                if donor_remaining[donor_index] <= 0:
                    continue

                if donor["store_id"] == receiver["store_id"]:
                    continue

                transfer_quantity = min(
                    donor_remaining[donor_index],
                    receiver_remaining[receiver_index]
                )

                if transfer_quantity <= 0:
                    continue

                recommendations.append({

                    "product_id": product_id,

                    "donor_store_id": int(
                        donor["store_id"]
                    ),

                    "receiver_store_id": int(
                        receiver["store_id"]
                    ),

                    "recommended_transfer_quantity": int(
                        transfer_quantity
                    ),

                    "donor_estimated_surplus": int(
                        donor_remaining[donor_index]
                    ),

                    "receiver_estimated_shortage": int(
                        receiver_remaining[receiver_index]
                    ),

                    "donor_availability_hours": round(
                        float(
                            donor["average_availability_hours"]
                        ),
                        2
                    ),

                    "receiver_availability_hours": round(
                        float(
                            receiver["average_availability_hours"]
                        ),
                        2
                    )

                })

                donor_remaining[donor_index] -= transfer_quantity

                receiver_remaining[receiver_index] -= transfer_quantity

    return pd.DataFrame(recommendations)


# ==================================================
# 14. INTERACTIVE WHAT-IF DASHBOARD
# ==================================================

st.header("7. What-if Analysis")

st.write(
    "Explore how changes in product demand and target stock "
    "coverage affect estimated inventory shortages, surplus "
    "and inter-store transfer recommendations."
)

WHAT_IF_INVENTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stock_transfer"
    / "store_product_inventory_simulated.csv"
)

if WHAT_IF_INVENTORY_PATH.exists():

    try:

        what_if_source = pd.read_csv(
            WHAT_IF_INVENTORY_PATH
        )

        st.warning(
            "What-if results use estimated inventory quantities. "
            "The original dataset does not contain actual physical "
            "stock counts. Scenario results are analytical estimates."
        )

        st.subheader("Scenario Settings")

        setting_col1, setting_col2 = st.columns(2)

        with setting_col1:

            demand_change = st.slider(
                "Demand Change (%)",
                min_value=-50,
                max_value=100,
                value=0,
                step=5,
                help="Change expected product demand."
            )

        with setting_col2:

            target_cover_days = st.slider(
                "Target Stock Coverage (Days)",
                min_value=1,
                max_value=7,
                value=2,
                step=1,
                help="Number of days of demand the store should hold."
            )

        st.caption(
            f"Scenario: Demand {demand_change:+d}% | "
            f"Target coverage: {target_cover_days} days"
        )

        # Calculate scenario

        what_if_results = calculate_what_if_scenario(
            what_if_source,
            demand_change,
            target_cover_days
        )

        what_if_transfers = generate_what_if_transfers(
            what_if_results
        )

        # Summary metrics

        shortage_count = int(
            (
                what_if_results["inventory_status"]
                == "Shortage"
            ).sum()
        )

        surplus_count = int(
            (
                what_if_results["inventory_status"]
                == "Surplus"
            ).sum()
        )

        balanced_count = int(
            (
                what_if_results["inventory_status"]
                == "Balanced"
            ).sum()
        )

        total_shortage = int(
            what_if_results["estimated_shortage"].sum()
        )

        total_surplus = int(
            what_if_results["estimated_surplus"].sum()
        )

        transfer_count = len(what_if_transfers)

        total_transfer_units = (
            int(
                what_if_transfers[
                    "recommended_transfer_quantity"
                ].sum()
            )
            if transfer_count > 0
            else 0
        )

        st.subheader("Scenario Results")

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Products with Shortage",
            shortage_count
        )

        metric2.metric(
            "Products with Surplus",
            surplus_count
        )

        metric3.metric(
            "Balanced Records",
            balanced_count
        )

        metric4, metric5, metric6 = st.columns(3)

        metric4.metric(
            "Estimated Shortage Units",
            f"{total_shortage:,}"
        )

        metric5.metric(
            "Estimated Surplus Units",
            f"{total_surplus:,}"
        )

        metric6.metric(
            "Recommended Transfer Units",
            f"{total_transfer_units:,}"
        )

        st.metric(
            "Transfer Recommendations",
            transfer_count
        )

        # Transfer recommendations

        st.subheader("Scenario Transfer Recommendations")

        if not what_if_transfers.empty:

            st.dataframe(
                what_if_transfers,
                use_container_width=True,
                hide_index=True
            )

            transfer_download = (
                what_if_transfers.to_csv(index=False)
            )

            st.download_button(
                label="Download Scenario Transfer Recommendations",
                data=transfer_download,
                file_name="stockwise_what_if_transfers.csv",
                mime="text/csv",
                key="what_if_transfer_download"
            )

        else:

            st.info(
                "No transfer recommendations were generated "
                "for this scenario."
            )

        # Inventory scenario details

        st.subheader("Store-Product Scenario Details")

        scenario_columns = [
            "store_id",
            "product_id",
            "scenario_daily_demand",
            "scenario_target_inventory",
            "estimated_inventory",
            "estimated_surplus",
            "estimated_shortage",
            "inventory_status"
        ]

        scenario_display = what_if_results[
            scenario_columns
        ].rename(
            columns={
                "store_id": "Store ID",
                "product_id": "Product ID",
                "scenario_daily_demand":
                    "Scenario Daily Demand",
                "scenario_target_inventory":
                    "Scenario Target Inventory",
                "estimated_inventory":
                    "Estimated Inventory",
                "estimated_surplus":
                    "Estimated Surplus",
                "estimated_shortage":
                    "Estimated Shortage",
                "inventory_status":
                    "Inventory Status"
            }
        )

        st.dataframe(
            scenario_display,
            use_container_width=True,
            hide_index=True
        )

        scenario_download = (
            what_if_results.to_csv(index=False)
        )

        st.download_button(
            label="Download What-if Scenario Results",
            data=scenario_download,
            file_name="stockwise_what_if_inventory.csv",
            mime="text/csv",
            key="what_if_inventory_download"
        )

        # Scenario summary

        st.subheader("Scenario Summary")

        summary = pd.DataFrame([{

            "demand_change_percent": demand_change,

            "target_cover_days": target_cover_days,

            "total_store_product_records": len(
                what_if_results
            ),

            "stores_products_with_shortage": shortage_count,

            "stores_products_with_surplus": surplus_count,

            "stores_products_balanced": balanced_count,

            "total_estimated_shortage_units": total_shortage,

            "total_estimated_surplus_units": total_surplus,

            "transfer_recommendations": transfer_count,

            "total_recommended_transfer_units": total_transfer_units

        }])

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            "What-if scenario calculated successfully!"
        )

    except Exception as error:

        st.error(
            f"Unable to run What-if Analysis: {error}"
        )

else:

    st.info(
        "What-if input inventory file was not found. "
        "Run the stock transfer generation script first."
    )


# ==================================================
# 15. FOOTER
# ==================================================

st.divider()

st.caption(
    "StockWise AI | Intelligent Grocery Inventory Management"
)
