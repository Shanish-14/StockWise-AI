
import json
import cv2
import os

# File paths
image_name = "img_00069.jpg"

image_path = os.path.join(
    "data/raw/expiry/Products-Real/train/images",
    image_name
)

annotation_path = "data/raw/expiry/Products-Real/train/annotations.json"

# Load annotations
with open(annotation_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Load image
image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Image not found: {image_path}")

# Different colors for annotation classes
colors = {
    "date": (0, 255, 0),
    "due": (0, 0, 255),
    "prod": (255, 0, 0),
    "code": (0, 255, 255)
}

# Draw annotation boxes
for annotation in data[image_name]["ann"]:

    class_name = annotation["cls"]
    x1, y1, x2, y2 = map(int, annotation["bbox"])

    color = colors.get(class_name, (255, 255, 255))

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        color,
        2
    )

    cv2.putText(
        image,
        class_name,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )

# Save output
os.makedirs("reports", exist_ok=True)

output_path = "reports/annotated_product_69.jpg"
cv2.imwrite(output_path, image)

print("Annotation visualization completed!")
print("Image saved to:", output_path)
