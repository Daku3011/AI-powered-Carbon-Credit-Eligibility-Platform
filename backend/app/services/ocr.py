import base64
import json
import io
from typing import Optional
from app.core.config import settings


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""


def extract_text_from_image(file_bytes: bytes, filename: str) -> str:
    """Extract text from image using pytesseract if available, otherwise return empty."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img)
    except ImportError:
        return ""
    except Exception:
        return ""


def extract_bill_data_from_openrouter(file_bytes: bytes, filename: str) -> Optional[dict]:
    """
    Extract utility bill data using OpenRouter API.
    Returns extracted fields or None if failed.
    """
    if not settings.OPENROUTER_API_KEY:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

        file_extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if file_extension == "pdf":
            text = extract_text_from_pdf(file_bytes)
        elif file_extension in ["png", "jpg", "jpeg"]:
            text = extract_text_from_image(file_bytes, filename)
        else:
            try:
                text = file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                text = ""

        if not text.strip():
            return None

        prompt = (
            "Extract utility bill information from the following text. "
            "Return ONLY a JSON object with these keys: "
            "energy_kwh (number), fuel_liters (number), cost (number), "
            "fuel_type (string like 'diesel', 'electricity', etc.), "
            "billing_period (string like '2026-05'). "
            "If a value is not found, use 0 for numbers and 'unknown' for strings. "
            "Do not include any markdown formatting, just the raw JSON.\n\n"
            f"Document text:\n{text[:3000]}"
        )

        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

        data = json.loads(raw_text)
        return {
            "energy_kwh": float(data.get("energy_kwh", 0)),
            "fuel_liters": float(data.get("fuel_liters", 0)),
            "cost": float(data.get("cost", 0)),
            "fuel_type": str(data.get("fuel_type", "unknown")),
            "billing_period": str(data.get("billing_period", "unknown")),
        }
    except Exception:
        return None


def process_ocr(file_bytes: bytes, filename: str) -> dict:
    """
    Main OCR processing function.
    Returns success response dict.
    """
    result = extract_bill_data_from_openrouter(file_bytes, filename)

    if result is None:
        return {
            "success": False,
            "extracted_data": None,
            "error": "Failed to extract data from the uploaded document.",
        }

    return {
        "success": True,
        "extracted_data": result,
    }
