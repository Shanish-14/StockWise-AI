

import json
import re
import os
from paddleocr import PaddleOCR

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"
image_folder = "data/raw/expiry/Products-Real/evaluation/images"

with open(annotation_path, "r", encoding="utf-8") as file:
    annotations = json.load(file)

print("Loading PaddleOCR model...")

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    engine="paddle",
    enable_mkldnn=False
)

def normalize_date(text):
    return re.sub(r"[^A-Z0-9]", "", text.upper())

correct = 0
incorrect = 0
failed = 0

print("\nStarting PaddleOCR evaluation...\n")

for image_name, image_data in list(annotations.items())[:10]:

    actual_date = None

    for annotation in image_data["ann"]:
        if annotation["cls"] == "exp":
            actual_date = annotation["transcription"]
            break

    if not actual_date:
        continue

    image_path = os.path.join(image_folder, image_name)

    try:
        print(f"Processing {image_name}...", flush=True)
        results = ocr.predict(image_path)

        detected_text = ""

        for result in results:
            detected_text += " ".join(result["rec_texts"])

        match = (
            normalize_date(actual_date)
            in normalize_date(detected_text)
        )

        if match:
            correct += 1
        else:
            incorrect += 1

        print("Image:", image_name)
        print("Actual:", actual_date)
        print("Detected:", detected_text)
        print("Match:", match)
        print("-" * 50)

    except Exception as error:
        failed += 1
        print("Image:", image_name)
        print("OCR failed:", str(error))
        print("-" * 50)
        continue

processed = correct + incorrect

print("\n========== PADDLEOCR EVALUATION ==========")
print("Successfully processed:", processed)
print("Correct matches:", correct)
print("Incorrect matches:", incorrect)
print("Failed images:", failed)

accuracy = (correct / processed) * 100 if processed else 0

print("Exact substring match rate:", round(accuracy, 2), "%")
