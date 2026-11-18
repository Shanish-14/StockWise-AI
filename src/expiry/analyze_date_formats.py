
import json
import re
from collections import Counter

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

formats = Counter()

for image_name, image_data in data.items():

    for ann in image_data["ann"]:

        if ann["cls"] != "date":
            continue

        date_text = ann.get("transcription", "").strip()

        if not date_text:
            continue

        if re.search(r"[A-Za-z]", date_text):
            category = "Contains month name"

        elif "/" in date_text:
            category = "Slash separated"

        elif "." in date_text:
            category = "Dot separated"

        elif "-" in date_text:
            category = "Hyphen separated"

        else:
            category = "Other format"

        formats[category] += 1


print("========== DATE FORMAT ANALYSIS ==========")

for category, count in formats.most_common():
    print(category, ":", count)

print("\nTotal dates:", sum(formats.values()))
