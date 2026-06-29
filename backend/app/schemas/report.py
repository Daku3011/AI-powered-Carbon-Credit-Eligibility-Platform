from typing import List, Optional
from pydantic import BaseModel


class ReportEligibility(BaseModel):
    readiness_score: int = 0
    emissions_rating: str = ""
    reduction_potential_pct: float = 0.0
    carbon_credit_potential: float = 0.0
    projected_revenue_inr: float = 0.0
    confidence_score: float = 0.0
    scope_1: float = 0.0
    scope_2: float = 0.0
    total: float = 0.0


class ReportRoadmapItem(BaseModel):
    year: int
    recommendation: str
    investment_inr: float
    savings_inr: float
    credits_earned: float


class ReportRequest(BaseModel):
    industry: str
    metrics: dict
    eligibility_score: ReportEligibility
    roadmap: List[ReportRoadmapItem]
