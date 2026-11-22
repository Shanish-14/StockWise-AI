








import easyocr
import cv2
from pathlib import Path

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
# 2. LOAD EASY OCR
# ==========================================

print("Loading EasyOCR model...")

reader = easyocr.Reader(["en"], gpu=False)


# ==========================================
# 3. LOAD IMAGE
# ==========================================

matches = list(DATASET_FOLDER.rglob(IMAGE_NAME))

if not matches:
    raise FileNotFoundError(
        f"Image not found: {IMAGE_NAME}"
    )

image_path = matches[0]

image = cv2.imread(str(image_path))

if image is None:
    raise ValueError("Could not load image.")

height, width = image.shape[:2]

print("\nImage loaded successfully!")
print("Image:", image_path)
print("Dimensions:", image.shape)


# ==========================================
# 4. DEFINE DATE REGIONS
# ==========================================

date_regions = {
    "top_date": (180, 840, 600, 895),
    "bottom_date": (180, 885, 600, 910)
}


# ==========================================
# 5. PROCESS EACH DATE REGION
# ==========================================

print("\nRunning OCR on separate date lines...")

for name, (x1, y1, x2, y2) in date_regions.items():

    print("\n" + "=" * 45)
    print(f"PROCESSING: {name.upper()}")
    print("=" * 45)

    # Keep crop coordinates inside image
    x1 = max(0, min(x1, width))
    x2 = max(0, min(x2, width))
    y1 = max(0, min(y1, height))
    y2 = max(0, min(y2, height))

    if x2 <= x1 or y2 <= y1:
        print("Invalid crop coordinates.")
        continue

    # Extract date line
    crop = image[y1:y2, x1:x2]

    # Save original crop
    original_path = (
        OUTPUT_FOLDER
        / f"img_00079_{name}_original.jpg"
    )

    cv2.imwrite(str(original_path), crop)

    # ======================================
    # 6. ENLARGE IMAGE
    # ======================================

    enlarged = cv2.resize(
        crop,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    # ======================================
    # 7. GRAYSCALE
    # ======================================

    gray = cv2.cvtColor(
        enlarged,
        cv2.COLOR_BGR2GRAY
    )

    # ======================================
    # 8. ADD WHITE BORDER
    # ======================================

    bordered = cv2.copyMakeBorder(
        gray,
        40,
        40,
        40,
        40,
        cv2.BORDER_CONSTANT,
        value=255
    )

    # ======================================
    # 9. SAVE PROCESSED IMAGE
    # ======================================

    processed_path = (
        OUTPUT_FOLDER
        / f"img_00079_{name}_processed.jpg"
    )

    cv2.imwrite(
        str(processed_path),
        bordered
    )

    # ======================================
    # 10. RUN OCR
    # ======================================

    results = reader.readtext(
        bordered,
        detail=1,
        paragraph=False,
        allowlist="0123456789./-:"
    )

    if not results:
        print("No text detected.")
        continue

    print("\nOCR RESULTS:")

    for bbox, text, confidence in results:

        print(
            f"Text: {text} | "
            f"Confidence: {confidence:.3f}"
        )


# ==========================================
# 11. COMPLETION
# ==========================================

print("\n" + "=" * 45)
print("EXPERIMENT COMPLETED!")
print("=" * 45)

print("\nOutput folder:")
print(OUTPUT_FOLDER)

print("\nGenerated files:")
print("- img_00079_top_date_original.jpg")
print("- img_00079_top_date_processed.jpg")
print("- img_00079_bottom_date_original.jpg")
print("- img_00079_bottom_date_processed.jpg")
