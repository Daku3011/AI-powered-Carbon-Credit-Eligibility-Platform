import math
from pydantic import BaseModel, Field, field_validator
from typing import List

class CalculatorMetrics(BaseModel):
    electricity_kwh: float = Field(..., ge=0)
    fuel_diesel_liters: float = Field(..., ge=0)
    waste_kg: float = Field(..., ge=0)
    operational_hours: float = Field(..., ge=0)

    @field_validator("electricity_kwh", "fuel_diesel_liters", "waste_kg", "operational_hours")
    @classmethod
    def validate_finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("Value must be a finite float")
        return v

class CalculatorRequest(BaseModel):
    industry: str = Field(..., max_length=100)
    metrics: CalculatorMetrics

class EligibilityScore(BaseModel):
    readiness_score: int
    emissions_rating: str
    reduction_potential_pct: float
    carbon_credit_potential: float
    projected_revenue_inr: float
    confidence_score: float

class RoadmapRecommendationSchema(BaseModel):
    year: int
    recommendation: str
    investment_inr: float
    savings_inr: float
    credits_earned: float

    class Config:
        from_attributes = True

class CalculatorResponse(BaseModel):
    scope_1_emissions_tco2e: float
    scope_2_emissions_tco2e: float
    total_emissions_tco2e: float
    eligibility_score: EligibilityScore
    roadmap: List[RoadmapRecommendationSchema]
