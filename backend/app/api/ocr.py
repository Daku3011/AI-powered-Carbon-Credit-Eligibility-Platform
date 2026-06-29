from fastapi import APIRouter, UploadFile, File
from app.schemas.ocr import OCRResponse
from app.services.ocr import process_ocr

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.post("", response_model=OCRResponse)
async def ocr_extract(file: UploadFile = File(...)):
    content = await file.read()
    result = process_ocr(content, file.filename or "unknown.pdf")
    return result
