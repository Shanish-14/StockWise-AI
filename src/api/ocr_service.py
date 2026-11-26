

import re
from datetime import datetime
from pathlib import Path

import easyocr

from src.expiry.date_detector import extract_dates


_reader = None


def get_reader():
    global _reader

    if _reader is None:
        print("Loading EasyOCR model...")
        _reader = easyocr.Reader(["en"], gpu=False)
        print("EasyOCR model loaded successfully.")

    return _reader


def scan_product_image(image_path: str):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    reader = get_reader()
    ocr_results = reader.readtext(str(image_path))

    extracted_text = " ".join(
        text for bbox, text, confidence in ocr_results
    )

    # First: use the existing keyword-aware detector
    candidates = extract_dates(ocr_results)

    detected_dates = []

    for candidate in candidates:
        detected_dates.append({
            "expiry_date": candidate["date"].isoformat(),
            "confidence": round(candidate["confidence"], 4),
            "score": candidate["score"],
            "detection_method": "keyword_detector"
        })

    # Second: fallback using the complete OCR text
    if extracted_text:

        normalized_text = re.sub(
            r"(?<=\d)\s*[_./-]\s*(?=\d)",
            "-",
            extracted_text
        )

        date_pattern = (
            r"\b\d{4}-\d{1,2}-\d{1,2}\b"
        )

        matches = re.findall(
            date_pattern,
            normalized_text
        )

        existing_dates = {
            item["expiry_date"]
            for item in detected_dates
        }

        for match in matches:
            try:
                parsed_date = datetime.strptime(
                    match, "%Y-%m-%d"
                ).date()

                iso_date = parsed_date.isoformat()

                if iso_date not in existing_dates:
                    detected_dates.append({
                        "expiry_date": iso_date,
                        "confidence": None,
                        "score": 0,
                        "detection_method": "full_text_fallback"
                    })

                    existing_dates.add(iso_date)

            except ValueError:
                continue

    # Sort candidates by score, then confidence
    detected_dates.sort(
        key=lambda item: (
            -item["score"],
            -(item["confidence"] or 0)
        )
    )

    return {
        "success": True,
        "extracted_text": extracted_text,
        "total_dates_found": len(detected_dates),
        "detected_dates": detected_dates,
        "suggested_expiry_date": (
            detected_dates[0]["expiry_date"]
            if detected_dates else None
        )
    }
