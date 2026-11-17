
import easyocr
import os

# Load EasyOCR
print("Loading OCR model...")
reader = easyocr.Reader(['en'], gpu=False)

# Select one product image
image_folder = "data/raw/expiry/Products-Real/train/images"

image_name = os.listdir(image_folder)[0]
image_path = os.path.join(image_folder, image_name)

print("Testing image:", image_name)

# Read text from image
results = reader.readtext(image_path)

print("\nDetected Text:")
for result in results:
    print(result[1])
    
print("\nOCR testing completed!")
