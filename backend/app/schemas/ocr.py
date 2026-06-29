from typing import Optional
from pydantic import BaseModel


class OCRExtractedData(BaseModel):
    energy_kwh: float
    fuel_liters: float
    cost: float
    fuel_type: str
    billing_period: str


class OCRResponse(BaseModel):
    success: bool
    extracted_data: Optional[OCRExtractedData] = None
    error: Optional[str] = None
