
from paddleocr import PaddleOCR

print("Loading PaddleOCR model...")

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    engine="paddle",
    enable_mkldnn=False
)

image_path = "data/raw/expiry/Products-Real/evaluation/images/test_00001.jpg"
print("Testing image:", image_path)

results = ocr.predict(image_path)

print("\nDetected Text:")

for result in results:
    result.print()

print("\nPaddleOCR testing completed!")
