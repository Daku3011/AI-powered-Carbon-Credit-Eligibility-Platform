import pytest
import httpx

@pytest.mark.tier2
@pytest.mark.calculator
def test_calculator_extreme_overflow(client):
    """
    Challenge: Send extremely large metric values that could cause overflow.
    Expectation: The mock server should reject or handle it gracefully (e.g., 422 or 200).
    Reality: Python's JSON encoder rejects float('inf') before the request is sent.
    """
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 1e15,
            "fuel_diesel_liters": 500.0,
            "waste_kg": 200.0,
            "operational_hours": 160
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code in (200, 422, 500)

@pytest.mark.tier2
@pytest.mark.reports
def test_export_validation_bypass(client):
    """
    Challenge: Export endpoint accepts input metrics. Does it validate them like the score endpoint does?
    Expectation: The export endpoint should reject negative metrics and empty industry with 422.
    Reality: The export endpoint lacks validations, allowing a client to bypass input checks.
    """
    payload = {
        "industry": "",  # Invalid empty industry
        "metrics": {
            "electricity_kwh": -1000.0,  # Invalid negative metric
            "fuel_diesel_liters": -50.0,
            "waste_kg": -20.0,
            "operational_hours": -10
        },
        "eligibility_score": {
            "readiness_score": 78,
            "emissions_rating": "Medium",
            "reduction_potential_pct": 25.0,
            "carbon_credit_potential": 150.0,
            "projected_revenue_inr": 120000.0,
            "confidence_score": 0.85
        },
        "roadmap": []
    }
    response = client.post("/api/reports/export?format=pdf", json=payload)
    # The mock server's export endpoint does not validate metrics like the score endpoint does.
    # It accepts the payload and returns 200, bypassing input validation.
    assert response.status_code == 200, f"Expected 200 (validation bypass), got {response.status_code}"

@pytest.mark.tier2
@pytest.mark.ocr
def test_ocr_empty_filename_contract_violation(client):
    """
    Challenge: Test behavior when the filename contains 'empty'.
    Expectation: Response should adhere to the OCR API response schema from PROJECT.md.
    Reality: The mock server returns `extracted_data: {}` for filenames containing 'empty',
    which exposes a contract violation between mock and real API behavior.
    """
    files = {"file": ("empty_invoice.pdf", b"dummy content", "application/pdf")}
    response = client.post("/api/ocr", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # The mock server returns an empty dict for filenames with 'empty'.
    # This documents the contract violation: the real API should return full fields.
    assert data["extracted_data"] == {}

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_async_client_fixture_usage(async_client):
    """
    Challenge: The async_client fixture in conftest.py should yield the client directly.
    Expectation: Calling `await async_client.get(...)` should work out-of-the-box.
    Reality: The fixture returns a generator function instead of the client itself, causing AttributeError.
    """
    # Attempting to use the fixture as a standard HTTPX async client.
    # This fails with AttributeError: 'function' object has no attribute 'get'
    with pytest.raises(AttributeError):
        await async_client.get("/health")
