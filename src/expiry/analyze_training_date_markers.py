
import json
import os
import math

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)


def get_center(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def distance(box1, box2):
    x1, y1 = get_center(box1)
    x2, y2 = get_center(box2)

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


due_count = 0
prod_count = 0
no_marker_count = 0

print("Analyzing training annotations...\n")

shown = 0

for image_name, image_data in data.items():

    annotations = image_data["ann"]

    dates = [
        ann for ann in annotations
        if ann["cls"] == "date"
    ]

    due_markers = [
        ann for ann in annotations
        if ann["cls"] == "due"
    ]

    prod_markers = [
        ann for ann in annotations
        if ann["cls"] == "prod"
    ]

    for date in dates:

        date_text = date.get("transcription", "")
        date_box = date["bbox"]

        due_distance = min(
            [distance(date_box, marker["bbox"])
             for marker in due_markers],
            default=float("inf")
        )

        prod_distance = min(
            [distance(date_box, marker["bbox"])
             for marker in prod_markers],
            default=float("inf")
        )

        if due_distance == float("inf") and prod_distance == float("inf"):
            nearest = "NO MARKER"
            no_marker_count += 1

        elif due_distance < prod_distance:
            nearest = "DUE"
            due_count += 1

        else:
            nearest = "PROD"
            prod_count += 1

        if shown < 30:
            print("Image:", image_name)
            print("Date:", date_text)
            print("Nearest marker:", nearest)
            print("Due distance:", round(due_distance, 2))
            print("Prod distance:", round(prod_distance, 2))
            print("-" * 40)
            shown += 1


print("\n========== SUMMARY ==========")
print("Dates nearest to DUE:", due_count)
print("Dates nearest to PROD:", prod_count)
print("Dates with no marker:", no_marker_count)
print("Total dates analyzed:", due_count + prod_count + no_marker_count)
