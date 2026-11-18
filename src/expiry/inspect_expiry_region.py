
import json

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

image_name = "test_00001.jpg"

print("IMAGE:", image_name)

for annotation in data[image_name]["ann"]:

    if annotation["cls"] == "exp":

        print("\nExpiry Date:", annotation["transcription"])
        print("Bounding Box:", annotation["bbox"])
        print("Date Components:", annotation.get("dmy_ann"))
