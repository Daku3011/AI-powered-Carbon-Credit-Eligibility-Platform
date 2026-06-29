import pytest
import httpx
import io

# Example E2E tests skeleton demonstrating how to interact with the mock server or backend

@pytest.mark.tier1
@pytest.mark.ocr
def test_ocr_success(client):
    """F2: Test OCR with valid file returns correct schema values."""
    files = {"file": ("invoice.pdf", b"dummy pdf content", "application/pdf")}
    response = client.post("/api/ocr", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "extracted_data" in data
    assert data["extracted_data"]["energy_kwh"] == 12500.5
    assert data["extracted_data"]["fuel_liters"] == 450.0
    assert data["extracted_data"]["fuel_type"] == "diesel"

@pytest.mark.tier2
@pytest.mark.ocr
def test_ocr_invalid_file(client):
    """F2: Test OCR handling of invalid invoice file names."""
    files = {"file": ("invalid_invoice.pdf", b"corrupted data", "application/pdf")}
    response = client.post("/api/ocr", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["extracted_data"] is None
    assert "error" in data

@pytest.mark.tier1
@pytest.mark.calculator
def test_calculator_success(client):
    """F3: Test carbon calculations for manufacturing industry."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 10000.0,
            "fuel_diesel_liters": 500.0,
            "waste_kg": 200.0,
            "operational_hours": 160
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assert output schemas and expected mock calculations
    assert "scope_1_emissions_tco2e" in data
    assert "scope_2_emissions_tco2e" in data
    assert "total_emissions_tco2e" in data
    assert data["scope_1_emissions_tco2e"] == round(500.0 * 0.00268, 2)
    assert data["scope_2_emissions_tco2e"] == round(10000.0 * 0.00082, 2)
    assert data["total_emissions_tco2e"] == round(data["scope_1_emissions_tco2e"] + data["scope_2_emissions_tco2e"], 2)
    
    # Assert eligibility score
    score = data["eligibility_score"]
    assert "readiness_score" in score
    assert "emissions_rating" in score
    assert "reduction_potential_pct" in score
    
    # Assert roadmap is non-empty
    assert len(data["roadmap"]) > 0
    assert data["roadmap"][0]["year"] == 1

@pytest.mark.tier2
@pytest.mark.calculator
def test_calculator_negative_metrics(client):
    """F3: Test calculator boundary with negative metrics (should raise 422)."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": -100.0,
            "fuel_diesel_liters": 500.0,
            "waste_kg": 200.0,
            "operational_hours": 160
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 422

@pytest.mark.tier1
@pytest.mark.chatbot
def test_chatbot_solar_query(client):
    """F6: Test chatbot responds with relevant solar documents."""
    payload = {"query": "Tell me about solar project registration guidelines."}
    response = client.post("/api/chatbot/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "solar" in data["answer"].lower()
    assert "Indian Carbon Market Draft Policy 2023.pdf" in data["sources"]

@pytest.mark.tier1
@pytest.mark.marketplace
def test_marketplace_list(client):
    """F4: Test retrieving project listings from the marketplace."""
    response = client.get("/api/marketplace")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == "solar_transition"
    assert "roi_pct" in data[0]

@pytest.mark.tier1
@pytest.mark.reports
def test_export_pdf_report(client):
    """F7: Test exporting PDF report stream."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 10000.0,
            "fuel_diesel_liters": 500.0,
            "waste_kg": 200.0,
            "operational_hours": 160
        },
        "eligibility_score": {
            "readiness_score": 78,
            "emissions_rating": "Medium",
            "reduction_potential_pct": 25.0,
            "carbon_credit_potential": 150.0,
            "projected_revenue_inr": 120000.0,
            "confidence_score": 0.85
        },
        "roadmap": [
            {
                "year": 1,
                "recommendation": "Install rooftop solar",
                "investment_inr": 500000,
                "savings_inr": 80000,
                "credits_earned": 50
            }
        ]
    }
    response = client.post("/api/reports/export?format=pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
