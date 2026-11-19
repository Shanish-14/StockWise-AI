
import easyocr
import json
import os
import re


# ==========================================
# 1. FILE PATHS
# ==========================================

base_folder = "data/raw/expiry/Products-Real/train"

image_folder = os.path.join(
    base_folder,
    "images"
)

annotation_file = os.path.join(
    base_folder,
    "annotations.json"
)


# ==========================================
# 2. LOAD ANNOTATIONS
# ==========================================

print("Loading dataset annotations...")

with open(annotation_file, "r", encoding="utf-8") as file:
    annotations = json.load(file)

print("Annotations loaded successfully!")


# ==========================================
# 3. SELECT IMAGES WITH DATE ANNOTATIONS
# ==========================================

test_images = []

for image_name, image_data in sorted(annotations.items()):

    date_annotations = [
        item
        for item in image_data.get("ann", [])
        if item.get("cls") == "date"
        and item.get("transcription", "").strip()
    ]

    image_path = os.path.join(
        image_folder,
        image_name
    )

    if date_annotations and os.path.exists(image_path):

        test_images.append(
            (image_name, date_annotations)
        )

    if len(test_images) == 20:
        break


print("\nImages selected:", len(test_images))


# ==========================================
# 4. TEXT NORMALIZATION
# ==========================================

def normalize_text(text):

    text = str(text).lower()

    # Remove spaces and punctuation
    text = re.sub(r"[^a-z0-9]", "", text)

    return text


# ==========================================
# 5. LOAD EASYOCR
# ==========================================

print("\nLoading EasyOCR model...")

reader = easyocr.Reader(
    ["en"],
    gpu=False
)

print("EasyOCR loaded successfully!")


# ==========================================
# 6. EVALUATION
# ==========================================

total_dates = 0
matched_dates = 0
failed_dates = 0

for image_name, date_annotations in test_images:

    image_path = os.path.join(
        image_folder,
        image_name
    )

    print("\n" + "=" * 55)
    print("IMAGE:", image_name)
    print("=" * 55)

    # Run OCR
    results = reader.readtext(image_path)

    detected_text = [
        result[1]
        for result in results
    ]

    full_text = " ".join(detected_text)

    normalized_ocr = normalize_text(full_text)

    print("\nOCR detected text:")

    for text in detected_text:
        print("-", text)

    print("\nGROUND TRUTH vs OCR:")

    for annotation in date_annotations:

        ground_truth = annotation["transcription"].strip()

        normalized_gt = normalize_text(ground_truth)

        total_dates += 1

        if normalized_gt and normalized_gt in normalized_ocr:

            matched_dates += 1

            print(
                "[MATCH]",
                ground_truth
            )

        else:

            failed_dates += 1

            print(
                "[NOT MATCHED]",
                ground_truth
            )


# ==========================================
# 7. FINAL RESULTS
# ==========================================

print("\n" + "=" * 55)
print("OCR EVALUATION SUMMARY")
print("=" * 55)

print("Images evaluated:", len(test_images))
print("Total annotated dates:", total_dates)
print("Matched dates:", matched_dates)
print("Unmatched dates:", failed_dates)

if total_dates > 0:

    accuracy = (
        matched_dates / total_dates
    ) * 100

    print(
        f"Date recognition rate: {accuracy:.2f}%"
    )

print("\nEvaluation completed!")
