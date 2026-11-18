




import json

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

count = 0

for image_name, image_data in data.items():

    for annotation in image_data["ann"]:

        if annotation["cls"] in ["date", "due"]:

            print("Image:", image_name)
            print("Class:", annotation["cls"])
            print("Available fields:", list(annotation.keys()))
            print("Text:", annotation.get("transcription", "Not available"))
            print("Bounding box:", annotation.get("bbox", "Not available"))
            print("-" * 50)

            count += 1

            if count == 10:
                break

    if count == 10:
        break

print("\nInspection completed!")
