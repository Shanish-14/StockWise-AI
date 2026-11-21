
from pathlib import Path
from datetime import datetime
import re
import easyocr

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "expiry"
    / "Products-Real"
    / "train"
    / "images"
)

IMAGE_NAMES = [
    "img_00065.jpg",
    "img_00079.jpg"
]

# --------------------------------------------------
# KEYWORDS
# --------------------------------------------------

EXPIRY_KEYWORDS = [
    "BEST BEFORE",
    "EXPIRY DATE",
    "EXPIRY",
    "EXPIRES",
    "USE BY",
    "BBE"
]

MANUFACTURING_KEYWORDS = [
    "PRODUCTION DATE",
    "PROD DATE",
    "MANUFACTURING DATE",
    "MANUFACTURED",
    "MANUFACTURE DATE",
    "MFG",
    "MFD",
    "PACKED ON",
    "PKD"
]

# --------------------------------------------------
# DATE EXTRACTION
# --------------------------------------------------

DATE_PATTERN = re.compile(
    r"\b(?:"
    r"\d{4}[./-]\d{1,2}[./-]\d{1,2}"
    r"|"
    r"\d{1,2}[./-]\d{1,2}[./-]\d{4}"
    r")\b"
)


def parse_date(date_text):

    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt).date()
        except ValueError:
            continue

    return None


def find_keyword_type(text):

    text = text.upper()

    for keyword in EXPIRY_KEYWORDS:
        if keyword in text:
            return "EXPIRY"

    for keyword in MANUFACTURING_KEYWORDS:
        if keyword in text:
            return "MANUFACTURING"

    return None


# --------------------------------------------------
# OCR PROCESSING
# --------------------------------------------------

def process_image(reader, image_path):

    print("\n" + "=" * 60)
    print(f"IMAGE: {image_path.name}")
    print("=" * 60)

    results = reader.readtext(
        str(image_path),
        detail=1,
        paragraph=False
    )

    date_candidates = []
    keyword_candidates = []

    # Read OCR results
    for result in results:

        bbox, text, confidence = result

        text = text.strip()

        # Calculate bounding-box centre
        center_x = sum(point[0] for point in bbox) / 4
        center_y = sum(point[1] for point in bbox) / 4

        # Check whether this OCR text contains a date
        matches = DATE_PATTERN.findall(text)

        for match in matches:

            parsed = parse_date(match)

            if parsed is not None:

                date_candidates.append({
                    "text": match,
                    "date": parsed,
                    "x": center_x,
                    "y": center_y,
                    "confidence": confidence,
                    "line": text
                })

        # Check whether this OCR text contains a keyword
        keyword_type = find_keyword_type(text)

        if keyword_type:

            keyword_candidates.append({
                "type": keyword_type,
                "text": text,
                "x": center_x,
                "y": center_y
            })

    # --------------------------------------------------
    # DISPLAY DETECTED KEYWORDS
    # --------------------------------------------------

    print("\nDetected keywords:")

    if keyword_candidates:

        for item in keyword_candidates:
            print(
                f"  {item['type']}: {item['text']}"
            )

    else:
        print("  No manufacturing or expiry keywords found.")

    # --------------------------------------------------
    # DISPLAY DATE CANDIDATES
    # --------------------------------------------------

    print("\nDetected dates:")

    if date_candidates:

        for item in date_candidates:
            print(
                f"  {item['text']} "
                f"| Confidence: {item['confidence']:.2f}"
            )

    else:
        print("  No valid dates found.")

    # --------------------------------------------------
    # ASSOCIATE DATES WITH KEYWORDS
    # --------------------------------------------------

    assigned = {
        "MANUFACTURING": [],
        "EXPIRY": []
    }

    unassigned = []

    for date_item in date_candidates:

        # First, check if the date and keyword
        # occur in the same OCR text line.
        direct_type = find_keyword_type(date_item["line"])

        if direct_type:

            assigned[direct_type].append(date_item)
            continue

        # Otherwise, find the nearest keyword.
        nearest_keyword = None
        nearest_distance = float("inf")

        for keyword_item in keyword_candidates:

            dx = date_item["x"] - keyword_item["x"]
            dy = date_item["y"] - keyword_item["y"]

            # Vertical distance gets slightly more weight.
            distance = (dx ** 2 + (dy * 1.5) ** 2) ** 0.5

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_keyword = keyword_item

        # Associate only when the keyword is nearby.
        if nearest_keyword and nearest_distance < 350:

            assigned[nearest_keyword["type"]].append(date_item)

        else:

            unassigned.append(date_item)

    # --------------------------------------------------
    # FINAL RESULTS
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("FINAL DATE CLASSIFICATION")
    print("-" * 60)

    for category in ["MANUFACTURING", "EXPIRY"]:

        print(f"\n{category} DATE:")

        if assigned[category]:

            for item in assigned[category]:

                print(
                    f"  {item['date']} "
                    f"(OCR confidence: {item['confidence']:.2f})"
                )

        else:

            print("  Not detected")

    print("\nUNASSIGNED DATES:")

    if unassigned:

        for item in unassigned:
            print(f"  {item['date']}")

    else:
        print("  None")


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print("Loading EasyOCR model...")

    reader = easyocr.Reader(["en"], gpu=False)

    for image_name in IMAGE_NAMES:

        image_path = IMAGE_FOLDER / image_name

        if not image_path.exists():

            print(f"\nImage not found: {image_path}")
            continue

        try:

            process_image(reader, image_path)

        except Exception as error:

            print(f"Error processing {image_name}: {error}")

    print("\n" + "=" * 60)
    print("TESTING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
