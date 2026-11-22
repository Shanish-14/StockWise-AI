
import easyocr
import cv2
from pathlib import Path
import re

# ==========================================
# 1. PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "expiry"
    / "Products-Real"
)

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "reports"
    / "expiry_debug"
)

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

IMAGE_NAME = "img_00079.jpg"


# ==========================================
# 2. LABEL KEYWORDS
# ==========================================

EXPIRY_LABELS = [
    "BEST BEFORE",
    "BEST BEFOR",
    "EXPIRY",
    "EXP DATE",
    "EXP DATE",
    "USE BY",
    "CONSUMIR ANTES DE"
]

MANUFACTURING_LABELS = [
    "PROD DATE",
    "PRODUCTION DATE",
    "PROD. DATE",
    "MFG DATE",
    "MFD DATE",
    "MANUFACTURE DATE",
    "MANUFACTURING DATE",
    "DATE OF MANUFACTURE",
    "FECHA DE PRODUCCION",
    "DATA DE FABRICACAO"
]


# ==========================================
# 3. TEXT NORMALIZATION
# ==========================================

def normalize_text(text):

    text = text.upper()

    text = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# 4. LOAD EASY OCR
# ==========================================

print("Loading EasyOCR model...")

reader = easyocr.Reader(
    ["en"],
    gpu=False
)


# ==========================================
# 5. LOAD IMAGE
# ==========================================

matches = list(
    DATASET_FOLDER.rglob(IMAGE_NAME)
)

if not matches:
    raise FileNotFoundError(
        f"Image not found: {IMAGE_NAME}"
    )

image_path = matches[0]

image = cv2.imread(str(image_path))

if image is None:
    raise ValueError("Could not load image.")

debug_image = image.copy()

print("\nImage loaded:", image_path)
print("Image dimensions:", image.shape)


# ==========================================
# 6. RUN OCR ON FULL IMAGE
# ==========================================

print("\nRunning OCR on full image...")

results = reader.readtext(
    str(image_path),
    detail=1,
    paragraph=False
)


# ==========================================
# 7. DETECT DATE LABELS
# ==========================================

detected_labels = []

for bbox, text, confidence in results:

    normalized = normalize_text(text)

    label_type = None

    # Check expiry labels
    for keyword in EXPIRY_LABELS:

        if normalize_text(keyword) in normalized:
            label_type = "EXPIRY"
            break

    # Check manufacturing labels
    if label_type is None:

        for keyword in MANUFACTURING_LABELS:

            if normalize_text(keyword) in normalized:
                label_type = "MANUFACTURING"
                break

    if label_type is None:
        continue

    points = [
        [int(point[0]), int(point[1])]
        for point in bbox
    ]

    x1 = min(point[0] for point in points)
    y1 = min(point[1] for point in points)
    x2 = max(point[0] for point in points)
    y2 = max(point[1] for point in points)

    detected_labels.append({
        "type": label_type,
        "text": text,
        "confidence": float(confidence),
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2
    })


# ==========================================
# 8. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 55)
print("AUTOMATIC DATE LABEL DETECTION")
print("=" * 55)

if not detected_labels:

    print("No date labels detected.")

else:

    for index, label in enumerate(
        detected_labels,
        start=1
    ):

        print(f"\nLabel {index}")
        print("Type:", label["type"])
        print("Text:", label["text"])

        print(
            "Confidence:",
            round(label["confidence"], 3)
        )

        print(
            "Coordinates:",
            (
                label["x1"],
                label["y1"],
                label["x2"],
                label["y2"]
            )
        )

        # Draw label box
        if label["type"] == "EXPIRY":
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        cv2.rectangle(
            debug_image,
            (label["x1"], label["y1"]),
            (label["x2"], label["y2"]),
            color,
            3
        )

        cv2.putText(
            debug_image,
            label["type"],
            (
                label["x1"],
                max(30, label["y1"] - 10)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )


# ==========================================
# 9. SAVE DEBUG IMAGE
# ==========================================

output_path = (
    OUTPUT_FOLDER
    / "img_00079_detected_labels.jpg"
)

cv2.imwrite(
    str(output_path),
    debug_image
)

print("\n" + "=" * 55)
print("DETECTION COMPLETED")
print("=" * 55)

print(
    "Expiry labels:",
    sum(
        1 for label in detected_labels
        if label["type"] == "EXPIRY"
    )
)

print(
    "Manufacturing labels:",
    sum(
        1 for label in detected_labels
        if label["type"] == "MANUFACTURING"
    )
)

print("\nDebug image saved:")
print(output_path)
