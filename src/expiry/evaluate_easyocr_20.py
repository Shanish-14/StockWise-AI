


import json
import os
import re
import easyocr

from datetime import datetime
from date_detector import extract_dates


# ==================================================
# 1. PATHS
# ==================================================

ANNOTATION_PATH = (
    "data/raw/expiry/Products-Real/evaluation/annotations.json"
)

IMAGE_FOLDER = (
    "data/raw/expiry/Products-Real/evaluation/images"
)

TOTAL_IMAGES = 20


# ==================================================
# 2. PARSE ACTUAL ANNOTATION
# ==================================================

def parse_actual_date(text):

    text = str(text).strip()

    formats = [
        "%Y.%m.%d",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%y",
        "%d-%m-%y",
        "%d/%m/%y"
    ]

    # Try complete dates first
    for fmt in formats:

        try:
            parsed = datetime.strptime(text, fmt).date()

            return {
                "type": "full",
                "date": parsed
            }

        except ValueError:
            continue

    # Handle MM.YYYY or MM/YYYY
    match = re.fullmatch(
        r"(\d{1,2})[./-](\d{4})",
        text
    )

    if match:

        month = int(match.group(1))
        year = int(match.group(2))

        if 1 <= month <= 12:

            return {
                "type": "month",
                "month": month,
                "year": year
            }

    # Handle YYYY.MM or YYYY/MM
    match = re.fullmatch(
        r"(\d{4})[./-](\d{1,2})",
        text
    )

    if match:

        year = int(match.group(1))
        month = int(match.group(2))

        if 1 <= month <= 12:

            return {
                "type": "month",
                "month": month,
                "year": year
            }

    return None


# ==================================================
# 3. COMPARE PREDICTION WITH ANNOTATION
# ==================================================

def compare_dates(actual, predicted):

    if actual["type"] == "full":

        return actual["date"] == predicted

    if actual["type"] == "month":

        return (
            actual["year"] == predicted.year
            and actual["month"] == predicted.month
        )

    return False


# ==================================================
# 4. LOAD ANNOTATIONS
# ==================================================

with open(
    ANNOTATION_PATH,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


# ==================================================
# 5. LOAD OCR
# ==================================================

print("Loading EasyOCR...")

reader = easyocr.Reader(
    ["en"],
    gpu=False
)


# ==================================================
# 6. EVALUATION
# ==================================================

correct = 0
incorrect = 0
not_detected = 0
total = 0
invalid_annotations = 0

print("\nStarting 20-image evaluation...\n")


for image_name, image_data in list(data.items())[:TOTAL_IMAGES]:

    image_path = os.path.join(
        IMAGE_FOLDER,
        image_name
    )

    if not os.path.exists(image_path):

        print("Image not found:", image_name)
        continue

    actual_dates = [
        ann["transcription"]
        for ann in image_data["ann"]
        if ann["cls"] == "exp"
    ]

    if not actual_dates:
        continue

    actual_text = actual_dates[0]

    actual = parse_actual_date(
        actual_text
    )

    if actual is None:

        invalid_annotations += 1

        print("Invalid annotation:", image_name, actual_text)

        continue

    total += 1

    # Run OCR
    ocr_results = reader.readtext(
        image_path
    )

    # Detect and rank dates
    candidates = extract_dates(
        ocr_results
    )

    print("\n" + "=" * 50)
    print("Image:", image_name)
    print("Actual expiry:", actual_text)

    if not candidates:

        not_detected += 1

        print("Predicted expiry: None")
        print("Result: NOT DETECTED")

        continue

    predicted = candidates[0]["date"]

    match = compare_dates(
        actual,
        predicted
    )

    print("Predicted expiry:", predicted)
    print("Detection score:", candidates[0]["score"])
    print(
        "OCR confidence:",
        round(candidates[0]["confidence"], 3)
    )

    if match:

        correct += 1

        print("Result: CORRECT")

    else:

        incorrect += 1

        print("Result: INCORRECT")

    print("-" * 50)


# ==================================================
# 7. FINAL RESULTS
# ==================================================

print("\n========== FINAL RESULTS ==========")

print("Total images evaluated:", total)
print("Correct predictions:", correct)
print("Incorrect predictions:", incorrect)
print("No date detected:", not_detected)
print("Invalid annotations:", invalid_annotations)

if total > 0:

    accuracy = correct / total * 100

    detection_rate = (
        (correct + incorrect) / total * 100
    )

    print(
        "\nExact/month match accuracy:",
        round(accuracy, 2),
        "%"
    )

    print(
        "Date detection rate:",
        round(detection_rate, 2),
        "%"
    )
