

import streamlit as st
import easyocr
import re
import pandas as pd

from datetime import datetime, date
from dateutil import parser


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="StockWise AI - Expiry Management",
    page_icon="📦",
    layout="wide"
)


# ==========================================
# 2. SESSION STATE
# ==========================================

if "products" not in st.session_state:
    st.session_state.products = []

if "ocr_candidates" not in st.session_state:
    st.session_state.ocr_candidates = []

if "expiry_date_input" not in st.session_state:
    st.session_state.expiry_date_input = date.today()

if "ocr_image_id" not in st.session_state:
    st.session_state.ocr_image_id = None

if "last_applied_scan" not in st.session_state:
    st.session_state.last_applied_scan = None


# ==========================================
# 3. OCR MODEL
# ==========================================

@st.cache_resource
def load_ocr():
    return easyocr.Reader(["en"], gpu=False)


# ==========================================
# 4. DATE PARSING
# ==========================================

def parse_product_date(text):

    text = text.strip()

    try:
        return parser.parse(
            text,
            dayfirst=True,
            fuzzy=False
        ).date()

    except (ValueError, OverflowError):
        return None


# ==========================================
# 5. DATE EXTRACTION
# ==========================================

def extract_dates(text):

    patterns = [
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{2}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b",
        r"\b\d{1,2}[./-]\d{4}\b",
        r"\b\d{4}[./-]\d{1,2}\b",
        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b",
        r"\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4}\b"
    ]

    found_dates = []

    for pattern in patterns:
        found_dates.extend(re.findall(pattern, text))

    unique_dates = []

    for item in sorted(found_dates, key=len, reverse=True):
        if not any(item in existing for existing in unique_dates):
            unique_dates.append(item)

    return unique_dates


# ==========================================
# 6. EXPIRY STATUS
# ==========================================

def calculate_expiry_status(expiry_date):

    today = date.today()

    remaining_days = (expiry_date - today).days

    if remaining_days < 0:
        status = "Expired"

    elif remaining_days <= 7:
        status = "Expiring Soon"

    else:
        status = "Safe"

    return status, remaining_days


# ==========================================
# 7. APPLICATION HEADER
# ==========================================

st.title("📦 StockWise AI")
st.subheader("Intelligent Expiry Management System")

st.write(
    "Scan product labels, register batches "
    "and monitor expiry dates."
)

st.divider()


# ==========================================
# 8. IMAGE UPLOAD AND OCR
# ==========================================

st.header("📷 Scan Product Expiry Date")

uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Uploaded Product",
        width=350
    )

    image_id = (
        uploaded_file.name,
        uploaded_file.size
    )

    if st.session_state.ocr_image_id != image_id:

        st.session_state.ocr_image_id = image_id
        st.session_state.ocr_candidates = []
        st.session_state.last_applied_scan = None

    if st.button("Read Expiry Date"):

        with st.spinner("Reading product image..."):

            reader = load_ocr()

            results = reader.readtext(
                uploaded_file.getvalue()
            )

            detected_text = [
                result[1] for result in results
            ]

            full_text = " ".join(detected_text)

            date_candidates = extract_dates(full_text)

            parsed_candidates = []

            for date_text in date_candidates:

                parsed_date = parse_product_date(date_text)

                if parsed_date:
                    parsed_candidates.append(
                        (date_text, parsed_date)
                    )

            st.session_state.ocr_candidates = parsed_candidates

            st.session_state.last_applied_scan = None

            st.session_state.pop(
                "ocr_date_choice",
                None
            )

            st.session_state.last_ocr_text = detected_text

    if "last_ocr_text" in st.session_state:

        with st.expander("View OCR detected text"):
            for text in st.session_state.last_ocr_text:
                st.write("- ", text)

    if st.session_state.ocr_candidates:

        st.subheader("Detected Date Candidates")

        selected_date = st.selectbox(
            "Select the correct expiry date",
            options=st.session_state.ocr_candidates,
            format_func=lambda item: (
                f"{item[0]} → {item[1]}"
            ),
            key="ocr_date_choice"
        )

        scan_token = (
            str(st.session_state.ocr_image_id)
            + selected_date[0]
        )

        if st.session_state.last_applied_scan != scan_token:

            st.session_state.expiry_date_input = selected_date[1]

            st.session_state.last_applied_scan = scan_token

        st.success(
            "OCR date selected. Please verify it before saving."
        )

    elif "last_ocr_text" in st.session_state:

        st.warning(
            "No readable date found. You can enter the date manually."
        )


st.divider()


# ==========================================
# 9. PRODUCT REGISTRATION
# ==========================================

st.header("➕ Add Product")

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
        value=1,
        step=1
    )

    expiry_date = st.date_input(
        "Expiry Date",
        key="expiry_date_input"
    )

    submitted = st.form_submit_button(
        "Save Product"
    )

    if submitted:

        if not product_name.strip():

            st.error("Please enter a product name.")

        else:

            status, remaining_days = calculate_expiry_status(
                expiry_date
            )

            product = {
                "Product": product_name.strip(),
                "Batch Number": batch_number.strip(),
                "Quantity": quantity,
                "Expiry Date": expiry_date,
                "Days Remaining": remaining_days,
                "Status": status
            }

            st.session_state.products.append(product)

            st.success("Product saved successfully!")


st.divider()


# ==========================================
# 10. INVENTORY DASHBOARD
# ==========================================

st.header("📊 Inventory Dashboard")

products_df = pd.DataFrame(
    st.session_state.products
)

if not products_df.empty:

    # Recalculate status using today's date
    statuses = products_df["Expiry Date"].apply(
        calculate_expiry_status
    )

    products_df["Status"] = [
        item[0] for item in statuses
    ]

    products_df["Days Remaining"] = [
        item[1] for item in statuses
    ]

    expired_count = (
        products_df["Status"] == "Expired"
    ).sum()

    expiring_count = (
        products_df["Status"] == "Expiring Soon"
    ).sum()

    safe_count = (
        products_df["Status"] == "Safe"
    ).sum()

else:

    expired_count = 0
    expiring_count = 0
    safe_count = 0


col1, col2, col3 = st.columns(3)

col1.metric("Expired Products", expired_count)
col2.metric("Expiring Soon", expiring_count)
col3.metric("Safe Products", safe_count)


# ==========================================
# 11. PRODUCT INVENTORY
# ==========================================

st.header("📋 Product Inventory")

if not products_df.empty:

    st.dataframe(
        products_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No products added yet.")


# ==========================================
# 12. EXPIRY ALERTS
# ==========================================

st.header("⚠️ Expiry Alerts")

if not products_df.empty:

    alerts = products_df[
        products_df["Status"].isin(
            ["Expired", "Expiring Soon"]
        )
    ]

    if not alerts.empty:

        st.dataframe(
            alerts,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No expiry alerts. All recorded products are safe."
        )

else:

    st.info("Add products to generate expiry alerts.")


st.divider()

st.caption(
    "StockWise AI | Expiry Management Prototype"
)
