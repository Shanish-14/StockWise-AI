
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

reader = easyocr.Reader(["en"], gpu=False)

correct = 0

for image_name in failed_images:

    image_path = os.path.join(image_folder, image_name)
    image = cv2.imread(image_path)

    expiry = next(
        ann for ann in data[image_name]["ann"]
        if ann["cls"] == "exp"
    )

    x1, y1, x2, y2 = map(int, expiry["bbox"])

    cropped = image[y1:y2, x1:x2]

    # Enlarge the date region
    enlarged = cv2.resize(
        cropped,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve contrast
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)

    enhanced = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    ).apply(gray)

    results = reader.readtext(
        enhanced,
        detail=0
    )

    detected_text = " ".join(results)

    normalize = lambda text: re.sub(
        r"[^a-zA-Z0-9]", "", text
    ).lower()

    actual = normalize(expiry["transcription"])
    detected = normalize(detected_text)

    match = actual in detected

    if match:
        correct += 1

    print("\nImage:", image_name)
    print("Actual:", expiry["transcription"])
    print("Enhanced OCR:", detected_text)
    print("Match:", match)

print("\n========== ENHANCED OCR RESULTS ==========")
print("Correct:", correct)
print("Incorrect:", len(failed_images) - correct)
print("Match rate:", round(correct / len(failed_images) * 100, 2), "%")
