
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.ocr_service import scan_product_image


router = APIRouter(
    prefix="/api/expiry",
    tags=["Expiry Management"]
)


@router.post("/scan")
async def scan_expiry_image(
    image: UploadFile = File(...)
):

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    extension = Path(image.filename or "").suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are supported."
        )

    content = await image.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB."
        )

    temporary_path = None

    try:
        with NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temporary_file:

            temporary_file.write(content)
            temporary_path = Path(temporary_file.name)

        result = scan_product_image(str(temporary_path))

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(error)}"
        )

    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

        await image.close()
