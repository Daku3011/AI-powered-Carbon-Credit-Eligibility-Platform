from pydantic import BaseModel, ConfigDict

class MarketplaceProjectSchema(BaseModel):
    id: str
    title: str
    description: str
    cost_inr: float
    roi_pct: float
    payback_years: float
    credit_potential: float

    model_config = ConfigDict(from_attributes=True)
