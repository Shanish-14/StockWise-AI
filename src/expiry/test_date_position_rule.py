
import json

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

checked = 0

for image_name, image_data in data.items():

    dates = []
    markers = []

    for annotation in image_data["ann"]:

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

    if len(dates) >= 2 and any(m["class"] == "due" for m in markers) and any(m["class"] == "prod" for m in markers):

        print("\nImage:", image_name)

        for date in dates:

            due_distance = min(
                abs(date["center_y"] - m["center_y"])
                for m in markers if m["class"] == "due"
            )

            prod_distance = min(
                abs(date["center_y"] - m["center_y"])
                for m in markers if m["class"] == "prod"
            )

            nearest = "DUE" if due_distance < prod_distance else "PROD"

            print("Date:", date["text"])
            print("Nearest marking:", nearest)

        checked += 1

        if checked == 20:
            break

print("\nImages checked:", checked)
