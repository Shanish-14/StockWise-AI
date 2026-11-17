
import json
import re
import os
from paddleocr import PaddleOCR

# File paths
annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"
image_folder = "data/raw/expiry/Products-Real/evaluation/images"

# Load annotations
with open(annotation_path, "r", encoding="utf-8") as file:
    annotations = json.load(file)

# Initialize PaddleOCR
print("Loading PaddleOCR model...")

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    engine="paddle",
    enable_mkldnn=False
)

# Normalize dates for comparison
def normalize_date(text):
    return re.sub(r"[^A-Z0-9]", "", text.upper())

correct = 0
total = 0

print("\nStarting PaddleOCR evaluation...\n")

# Test first 20 annotated images
for image_name, image_data in list(annotations.items())[:20]:

    # Get actual expiry date
    actual_date = None

    for annotation in image_data["ann"]:
        if annotation["cls"] == "exp":
            actual_date = annotation["transcription"]
            break

    if not actual_date:
        continue

    image_path = os.path.join(image_folder, image_name)

    # Run OCR
    results = ocr.predict(image_path)

    detected_text = ""

    for result in results:
        detected_text += " ".join(result["rec_texts"])

    # Compare actual and detected dates
    actual_normalized = normalize_date(actual_date)
    detected_normalized = normalize_date(detected_text)

    match = actual_normalized in detected_normalized

    if match:
        correct += 1

    total += 1

    print("Image:", image_name)
    print("Actual:", actual_date)
    print("Detected:", detected_text)
    print("Match:", match)
    print("-" * 50)

# Final results
accuracy = (correct / total) * 100 if total else 0

print("\n========== PADDLEOCR EVALUATION ==========")
print("Total images tested:", total)
print("Correct matches:", correct)
print("Incorrect matches:", total - correct)
print("Exact substring match rate:", round(accuracy, 2), "%")
