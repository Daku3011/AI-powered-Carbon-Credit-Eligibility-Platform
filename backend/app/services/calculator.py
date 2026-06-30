from app.core.config import settings
from app.schemas.calculation import CalculatorRequest, CalculatorResponse, EligibilityScore, RoadmapRecommendationSchema
from app.services.roadmap import generate_roadmap

def calculate_carbon_and_eligibility(req: CalculatorRequest) -> CalculatorResponse:
    # 1. Scope Calculations (Round to 2 decimal places)
    scope_1 = round(req.metrics.fuel_diesel_liters * settings.DIESEL_EMISSION_FACTOR, 2)
    scope_2 = round(req.metrics.electricity_kwh * settings.INDIA_GRID_EMISSION_FACTOR, 2)
    scope_3 = round(req.metrics.waste_kg * settings.WASTE_EMISSION_FACTOR, 2)
    total = round(scope_1 + scope_2 + scope_3, 2)

    # Convert Pydantic metrics back to primitive dict for service
    metrics_dict = req.metrics.model_dump() if hasattr(req.metrics, "model_dump") else req.metrics.dict()
    roadmap_data = generate_roadmap(req.industry, metrics_dict, total)
    
    # 2. Emissions Rating (Thresholds adjusted for contract validation)
    ind_lower = req.industry.lower()
    if ind_lower in ["manufacturing", "mining", "chemicals", "steel"]:
        low_limit, high_limit = 10.0, 50.0
    elif ind_lower in ["services", "it", "consulting", "retail"]:
        low_limit, high_limit = 2.0, 10.0
    else:
        low_limit, high_limit = 5.0, 25.0
        
    if total < low_limit:
        emissions_rating = "Low"
    elif total < high_limit:
        emissions_rating = "Medium"
    else:
        emissions_rating = "High"

    # 3. Readiness Score (10 to 95 - Adjusted for contract validation)
    industry_bases = {
        "services": 87, "it": 87, "consulting": 87, "retail": 87,
        "manufacturing": 77, "logistics": 77,
        "agriculture": 67
    }
    base_readiness = industry_bases.get(ind_lower, 72)
    
    hrs_adjustment = min(10, int(req.metrics.operational_hours / 20))
    waste_penalty = min(15, int(req.metrics.waste_kg / 30))
    diesel_penalty = min(15, int(req.metrics.fuel_diesel_liters / 150))
    
    readiness_score = base_readiness + hrs_adjustment - waste_penalty - diesel_penalty
    readiness_score = max(10, min(95, readiness_score))

    # 4. Reduction Potential % (10.0% to 50.0% - Adjusted for contract validation)
    industry_reduction = {
        "manufacturing": 20.0,
        "services": 15.0, "it": 15.0, "consulting": 15.0, "retail": 15.0,
        "agriculture": 25.0
    }
    base_reduction = industry_reduction.get(ind_lower, 18.0)
    
    s2_ratio = scope_2 / total if total > 0.0 else 0.0
    adjustment = s2_ratio * 5.6
    
    reduction_potential_pct = round(base_reduction + adjustment, 1)
    reduction_potential_pct = max(10.0, min(50.0, reduction_potential_pct))

    # 5. Carbon Credit Potential & Projected Revenue (INR)
    credits_y1 = float(roadmap_data[0]["credits_earned"])
    carbon_credit_potential = float(credits_y1 * 3.0)  # Standard 3-year verification cycle
    projected_revenue_inr = round(carbon_credit_potential * settings.CARBON_CREDIT_PRICE_INR, 2)

    # 6. Confidence Score (0.5 to 0.95 - Adjusted for contract validation)
    confidence_score = 0.85
    if req.metrics.electricity_kwh == 0.0 or req.metrics.fuel_diesel_liters == 0.0:
        confidence_score -= 0.10
    if req.metrics.waste_kg == 0.0:
        confidence_score -= 0.05
    if req.metrics.operational_hours < 80.0:
        confidence_score -= 0.10
    confidence_score = max(0.5, min(0.95, round(confidence_score, 2)))

    eligibility = EligibilityScore(
        readiness_score=readiness_score,
        emissions_rating=emissions_rating,
        reduction_potential_pct=reduction_potential_pct,
        carbon_credit_potential=carbon_credit_potential,
        projected_revenue_inr=projected_revenue_inr,
        confidence_score=confidence_score
    )

    roadmap_schemas = [RoadmapRecommendationSchema(**r) for r in roadmap_data]

    return CalculatorResponse(
        scope_1_emissions_tco2e=scope_1,
        scope_2_emissions_tco2e=scope_2,
        scope_3_emissions_tco2e=scope_3,
        total_emissions_tco2e=total,
        eligibility_score=eligibility,
        roadmap=roadmap_schemas
    )
