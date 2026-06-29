from pydantic import BaseModel

class MarketplaceProjectSchema(BaseModel):
    id: str
    title: str
    description: str
    cost_inr: float
    roi_pct: float
    payback_years: float
    credit_potential: float

    class Config:
        from_attributes = True
