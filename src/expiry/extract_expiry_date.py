
import re
from datetime import datetime, date

def extract_dates(text):
    """
    Extract possible dates from OCR text.
    Supports formats like:
    2025/01/28, 28/01/2025, 28.01.2025
    """

    patterns = [
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
        r'\b\d{1,2}\.\d{1,2}\.\d{4}\b'
    ]

    dates = []

    for pattern in patterns:
        matches = re.findall(pattern, text)
        dates.extend(matches)

    return dates


def validate_expiry_date(date_text):
    """Convert a detected date into a Python date."""

    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt).date()
        except ValueError:
            continue

    return None


def check_expiry(expiry_date):
    """Classify the product based on its expiry date."""

    today = date.today()
    days_left = (expiry_date - today).days

    if days_left < 0:
        return "Expired"

    elif days_left <= 30:
        return "Expiring Soon"

    else:
        return "Safe"


# Test using the date detected in our OCR test
sample_text = "Best before: 2025/01/28"

detected_dates = extract_dates(sample_text)

print("Detected dates:", detected_dates)

for item in detected_dates:
    parsed_date = validate_expiry_date(item)

    if parsed_date:
        status = check_expiry(parsed_date)

        print("Expiry Date:", parsed_date)
        print("Product Status:", status)
    else:
        print("Invalid date:", item)
