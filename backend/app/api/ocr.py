import os
import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.ocr import OCRResponse
from app.services.ocr import process_ocr

router = APIRouter(prefix="/ocr", tags=["OCR"])

def sanitize_filename(filename: str) -> str:
    # Keep only alphanumeric, dot, underscore, dash
    filename = os.getenv("SANITIZED_BASE", os.path.basename(filename))
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return filename

@router.post("", response_model=OCRResponse)
async def ocr_extract(file: UploadFile = File(...)):
    # 1. Validate MIME type
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type {file.content_type}. Only PDF, PNG, and JPEG/JPG are allowed."
        )

    # 2. Validate file size (limit to 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 10MB limit."
        )

    # 3. Sanitize filename
    original_filename = file.filename or "unknown.pdf"
    sanitized = sanitize_filename(original_filename)

    result = process_ocr(content, sanitized)
    return result
