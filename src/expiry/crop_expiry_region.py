
import json
import cv2
import os

image_name = "test_00001.jpg"

image_path = os.path.join(
    "data/raw/expiry/Products-Real/evaluation/images",
    image_name
)

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

image = cv2.imread(image_path)

for annotation in data[image_name]["ann"]:

    if annotation["cls"] == "exp":

        x1, y1, x2, y2 = annotation["bbox"]

        cropped = image[y1:y2, x1:x2]

        os.makedirs("reports", exist_ok=True)

        output_path = "reports/expiry_date_crop.jpg"

        cv2.imwrite(output_path, cropped)

        print("Actual expiry date:", annotation["transcription"])
        print("Cropped image saved:", output_path)

        break
