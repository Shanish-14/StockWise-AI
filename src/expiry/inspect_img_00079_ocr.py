
import easyocr
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "expiry"
    / "Products-Real"
    / "evaluation"
    / "images"
    / "test_00079.jpg"
)

print("Loading EasyOCR...")

reader = easyocr.Reader(["en"], gpu=False)

results = reader.readtext(
    str(IMAGE_PATH),
    detail=1,
    paragraph=False
)

print("\n" + "=" * 60)
print("COMPLETE OCR OUTPUT")
print("=" * 60)

for i, (bbox, text, confidence) in enumerate(results, start=1):

    xs = [point[0] for point in bbox]
    ys = [point[1] for point in bbox]

    x = round(sum(xs) / len(xs))
    y = round(sum(ys) / len(ys))

    print(
        f"{i:02d}. Text: {text:<35} "
        f"Confidence: {confidence:.3f} "
        f"Position: ({x}, {y})"
    )

print("\nTotal OCR detections:", len(results))
