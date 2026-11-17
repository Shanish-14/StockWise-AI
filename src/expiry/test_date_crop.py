
import json
import os
import easyocr
from PIL import Image

image_name = "test_00002.jpg"

image_path = (
    "data/raw/expiry/Products-Real/evaluation/images/"
    + image_name
)

annotation_path = (
    "data/raw/expiry/Products-Real/evaluation/annotations.json"
)

# Load annotations
with open(annotation_path, "r", encoding="utf-8") as file:
    annotations = json.load(file)

# Find the expiry-date annotation
image_data = annotations[image_name]

expiry_annotation = next(
    ann for ann in image_data["ann"]
    if ann["cls"] == "exp"
)

x1, y1, x2, y2 = expiry_annotation["bbox"]

# Open image and crop expiry-date region with padding
image = Image.open(image_path)

padding = 50

x1 = max(0, int(x1) - padding)
y1 = max(0, int(y1) - padding)
x2 = min(image.width, int(x2) + padding)
y2 = min(image.height, int(y2) + padding)

cropped_image = image.crop((x1, y1, x2, y2))
print("Image size:", image.size)
print("Expiry bounding box:", expiry_annotation["bbox"])
print("Crop size:", cropped_image.size)

# Save cropped image
os.makedirs("reports", exist_ok=True)

crop_path = "reports/test_00002_expiry_crop.jpg"
cropped_image.save(crop_path)

print("Expiry-date crop saved:", crop_path)
print("Actual expiry date:", expiry_annotation["transcription"])

# Read cropped image using EasyOCR
print("\nLoading EasyOCR...")
reader = easyocr.Reader(["en"], gpu=False)

from PIL import ImageEnhance, ImageFilter, ImageOps

# Open cropped image
crop = Image.open(crop_path)

# Convert to grayscale
enhanced = ImageOps.grayscale(crop)

# Increase image size 3 times
enhanced = enhanced.resize(
    (enhanced.width * 3, enhanced.height * 3),
    Image.Resampling.LANCZOS
)

# Improve contrast and sharpness
enhanced = ImageEnhance.Contrast(enhanced).enhance(2)
enhanced = enhanced.filter(
    ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
)

# Save enhanced image
enhanced_path = "reports/test_00002_enhanced.jpg"
enhanced.save(enhanced_path)

print("\nTesting original cropped image...")

results = reader.readtext(
    crop_path,
    detail=1,
    min_size=5,
    text_threshold=0.4,
    low_text=0.3,
    contrast_ths=0.05,
    rotation_info=[90, 180, 270]
)

print("\nDetected text:")
if results:
    for result in results:
        print("Text:", result[1])
        print("Confidence:", result[2])
else:
    print("No text detected.")