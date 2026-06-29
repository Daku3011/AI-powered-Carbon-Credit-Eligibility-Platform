import pytest

def test_carbon_and_eligibility_scoring_with_manufacturing_standard_input(client):
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 12500.5,
            "fuel_diesel_liters": 450.0,
            "waste_kg": 120.0,
            "operational_hours": 160
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check carbon calculations
    assert data["scope_1_emissions_tco2e"] == 1.21
    assert data["scope_2_emissions_tco2e"] == 10.25
    assert data["total_emissions_tco2e"] == 11.46
    
    # Check eligibility scoring
    score = data["eligibility_score"]
    assert score["readiness_score"] == 78
    assert score["emissions_rating"] == "Medium"
    assert score["reduction_potential_pct"] == 25.0
    assert score["carbon_credit_potential"] == 150.0
    assert score["projected_revenue_inr"] == 120000.0
    assert score["confidence_score"] == 0.85
    
    # Check roadmap
    assert len(data["roadmap"]) == 3
    assert data["roadmap"][0]["year"] == 1
    assert data["roadmap"][0]["recommendation"] == "Install rooftop solar"
    assert data["roadmap"][0]["investment_inr"] == 500000
    assert data["roadmap"][0]["savings_inr"] == 80000
    assert data["roadmap"][0]["credits_earned"] == 50

def test_carbon_calculator_with_zero_inputs_returns_clamped_scores(client):
    payload = {
        "industry": "retail",
        "metrics": {
            "electricity_kwh": 0.0,
            "fuel_diesel_liters": 0.0,
            "waste_kg": 0.0,
            "operational_hours": 0.0
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Total emissions are 0.0
    assert data["scope_1_emissions_tco2e"] == 0.0
    assert data["scope_2_emissions_tco2e"] == 0.0
    assert data["total_emissions_tco2e"] == 0.0
    
    score = data["eligibility_score"]
    # Readiness should clamp at 87 - 0 - 0 - 0 = 87
    assert score["readiness_score"] == 87
    # Rating for low emissions is Low
    assert score["emissions_rating"] == "Low"
    # Reduction potential clamps to 10% minimum
    assert score["reduction_potential_pct"] == 15.0  # Base is 15.0, adjustment 0.0
    # Confidence score should decrease because inputs are 0: 0.85 - 0.10 (elec/diesel == 0) - 0.05 (waste == 0) - 0.10 (hrs < 80) = 0.60
    assert score["confidence_score"] == 0.60

def test_carbon_calculator_rejects_negative_metrics(client):
    payload = {
        "industry": "services",
        "metrics": {
            "electricity_kwh": -10.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 40.0
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 422  # Validation error

def test_carbon_calculator_under_minimum_operational_hours(client):
    payload = {
        "industry": "agriculture",
        "metrics": {
            "electricity_kwh": 1000.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 50.0
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Confidence score: base 0.85 - 0.10 (hours < 80) = 0.75
    assert data["eligibility_score"]["confidence_score"] == 0.75

def test_carbon_calculator_different_industries_emissions_ratings(client):
    # Test high emissions rating for services (threshold is >= 10.0)
    # 15000 kWh * 0.00082 = 12.3 tCO2e
    payload = {
        "industry": "services",
        "metrics": {
            "electricity_kwh": 15000.0,
            "fuel_diesel_liters": 0.0,
            "waste_kg": 0.0,
            "operational_hours": 100.0
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["eligibility_score"]["emissions_rating"] == "High"
