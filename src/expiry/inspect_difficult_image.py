
import json

image_name = "img_00069.jpg"

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

print("IMAGE:", image_name)
print("=" * 50)

for annotation in data[image_name]["ann"]:

    x1, y1, x2, y2 = annotation["bbox"]

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    print("Class:", annotation["cls"])
    print("Text:", annotation.get("transcription", "Not available"))
    print("Center X:", round(center_x, 2))
    print("Center Y:", round(center_y, 2))
    print("Bounding box:", annotation["bbox"])
    print("-" * 40)

print("Inspection completed!")
