
import cv2
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

OUTPUT_DIR = PROJECT_ROOT / "reports" / "expiry_debug"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(IMAGE_PATH)

height, width = image.shape[:2]

print("Image size:", width, "x", height)

# Draw horizontal grid lines.
for y in range(0, height, 50):

    cv2.line(
        image,
        (0, y),
        (width, y),
        (0, 255, 0),
        1
    )

    cv2.putText(
        image,
        str(y),
        (5, max(y - 5, 15)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        1
    )

# Draw vertical grid lines.
for x in range(0, width, 50):

    cv2.line(
        image,
        (x, 0),
        (x, height),
        (255, 0, 0),
        1
    )

    cv2.putText(
        image,
        str(x),
        (x + 3, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 0, 0),
        1
    )

output_path = OUTPUT_DIR / "img_00079_grid.jpg"

cv2.imwrite(str(output_path), image)

print("Grid image saved:", output_path)
