


import json
import re
from datetime import datetime
from dateutil import parser


# FUNCTION TO UNDERSTAND DIFFERENT DATE FORMATS
def parse_product_date(text):

    text = text.strip()

    # Format: 2021.08.03
    if re.fullmatch(r"\d{4}[./-]\d{1,2}[./-]\d{1,2}", text):
        for fmt in ("%Y.%m.%d", "%Y/%m/%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # Format: 21.05.26
    if re.fullmatch(r"\d{2}[./-]\d{1,2}[./-]\d{1,2}", text):
        for fmt in ("%y.%m.%d", "%y/%m/%d", "%y-%m-%d"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # Format: 23.07.2022
    if re.fullmatch(r"\d{1,2}[./-]\d{1,2}[./-]\d{4}", text):
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # Format: 02.2023
    if re.fullmatch(r"\d{1,2}[./-]\d{4}", text):
        for fmt in ("%m.%Y", "%m/%Y", "%m-%Y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # Format: 2022.04
    if re.fullmatch(r"\d{4}[./-]\d{1,2}", text):
        for fmt in ("%Y.%m", "%Y/%m", "%Y-%m"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

    # Formats containing month names
    try:
        return parser.parse(text, dayfirst=True, fuzzy=False)
    except (ValueError, OverflowError):
        return None


# LOAD TRAINING DATASET
annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)


# TEST ALL DATE ANNOTATIONS
total = 0
parsed = 0
failed = []

for image_name, image_data in data.items():

    for ann in image_data["ann"]:

        if ann["cls"] == "date":

            date_text = ann.get("transcription", "").strip()

            if not date_text:
                continue

            total += 1

            result = parse_product_date(date_text)

            if result is not None:
                parsed += 1
            else:
                failed.append((image_name, date_text))


# DISPLAY RESULTS
print("\n========== FULL DATASET PARSER RESULTS ==========")

print("Total dates:", total)
print("Successfully parsed:", parsed)
print("Failed:", len(failed))

accuracy = (parsed / total) * 100 if total else 0

print("Parsing success rate:", round(accuracy, 2), "%")

print("\n========== FAILED DATE EXAMPLES ==========")

for image_name, date_text in failed[:20]:
    print(image_name, "->", date_text)
