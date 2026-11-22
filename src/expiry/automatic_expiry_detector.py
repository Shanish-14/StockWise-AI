


import re
import argparse
from pathlib import Path
from datetime import datetime, date

import easyocr


# --------------------------------------------------
# 1. DATE PATTERNS
# --------------------------------------------------

DATE_PATTERNS = [
    r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
    r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b",
    r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2}\b",
    r"\b\d{1,2}[./-]\d{4}\b",
    r"\b\d{4}[./-]\d{1,2}\b",
]

DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%d-%m-%y",
    "%d/%m/%y",
    "%d.%m.%y",
    "%m-%Y",
    "%m/%Y",
    "%m.%Y",
    "%Y-%m",
    "%Y/%m",
    "%Y.%m",
]


# --------------------------------------------------
# 2. PARSE PRODUCT DATE
# --------------------------------------------------

def parse_product_date(date_text):

    date_text = date_text.strip()

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(
                date_text,
                fmt
            ).date()

        except ValueError:
            continue

    return None


# --------------------------------------------------
# 3. EXTRACT DATES FROM OCR TEXT
# --------------------------------------------------

def extract_dates(ocr_results):

    found_dates = []

    for result in ocr_results:

        text = result[1]

        for pattern in DATE_PATTERNS:

            matches = re.findall(
                pattern,
                text
            )

            found_dates.extend(matches)

    # Remove duplicate matches
    found_dates = list(set(found_dates))

    # IMPORTANT:
    # Keep longer dates before shorter dates.
    # Example:
    # 2025/01/28 is kept.
    # 2025/01 is removed because it is part
    # of the complete date.

    sorted_dates = sorted(
        found_dates,
        key=len,
        reverse=True
    )

    unique_dates = []

    for current_date in sorted_dates:

        if not any(
            current_date in existing
            for existing in unique_dates
        ):

            unique_dates.append(current_date)

    return unique_dates


# --------------------------------------------------
# 4. CHECK EXPIRY STATUS
# --------------------------------------------------

def check_expiry_status(expiry_date):

    today = date.today()

    remaining_days = (
        expiry_date - today
    ).days

    if remaining_days < 0:

        status = "EXPIRED"

    elif remaining_days <= 30:

        status = "EXPIRING SOON"

    else:

        status = "SAFE"

    return status, remaining_days


# --------------------------------------------------
# 5. MAIN OCR DETECTOR
# --------------------------------------------------

def detect_expiry_date(image_path):

    image_path = Path(image_path)

    if not image_path.exists():

        print("ERROR: Image not found.")
        print(image_path)

        return

    print("\nLoading EasyOCR model...")

    reader = easyocr.Reader(
        ["en"],
        gpu=False
    )

    print("Reading image...")

    ocr_results = reader.readtext(
        str(image_path)
    )

    print("\nRAW OCR TEXT")

    for result in ocr_results:

        print(
            result[1],
            "| Confidence:",
            round(result[2], 3)
        )

    # Extract dates
    detected_dates = extract_dates(
        ocr_results
    )

    print("\nDETECTED DATES")

    if not detected_dates:

        print("No date detected.")
        return

    valid_dates = []

    for detected_date in detected_dates:

        parsed_date = parse_product_date(
            detected_date
        )

        if parsed_date is not None:

            valid_dates.append(
                (detected_date, parsed_date)
            )

    if not valid_dates:

        print("No valid date found.")
        return

    for original_date, parsed_date in valid_dates:

        status, remaining_days = check_expiry_status(
            parsed_date
        )

        print("\n------------------------------")

        print(
            "Detected date:",
            original_date
        )

        print(
            "Standard date:",
            parsed_date.strftime("%Y-%m-%d")
        )

        print(
            "Expiry status:",
            status
        )

        print(
            "Days remaining:",
            remaining_days
        )

        print("------------------------------")


# --------------------------------------------------
# 6. RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Automatic expiry date detector"
    )

    parser.add_argument(
        "image",
        help="Path to product image"
    )

    args = parser.parse_args()

    detect_expiry_date(args.image)
