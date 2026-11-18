

import json
from collections import Counter

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

class_counts = Counter()

for image_name, image_data in list(data.items())[:20]:

    for annotation in image_data["ann"]:
        class_counts[annotation["cls"]] += 1

print("ANNOTATION COUNTS IN FIRST 20 EVALUATION IMAGES")
print("=" * 50)

for class_name, count in class_counts.items():
    print(f"{class_name}: {count}")

print("\nInspection completed!")
