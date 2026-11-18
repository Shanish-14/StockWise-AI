
import easyocr
import json
import cv2
import os
import re

# 1. Load EasyOCR
print("Loading EasyOCR model...", flush=True)

reader = easyocr.Reader(['en'], gpu=False)

# 2. Dataset paths
image_folder = "data/raw/expiry/Products-Real/evaluation/images"

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

# 3. Load annotations
with open(annotation_path, "r", encoding="utf-8") as file:
    annotations = json.load(file)

correct = 0
incorrect = 0
failed = 0

print("\nStarting cropped-image evaluation...\n", flush=True)

# 4. Process first 10 images
for image_name in list(annotations.keys())[:10]:

    image_path = os.path.join(image_folder, image_name)

    actual_date = ""

    # Find actual expiry date and bounding box
    for ann in annotations[image_name]["ann"]:
        if ann["cls"] == "exp":
            actual_date = ann["transcription"]
            x1, y1, x2, y2 = ann["bbox"]
            break

    try:
        print(f"Processing {image_name}...", flush=True)

        # Read original image
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Could not read image")

        # Crop expiry-date region
        cropped = image[y1:y2, x1:x2]

        if cropped.size == 0:
            raise ValueError("Empty cropped image")

        # Run EasyOCR on cropped region
        results = reader.readtext(cropped)

        detected_text = " ".join(
            result[1] for result in results
        )

        # Normalize text for comparison
        normalized_actual = re.sub(
            r"[^A-Z0-9]", "", actual_date.upper()
        )

        normalized_detected = re.sub(
            r"[^A-Z0-9]", "", detected_text.upper()
        )

        match = normalized_actual in normalized_detected

        if match:
            correct += 1
        else:
            incorrect += 1

        print("Actual:", actual_date)
        print("Detected:", detected_text)
        print("Match:", match)
        print("-" * 50)

    except Exception as error:
        failed += 1
        print("Error:", error)

# 5. Final results
total = correct + incorrect

print("\n========== CROPPED EASYOCR RESULTS ==========")
print("Successfully processed:", total)
print("Correct matches:", correct)
print("Incorrect matches:", incorrect)
print("Failed images:", failed)

if total > 0:
    accuracy = (correct / total) * 100
    print("Exact substring match rate:", round(accuracy, 2), "%")
