

import cv2
from pathlib import Path
import easyocr

# ==========================================
# PATHS
# ==========================================

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

# ==========================================
# LOAD IMAGE
# ==========================================

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(IMAGE_PATH)

height, width = image.shape[:2]

print("Image dimensions:", width, "x", height)

# ==========================================
# OCR
# ==========================================

reader = easyocr.Reader(["en"], gpu=False)

# ==========================================
# SMALL DATE REGIONS
# ==========================================

regions = {
    "expiry_date": (180, 840, 550, 905),
    "manufacturing_date": (180, 890, 550, 950)
}

# ==========================================
# PROCESS
# ==========================================

for name, (x1, y1, x2, y2) in regions.items():

    crop = image[y1:y2, x1:x2]

    # Enlarge 5 times.
    enlarged = cv2.resize(
        crop,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    # Grayscale.
    gray = cv2.cvtColor(
        enlarged,
        cv2.COLOR_BGR2GRAY
    )

    # Improve contrast.
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Add white border.
    bordered = cv2.copyMakeBorder(
        enhanced,
        40, 40, 40, 40,
        cv2.BORDER_CONSTANT,
        value=255
    )

    # Save crop.
    output_path = OUTPUT_DIR / f"{name}.jpg"

    cv2.imwrite(str(output_path), bordered)

    # OCR.
    results = reader.readtext(
        bordered,
        detail=1,
        allowlist="0123456789./-"
    )

    print("\n" + "=" * 45)
    print(name.upper())
    print("=" * 45)

    for bbox, text, confidence in results:

        print(
            "Text:", text,
            "| Confidence:", round(confidence, 3)
        )

    print("Saved:", output_path)

print("\nCompleted.")
