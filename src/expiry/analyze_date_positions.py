


import json

image_name = "img_00003.jpg"

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

dates = []
markers = []

for annotation in data[image_name]["ann"]:

    x1, y1, x2, y2 = annotation["bbox"]

    center_y = (y1 + y2) / 2

    if annotation["cls"] == "date":
        dates.append({
            "text": annotation["transcription"],
            "center_y": center_y
        })

    elif annotation["cls"] in ["due", "prod"]:
        markers.append({
            "class": annotation["cls"],
            "center_y": center_y
        })

for date in dates:

    print("\nDate:", date["text"])

    for marker in markers:

        difference = abs(
            date["center_y"] - marker["center_y"]
        )

        print(
            f"Vertical difference from {marker['class']}: "
            f"{difference:.2f} pixels"
        )

print("\nAnalysis completed!")
