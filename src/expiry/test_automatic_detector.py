
import easyocr
import re
import os
from datetime import datetime
from dateutil import parser


# ==========================================
# 1. DATE EXTRACTION
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
    ]

    found_dates = []

    for pattern in patterns:
        found_dates.extend(re.findall(pattern, text))

    unique_dates = []

    for date in sorted(found_dates, key=len, reverse=True):
        if not any(date in existing for existing in unique_dates):
            unique_dates.append(date)

    return unique_dates


# ==========================================
# 2. DATE PARSING
# ==========================================

def parse_product_date(text):

    try:
        return parser.parse(
            text,
            dayfirst=True,
            fuzzy=False
        )
    except (ValueError, OverflowError):
        return None


# ==========================================
# 3. SETTINGS
# ==========================================

image_folder = os.path.join(
    "data",
    "raw",
    "expiry",
    "Products-Real",
    "train",
    "images"
)

image_names = [
    f"img_{i:05d}.jpg"
    for i in range(1, 11)
]

expiry_keywords = [
    "best before",
    "expiry",
    "expires",
    "expiration",
    "use by",
    "exp date"
]


# ==========================================
# 4. LOAD OCR MODEL ONCE
# ==========================================

print("Loading EasyOCR model...")

reader = easyocr.Reader(["en"], gpu=False)

print("EasyOCR loaded successfully!")


# ==========================================
# 5. PROCESS 10 IMAGES
# ==========================================

total_images = 0
images_with_dates = 0
images_with_keywords = 0

for image_name in image_names:

    image_path = os.path.join(
        image_folder,
        image_name
    )

    if not os.path.exists(image_path):
        print("\nImage not found:", image_name)
        continue

    total_images += 1

    print("\n" + "=" * 55)
    print("PROCESSING:", image_name)
    print("=" * 55)

    results = reader.readtext(image_path)

    detected_text = [
        result[1] for result in results
    ]

    full_text = " ".join(detected_text)

    print("\nOCR TEXT:")

    for text in detected_text:
        print("-", text)

    # Check expiry-related keywords
    lower_text = full_text.lower()

    found_keywords = [
        keyword
        for keyword in expiry_keywords
        if keyword in lower_text
    ]

    # Extract dates
    date_candidates = extract_dates(full_text)

    print("\nEXPIRY KEYWORDS:")

    if found_keywords:
        images_with_keywords += 1
        print(found_keywords)
    else:
        print("No expiry keyword detected.")

    print("\nDATE CANDIDATES:")

    if date_candidates:
        images_with_dates += 1

        for date_text in date_candidates:

            parsed_date = parse_product_date(date_text)

            if parsed_date:
                print(
                    date_text,
                    "->",
                    parsed_date.strftime("%Y-%m-%d")
                )
            else:
                print(
                    date_text,
                    "-> Could not parse"
                )

    else:
        print("No date detected.")

    # Do not automatically assign expiry status.
    # A keyword and date may refer to different parts
    # of the product label.

    if found_keywords and date_candidates:
        print("\nRESULT: Keyword and date both detected.")
    elif date_candidates:
        print("\nRESULT: Date detected, expiry not confirmed.")
    elif found_keywords:
        print("\nRESULT: Expiry keyword detected, no date found.")
    else:
        print("\nRESULT: No expiry information detected.")


# ==========================================
# 6. FINAL SUMMARY
# ==========================================

print("\n" + "=" * 55)
print("10-IMAGE TEST SUMMARY")
print("=" * 55)

print("Images processed:", total_images)
print("Images with date candidates:", images_with_dates)
print("Images with expiry keywords:", images_with_keywords)

print("\nTesting completed!")
