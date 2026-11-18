
import easyocr
import json
import os
import re

print("Loading EasyOCR model...", flush=True)

reader = easyocr.Reader(['en'], gpu=False)

image_folder = "data/raw/expiry/Products-Real/evaluation/images"
annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    annotations = json.load(file)

correct = 0
incorrect = 0
failed = 0

print("\nStarting EasyOCR evaluation...\n", flush=True)

for image_name in list(annotations.keys())[:10]:

    image_path = os.path.join(image_folder, image_name)

    actual_date = ""

    for ann in annotations[image_name]["ann"]:
        if ann["cls"] == "exp":
            actual_date = ann["transcription"]
            break

    try:
        print(f"Processing {image_name}...", flush=True)

        results = reader.readtext(image_path)

        detected_text = " ".join(
            result[1] for result in results
        )

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

print("\n========== EASYOCR EVALUATION ==========")
print("Successfully processed:", correct + incorrect)
print("Correct matches:", correct)
print("Incorrect matches:", incorrect)
print("Failed images:", failed)

total = correct + incorrect

if total > 0:
    print("Exact substring match rate:", round(correct / total * 100, 2), "%")
