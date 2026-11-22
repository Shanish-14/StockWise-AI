

import re
import easyocr
import cv2
import numpy as np

from pathlib import Path
from datetime import datetime

# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "expiry"
    / "Products-Real"
    / "evaluation"
    / "images"
    / "test_00079.jpg"
)

OUTPUT_DIR = PROJECT_ROOT / "reports" / "expiry_debug"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_IMAGE = OUTPUT_DIR / "img_00079_date_matching.jpg"


# ==================================================
# 2. INITIALIZE OCR
# ==================================================

print("Loading EasyOCR model...")

reader = easyocr.Reader(["en"], gpu=False)


# ==================================================
# 3. DATE PARSER
# ==================================================

def parse_date(text):

    text = text.strip()

    formats = [
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y.%m.%d",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d.%m.%y",
        "%d/%m/%y",
        "%d-%m-%y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def extract_date_candidates(text):

    patterns = [
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
    ]

    candidates = []

    for pattern in patterns:

        for match in re.finditer(pattern, text):

            raw_date = match.group()

            parsed_date = parse_date(raw_date)

            if parsed_date:

                candidates.append({
                    "text": raw_date,
                    "date": parsed_date
                })

    return candidates


# ==================================================
# 4. LABEL DETECTION
# ==================================================

EXPIRY_LABELS = [
    "best before",
    "expiry",
    "expires",
    "expiration",
    "use by",
    "consumir antes de",
]

MFG_LABELS = [
    "prod date",
    "production date",
    "mfg date",
    "mfd date",
    "manufacturing date",
    "date of manufacture",
    "fecha de produccion",
    "data de fabricacao",
]


def normalize(text):

    text = text.lower()

    text = re.sub(r"[^a-z0-9 ]", " ", text)

    return " ".join(text.split())


def classify_label(text):

    normalized = normalize(text)

    if any(label in normalized for label in EXPIRY_LABELS):
        return "EXPIRY"

    if any(label in normalized for label in MFG_LABELS):
        return "MANUFACTURING"

    return None


# ==================================================
# 5. LOAD IMAGE
# ==================================================

if not IMAGE_PATH.exists():

    raise FileNotFoundError(
        f"Image not found: {IMAGE_PATH}"
    )

image = cv2.imread(str(IMAGE_PATH))

if image is None:

    raise ValueError("Could not load image.")

print("\nImage loaded successfully.")


# ==================================================
# 6. RUN OCR
# ==================================================

results = reader.readtext(
    str(IMAGE_PATH),
    detail=1
)

print("OCR completed.")


# ==================================================
# 7. COLLECT LABELS AND DATES
# ==================================================

labels = []
date_candidates = []

for bbox, text, confidence in results:

    xs = [point[0] for point in bbox]
    ys = [point[1] for point in bbox]

    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)

    label_type = classify_label(text)

    if label_type:

        labels.append({
            "type": label_type,
            "text": text,
            "x": center_x,
            "y": center_y,
            "confidence": confidence
        })

    for candidate in extract_date_candidates(text):

        date_candidates.append({
            "text": candidate["text"],
            "date": candidate["date"],
            "x": center_x,
            "y": center_y,
            "ocr_confidence": confidence
        })


# ==================================================
# 8. DISPLAY DETECTIONS
# ==================================================

print("\n" + "=" * 55)
print("DETECTION SUMMARY")
print("=" * 55)

print("Labels detected:", len(labels))
print("Date candidates detected:", len(date_candidates))

print("\nDetected labels:")

for label in labels:

    print(
        label["type"],
        "|",
        label["text"],
        "| Position:",
        (round(label["x"]), round(label["y"]))
    )

print("\nDetected dates:")

for candidate in date_candidates:

    print(
        candidate["text"],
        "|",
        candidate["date"],
        "| Position:",
        (round(candidate["x"]), round(candidate["y"]))
    )


# ==================================================
# 9. MATCH DATES WITH LABELS
# ==================================================

MAX_DISTANCE = 300

matches = {
    "EXPIRY": None,
    "MANUFACTURING": None
}

used_candidates = set()

# Process the labels with the most explicit nearby text first.
for label in labels:

    best_candidate = None
    best_distance = float("inf")
    best_index = None

    for index, candidate in enumerate(date_candidates):

        if index in used_candidates:
            continue

        distance = np.sqrt(
            (label["x"] - candidate["x"]) ** 2
            +
            (label["y"] - candidate["y"]) ** 2
        )

        if distance < best_distance:

            best_distance = distance
            best_candidate = candidate
            best_index = index

    if (
        best_candidate is not None
        and best_distance <= MAX_DISTANCE
    ):

        current = matches[label["type"]]

        # Keep the closest match for each category.
        if (
            current is None
            or best_distance < current["distance"]
        ):

            matches[label["type"]] = {
                "label": label["text"],
                "date_text": best_candidate["text"],
                "date": best_candidate["date"],
                "distance": best_distance,
                "ocr_confidence": best_candidate["ocr_confidence"]
            }

            used_candidates.add(best_index)


# ==================================================
# 10. DISPLAY MATCHING RESULTS
# ==================================================

print("\n" + "=" * 55)
print("DATE MATCHING RESULTS")
print("=" * 55)

for category in ["MANUFACTURING", "EXPIRY"]:

    result = matches[category]

    if result is not None:

        print(f"\n{category} DATE")

        print("Label:", result["label"])

        print("Detected text:", result["date_text"])

        print("Parsed date:", result["date"])

        print(
            "Distance:",
            round(result["distance"], 2)
        )

        print(
            "OCR confidence:",
            round(result["ocr_confidence"], 3)
        )

    else:

        print(f"\n{category} DATE: NOT DETECTED")


# ==================================================
# 11. CHECK DATE LOGIC
# ==================================================

print("\n" + "=" * 55)
print("DATE VALIDATION")
print("=" * 55)

mfg = matches["MANUFACTURING"]
exp = matches["EXPIRY"]

if mfg is not None and exp is not None:

    if exp["date"] > mfg["date"]:

        print("Date order: VALID")

        print("Manufacturing date:", mfg["date"])

        print("Expiry date:", exp["date"])

    else:

        print("WARNING: Expiry date is not after manufacturing date.")

else:

    print("Cannot validate date order.")
    print("Both dates must be detected first.")


# ==================================================
# 12. CREATE DEBUG IMAGE
# ==================================================

debug_image = image.copy()

# Draw labels.
for label in labels:

    if label["type"] == "EXPIRY":
        color = (0, 255, 0)
    else:
        color = (255, 0, 0)

    cv2.circle(
        debug_image,
        (int(label["x"]), int(label["y"])),
        10,
        color,
        -1
    )

    cv2.putText(
        debug_image,
        label["type"],
        (int(label["x"]), int(label["y"]) - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )


# Draw date candidates.
for candidate in date_candidates:

    cv2.circle(
        debug_image,
        (int(candidate["x"]), int(candidate["y"])),
        8,
        (0, 255, 255),
        -1
    )


# Draw matched connections.
for category, result in matches.items():

    if result is None:
        continue

    label = next(
        (
            item for item in labels
            if item["text"] == result["label"]
            and item["type"] == category
        ),
        None
    )

    candidate = next(
        (
            item for item in date_candidates
            if item["text"] == result["date_text"]
            and item["date"] == result["date"]
        ),
        None
    )

    if label is not None and candidate is not None:

        cv2.line(
            debug_image,
            (int(label["x"]), int(label["y"])),
            (int(candidate["x"]), int(candidate["y"])),
            (255, 255, 0),
            2
        )


cv2.imwrite(
    str(OUTPUT_IMAGE),
    debug_image
)

print("\nDebug image saved:")
print(OUTPUT_IMAGE)

print("\nMatching process completed.")
