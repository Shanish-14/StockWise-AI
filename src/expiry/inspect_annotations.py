

import json
from collections import Counter

annotation_path = "data/raw/expiry/Products-Real/evaluation/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

class_counts = Counter()
expiry_examples = []

for image_name, image_data in data.items():

    for annotation in image_data["ann"]:

        class_name = annotation["cls"]
        class_counts[class_name] += 1

        if class_name == "exp":
            expiry_examples.append({
                "image": image_name,
                "date": annotation["transcription"]
            })

print("========== ANNOTATION SUMMARY ==========")

print("\nClass counts:")
for class_name, count in class_counts.items():
    print(class_name, ":", count)

print("\nTotal expiry dates:", len(expiry_examples))

print("\nFirst 10 expiry examples:")
for item in expiry_examples[:10]:
    print(item["image"], ":", item["date"])
