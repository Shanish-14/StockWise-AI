
import easyocr
import os
import re
from datetime import datetime, date

# 1. Initialize OCR
print("Loading OCR model...")
reader = easyocr.Reader(['en'], gpu=False)


# 2. Extract possible dates
def extract_dates(text):

    patterns = [
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
        r'\b\d{1,2}\.\d{1,2}\.\d{4}\b'
    ]

    dates = []

    for pattern in patterns:
        dates.extend(re.findall(pattern, text))

    return list(dict.fromkeys(dates))


# 3. Convert text into date
def validate_expiry_date(date_text):

    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt).date()
        except ValueError:
            continue

    return None


# 4. Check expiry status
def check_expiry(expiry_date):

    today = date.today()
    days_left = (expiry_date - today).days

    if days_left < 0:
        return "Expired"

    elif days_left <= 30:
        return "Expiring Soon"

    else:
        return "Safe"


# 5. Process product image
def process_product(image_path):

    print("\nProcessing:", image_path)

    results = reader.readtext(image_path)

    full_text = " ".join([result[1] for result in results])

    print("\nDetected Text:")
    print(full_text)

    detected_dates = extract_dates(full_text)

    if not detected_dates:
        print("\nNo date detected.")
        return

    print("\nExpiry Analysis:")

    for item in detected_dates:

        parsed_date = validate_expiry_date(item)

        if parsed_date:

            status = check_expiry(parsed_date)

            print("Detected Date:", item)
            print("Product Status:", status)

        else:
            print("Could not validate:", item)


# 6. Run pipeline
if __name__ == "__main__":

    image_folder = "data/raw/expiry/Products-Real/train/images"

    image_name = os.listdir(image_folder)[0]

    image_path = os.path.join(image_folder, image_name)

    process_product(image_path)
