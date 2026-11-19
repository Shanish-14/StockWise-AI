

import easyocr
import re
import os
from datetime import datetime
from dateutil import parser


# ==========================================
# 1. DATE PARSING FUNCTION
# ==========================================

def parse_product_date(text):

    text = text.strip()

    # YYYY.MM.DD
    if re.fullmatch(r"\d{4}[./-]\d{1,2}[./-]\d{1,2}", text):
        for fmt in ("%Y.%m.%d", "%Y/%m/%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # YY.MM.DD
    if re.fullmatch(r"\d{2}[./-]\d{1,2}[./-]\d{1,2}", text):
        for fmt in ("%y.%m.%d", "%y/%m/%d", "%y-%m-%d"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # DD.MM.YYYY
    if re.fullmatch(r"\d{1,2}[./-]\d{1,2}[./-]\d{4}", text):
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # MM.YYYY
    if re.fullmatch(r"\d{1,2}[./-]\d{4}", text):
        for fmt in ("%m.%Y", "%m/%Y", "%m-%Y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # YYYY.MM
    if re.fullmatch(r"\d{4}[./-]\d{1,2}", text):
        for fmt in ("%Y.%m", "%Y/%m", "%Y-%m"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # Dates containing month names
    try:
        return parser.parse(text, dayfirst=True, fuzzy=False)
    except (ValueError, OverflowError):
        return None


# ==========================================
# 2. EXTRACT DATES FROM OCR TEXT
# ==========================================

def extract_dates(text):

    patterns = [
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{2}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b",
        r"\b\d{1,2}[./-]\d{4}\b",
        r"\b\d{4}[./-]\d{1,2}\b",
        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b",
        r"\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4}\b",
        r"\b[A-Za-z]{3,9}/\d{1,2}/\d{2,4}\b"
    ]

    found_dates = []

    for pattern in patterns:
        matches = re.findall(pattern, text)
        found_dates.extend(matches)

    # Remove shorter dates contained inside longer dates
    unique_dates = []

    for date in sorted(found_dates, key=len, reverse=True):

        if not any(date in existing for existing in unique_dates):
            unique_dates.append(date)

    return unique_dates


# ==========================================
# 3. SELECT PRODUCT IMAGE
# ==========================================

image_name = "img_00001.jpg"

image_path = os.path.join(
    "data/raw/expiry/Products-Real/train/images",
    image_name
)

if not os.path.exists(image_path):
    print("Image not found:", image_path)
    raise SystemExit


# ==========================================
# 4. LOAD EASYOCR
# ==========================================

print("Loading EasyOCR model...")

reader = easyocr.Reader(["en"], gpu=False)


# ==========================================
# 5. READ PRODUCT IMAGE
# ==========================================

print("\nProcessing image:", image_name)

results = reader.readtext(image_path)

detected_text = []

for result in results:
    detected_text.append(result[1])

full_text = " ".join(detected_text)

print("\n========== OCR DETECTED TEXT ==========")

for text in detected_text:
    print(text)


# ==========================================
# 6. CHECK EXPIRY-RELATED KEYWORDS
# ==========================================

expiry_keywords = [
    "best before",
    "expiry",
    "expires",
    "expiration",
    "use by",
    "exp date"
]

lower_text = full_text.lower()

expiry_context_found = any(
    keyword in lower_text
    for keyword in expiry_keywords
)


# ==========================================
# 7. EXTRACT AND PARSE DATES
# ==========================================

date_candidates = extract_dates(full_text)

print("\n========== DATE DETECTION ==========")

today = datetime.now().date()

if not date_candidates:
    print("No dates detected.")

for date_text in date_candidates:

    parsed_date = parse_product_date(date_text)

    print("\nDetected text:", date_text)

    if parsed_date is None:
        print("Could not understand this date.")
        continue

    print(
        "Standard date:",
        parsed_date.strftime("%Y-%m-%d")
    )

    # Check if date contains only month and year
    month_only = (
        re.fullmatch(r"\d{1,2}[./-]\d{4}", date_text)
        or re.fullmatch(r"\d{4}[./-]\d{1,2}", date_text)
    )

    if month_only:
        print("Status: Month/year only - exact day unknown")

    elif not expiry_context_found:
        print("Status: Date found, but expiry is not confirmed")

    elif parsed_date.date() < today:
        print("Status: EXPIRED")

    else:
        print("Status: NOT EXPIRED")


# ==========================================
# 8. FINAL RESULT
# ==========================================

print("\n========== FINAL RESULT ==========")

if expiry_context_found:
    print("Expiry-related text found in the image.")
else:
    print("No clear expiry-related keyword found.")

print("\nAutomatic expiry detection test completed!")
