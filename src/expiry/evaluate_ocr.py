
import json
import easyocr
import os
import re
from datetime import datetime

# Dataset paths
image_folder = "data/raw/expiry/Products-Real/evaluation/images"
annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

# Load annotations
with open(annotation_path, "r", encoding="utf-8") as file:
    annotations = json.load(file)

# Load OCR model
print("Loading EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)

def normalize_date(text):
    return re.sub(r'[^A-Z0-9]', '', text.upper())

# Evaluation
total = 0
correct = 0
results = []

print("\nStarting OCR evaluation...")

for image_name, image_data in list(annotations.items())[:20]:

    image_path = os.path.join(image_folder, image_name)

    if not os.path.exists(image_path):
        continue

    # Get actual expiry date from exp annotation
    actual_dates = [
        ann["transcription"]
        for ann in image_data["ann"]
        if ann["cls"] == "exp"
    ]

    if not actual_dates:
        continue

    actual_date = actual_dates[0]

    # Read image using OCR
    ocr_results = reader.readtext(image_path)

    detected_text = " ".join([item[1] for item in ocr_results])

    # Compare normalized text
    normalized_actual = normalize_date(actual_date)
    normalized_detected = normalize_date(detected_text)

    total += 1

    if normalized_actual in normalized_detected:
        correct += 1
        status = "Correct"
    else:
        status = "Incorrect"

    results.append({
        "image": image_name,
        "actual_date": actual_date,
        "detected_text": detected_text,
        "status": status
    })

    if total % 50 == 0:
        print(f"Processed {total} images...")

# Final results
accuracy = (correct / total) * 100 if total > 0 else 0

print("\n========== OCR EVALUATION ==========")
print("Total images:", total)
print("Correct detections:", correct)
print("Incorrect detections:", total - correct)
print(f"OCR Accuracy: {accuracy:.2f}%")

# Save results
os.makedirs("reports", exist_ok=True)

with open("reports/ocr_evaluation_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\nResults saved to reports/ocr_evaluation_results.json")
