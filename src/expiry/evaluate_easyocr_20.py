
import json
import os
import re
import easyocr

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"
image_folder = "data/raw/expiry/Products-Real/evaluation/images"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

print("Loading EasyOCR...")
reader = easyocr.Reader(["en"], gpu=False)

correct = 0
total = 0

for image_name, image_data in list(data.items())[:20]:

    image_path = os.path.join(image_folder, image_name)

    actual_dates = [
        ann["transcription"]
        for ann in image_data["ann"]
        if ann["cls"] == "exp"
    ]

    if not actual_dates:
        continue

    results = reader.readtext(image_path)

    detected_text = " ".join(result[1] for result in results)

    def normalize(text):
        return re.sub(r"[^a-zA-Z0-9]", "", text).lower()

    actual = normalize(actual_dates[0])
    detected = normalize(detected_text)

    match = actual in detected

    if match:
        correct += 1

    total += 1

    print("\nImage:", image_name)
    print("Actual expiry:", actual_dates[0])
    print("OCR detected:", detected_text)
    print("Match:", match)
    if not match:
     print("FAILED IMAGE:", image_name)

    print("-" * 40)

print("\n========== FINAL RESULTS ==========")
print("Total images:", total)
print("Correct matches:", correct)
print("Incorrect matches:", total - correct)

if total > 0:
    print("Match rate:", round(correct / total * 100, 2), "%")
