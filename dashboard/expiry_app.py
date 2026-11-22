

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
    page_title="StockWise AI - Expiry Management",
    page_icon="📦",
    layout="wide"
)

st.title("📦 StockWise AI")
st.subheader("Intelligent Expiry Management System")


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

    # Supported date formats
    date_patterns = [
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b"
    ]

    # Expiry keywords
    expiry_keywords = [
        "EXPIRY",
        "EXPIRES",
        "EXP",
        "USE BY",
        "BEST BEFORE",
        "BBE"
    ]

    # Manufacturing keywords
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

    # Supported Python date formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y"
    ]

    # ------------------------------------------------
    # READ OCR TEXT AND KEYWORD LOCATIONS
    # ------------------------------------------------

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

        # Detect expiry keywords
        for keyword in expiry_keywords:

            pattern = (
                r"(?<![A-Z])"
                + re.escape(keyword)
                + r"(?![A-Z])"
            )

            if re.search(pattern, text_upper):

                expiry_boxes.append(position)

                break

        # Detect manufacturing keywords
        for keyword in manufacturing_keywords:

            pattern = (
                r"(?<![A-Z])"
                + re.escape(keyword)
                + r"(?![A-Z])"
            )

            if re.search(pattern, text_upper):

                manufacturing_boxes.append(position)

                break

        # ------------------------------------------------
        # EXTRACT DATE CANDIDATES
        # ------------------------------------------------

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

    # ------------------------------------------------
    # SCORE DATE CANDIDATES
    # ------------------------------------------------

    for candidate in candidates:

        x1, y1 = candidate["position"]

        # Positive scoring for expiry keywords
        for x2, y2 in expiry_boxes:

            distance = math.sqrt(
                (x1 - x2) ** 2
                + (y1 - y2) ** 2
            )

            if distance < 250:

                candidate["score"] += 10

            elif distance < 450:

                candidate["score"] += 3

        # Negative scoring for manufacturing keywords
        for x2, y2 in manufacturing_boxes:

            distance = math.sqrt(
                (x1 - x2) ** 2
                + (y1 - y2) ** 2
            )

            if distance < 250:

                candidate["score"] -= 15

            elif distance < 450:

                candidate["score"] -= 5

    # ------------------------------------------------
    # REMOVE DUPLICATE DATES
    # ------------------------------------------------

    unique_candidates = {}

    for candidate in candidates:

        current_date = candidate["date"]

        if (
            current_date not in unique_candidates
            or candidate["score"]
            > unique_candidates[current_date]["score"]
        ):

            unique_candidates[current_date] = candidate

    # ------------------------------------------------
    # RANK DATE CANDIDATES
    # ------------------------------------------------

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

    # ------------------------------------------------
    # DISPLAY DETECTED DATES
    # ------------------------------------------------

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

    # ------------------------------------------------
    # SUMMARY METRICS
    # ------------------------------------------------

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

    # ------------------------------------------------
    # PRODUCT INVENTORY
    # ------------------------------------------------

    st.subheader("Product Inventory")

    st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------
    # EXPIRY ALERTS
    # ------------------------------------------------

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

    # ------------------------------------------------
    # DELETE PRODUCT
    # ------------------------------------------------

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
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "StockWise AI | Intelligent Grocery Inventory Management"
)
