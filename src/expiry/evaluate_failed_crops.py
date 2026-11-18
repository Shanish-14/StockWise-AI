
import json
import os
import re
import cv2
import easyocr

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"
image_folder = "data/raw/expiry/Products-Real/evaluation/images"

failed_images = [
    "test_00002.jpg",
    "test_00008.jpg",
    "test_00011.jpg",
    "test_00013.jpg",
    "test_00014.jpg"
]

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

print("Loading EasyOCR...")
reader = easyocr.Reader(["en"], gpu=False)

correct = 0

for image_name in failed_images:

    image_path = os.path.join(image_folder, image_name)
    image = cv2.imread(image_path)

    annotations = data[image_name]["ann"]

    expiry = next(
        ann for ann in annotations if ann["cls"] == "exp"
    )

    x1, y1, x2, y2 = map(int, expiry["bbox"])

    cropped = image[y1:y2, x1:x2]

    detected_results = reader.readtext(cropped)

    detected_text = " ".join(result[1] for result in detected_results)

    actual = re.sub(r"[^a-zA-Z0-9]", "", expiry["transcription"]).lower()
    detected = re.sub(r"[^a-zA-Z0-9]", "", detected_text).lower()

    match = actual in detected

    if match:
        correct += 1

    print("\nImage:", image_name)
    print("Actual expiry:", expiry["transcription"])
    print("Cropped OCR:", detected_text)
    print("Match:", match)

    print("-" * 40)

print("\n========== CROPPED OCR RESULTS ==========")
print("Images tested:", len(failed_images))
print("Correct matches:", correct)
print("Incorrect matches:", len(failed_images) - correct)
print("Match rate:", round(correct / len(failed_images) * 100, 2), "%")
