
import re
import math
from datetime import datetime


def extract_dates(ocr_results):

    date_patterns = [
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b"
    ]

    expiry_keywords = [
        "EXPIRY", "EXPIRES", "EXP",
        "USE BY", "BEST BEFORE", "BBE"
    ]

    manufacturing_keywords = [
        "MFG", "MFD", "MANUFACTURED",
        "MANUFACTURING", "PACKED ON",
        "PKD", "PROD DATE", "DATE OF MANUFACTURE"
    ]

    formats = [
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
        "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y"
    ]

    candidates = []
    expiry_boxes = []
    manufacturing_boxes = []

    for bbox, text, confidence in ocr_results:

        text_upper = text.upper()

        center_x = sum(p[0] for p in bbox) / 4
        center_y = sum(p[1] for p in bbox) / 4

        position = (center_x, center_y)

        for keyword in expiry_keywords:
            pattern = (
                r"(?<![A-Z])"
                + re.escape(keyword)
                + r"(?![A-Z])"
            )

            if re.search(pattern, text_upper):
                expiry_boxes.append(position)
                break

        for keyword in manufacturing_keywords:
            pattern = (
                r"(?<![A-Z])"
                + re.escape(keyword)
                + r"(?![A-Z])"
            )

            if re.search(pattern, text_upper):
                manufacturing_boxes.append(position)
                break

        for pattern in date_patterns:

            for item in re.findall(pattern, text):

                parsed_date = None

                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(
                            item, fmt
                        ).date()
                        break
                    except ValueError:
                        continue

                if parsed_date:
                    candidates.append({
                        "date": parsed_date,
                        "position": position,
                        "confidence": float(confidence),
                        "score": 0
                    })

    for candidate in candidates:

        x1, y1 = candidate["position"]

        for x2, y2 in expiry_boxes:

            distance = math.sqrt(
                (x1 - x2) ** 2 + (y1 - y2) ** 2
            )

            if distance < 250:
                candidate["score"] += 10
            elif distance < 450:
                candidate["score"] += 3

        for x2, y2 in manufacturing_boxes:

            distance = math.sqrt(
                (x1 - x2) ** 2 + (y1 - y2) ** 2
            )

            if distance < 250:
                candidate["score"] -= 15
            elif distance < 450:
                candidate["score"] -= 5

    unique_candidates = {}

    for candidate in candidates:

        current_date = candidate["date"]

        if (
            current_date not in unique_candidates
            or candidate["score"]
            > unique_candidates[current_date]["score"]
        ):
            unique_candidates[current_date] = candidate

    return sorted(
        unique_candidates.values(),
        key=lambda item: (
            -item["score"],
            -item["confidence"]
        )
    )
