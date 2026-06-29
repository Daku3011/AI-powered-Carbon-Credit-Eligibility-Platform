import base64
from typing import Optional
from app.core.config import settings

def extract_bill_data_from_gemini(file_bytes: bytes, filename: str) -> Optional[dict]:
    """
    Extract utility bill data using Gemini API OCR.
    Returns extracted fields or None if failed.
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        file_extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        mime_type = mime_map.get(file_extension, "application/pdf")

        prompt = (
            "Extract utility bill information from this document. "
            "Return ONLY a JSON object with these keys: "
            "energy_kwh (number), fuel_liters (number), cost (number), "
            "fuel_type (string like 'diesel', 'electricity', etc.), "
            "billing_period (string like '2026-05'). "
            "If a value is not found, use 0 for numbers and 'unknown' for strings. "
            "Do not include any markdown formatting, just the raw JSON."
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                prompt,
            ],
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

        import json
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
    result = extract_bill_data_from_gemini(file_bytes, filename)

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
