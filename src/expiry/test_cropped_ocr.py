
import easyocr

print("Loading EasyOCR...")

reader = easyocr.Reader(['en'], gpu=False)

image_path = "reports/expiry_date_crop.jpg"

print("\nReading cropped expiry-date image...")

results = reader.readtext(image_path)

print("\nDetected Text:")

for result in results:
    print(result[1])

print("\nCropped OCR test completed!")
