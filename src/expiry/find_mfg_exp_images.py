



from pathlib import Path
import easyocr

# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "expiry"
    / "Products-Real"
    / "train"
    / "images"
)

# Scan only the first 100 images
MAX_IMAGES = 100

EXPIRY_KEYWORDS = [
    "EXPIRY",
    "EXPIRES",
    "EXP",
    "USE BY",
    "BEST BEFORE",
    "BBE"
]

MANUFACTURING_KEYWORDS = [
    "MFG",
    "MFD",
    "MANUFACTURED",
    "MANUFACTURING",
    "PACKED ON",
    "PKD",
    "PROD DATE",
    "DATE OF MANUFACTURE"
]


def find_keywords(text, keywords):
    text = text.upper()

    return [
        keyword
        for keyword in keywords
        if keyword in text
    ]


def main():

    print("Loading EasyOCR model...")

    reader = easyocr.Reader(["en"], gpu=False)

    image_files = sorted(IMAGE_FOLDER.glob("*.jpg"))[:MAX_IMAGES]

    if not image_files:
        print("No images found. Check the image folder path.")
        return

    print(f"\nImages selected: {len(image_files)}")
    print("Starting OCR scan...\n")

    both_found = 0
    expiry_only = 0
    manufacturing_only = 0
    neither_found = 0
    errors = 0

    for index, image_path in enumerate(image_files, start=1):

        try:
            results = reader.readtext(
                str(image_path),
                detail=1,
                paragraph=False
            )

            detected_text = " ".join(
                result[1] for result in results
            )

            expiry_matches = find_keywords(
                detected_text,
                EXPIRY_KEYWORDS
            )

            manufacturing_matches = find_keywords(
                detected_text,
                MANUFACTURING_KEYWORDS
            )

            if expiry_matches and manufacturing_matches:

                both_found += 1

                print(f"\nBOTH KEYWORDS FOUND: {image_path.name}")
                print(f"Expiry: {expiry_matches}")
                print(f"Manufacturing: {manufacturing_matches}")
                print(f"Detected text: {detected_text}")

            elif expiry_matches:

                expiry_only += 1

            elif manufacturing_matches:

                manufacturing_only += 1

            else:

                neither_found += 1

            print(
                f"Progress: {index}/{len(image_files)} | "
                f"Both found: {both_found}",
                end="\r"
            )

        except Exception as error:

            errors += 1
            print(f"\nError in {image_path.name}: {error}")

    print("\n\n" + "=" * 45)
    print("OCR SCAN COMPLETED")
    print("=" * 45)

    print(f"Total images scanned: {len(image_files)}")
    print(f"Both keyword types: {both_found}")
    print(f"Expiry keywords only: {expiry_only}")
    print(f"Manufacturing keywords only: {manufacturing_only}")
    print(f"Neither keyword found: {neither_found}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()
