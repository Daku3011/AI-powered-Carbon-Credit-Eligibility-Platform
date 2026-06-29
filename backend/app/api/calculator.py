from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.calculation import CalculatorRequest, CalculatorResponse
from app.services.calculator import calculate_carbon_and_eligibility
from app.models.calculation import CalculationRecord, RoadmapRecommendation

router = APIRouter(prefix="/calculator", tags=["Calculator"])

@router.post("/score", response_model=CalculatorResponse)
def calculate_score(req: CalculatorRequest, db: Session = Depends(get_db)):
    # 1. Compute response data
    response_data = calculate_carbon_and_eligibility(req)
    
    # 2. Persist record to database
    db_record = CalculationRecord(
        industry=req.industry,
        electricity_kwh=req.metrics.electricity_kwh,
        fuel_diesel_liters=req.metrics.fuel_diesel_liters,
        waste_kg=req.metrics.waste_kg,
        operational_hours=req.metrics.operational_hours,
        scope_1_emissions_tco2e=response_data.scope_1_emissions_tco2e,
        scope_2_emissions_tco2e=response_data.scope_2_emissions_tco2e,
        total_emissions_tco2e=response_data.total_emissions_tco2e,
        readiness_score=response_data.eligibility_score.readiness_score,
        emissions_rating=response_data.eligibility_score.emissions_rating,
        reduction_potential_pct=response_data.eligibility_score.reduction_potential_pct,
        carbon_credit_potential=response_data.eligibility_score.carbon_credit_potential,
        projected_revenue_inr=response_data.eligibility_score.projected_revenue_inr,
        confidence_score=response_data.eligibility_score.confidence_score
    )
    db_record.roadmap = [
        RoadmapRecommendation(
            year=item.year,
            recommendation=item.recommendation,
            investment_inr=item.investment_inr,
            savings_inr=item.savings_inr,
            credits_earned=item.credits_earned
        ) for item in response_data.roadmap
    ]
    db.add(db_record)
    db.commit()
    
    return response_data
