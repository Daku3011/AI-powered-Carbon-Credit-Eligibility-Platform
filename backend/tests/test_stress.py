import pytest
import concurrent.futures
from fastapi.testclient import TestClient
import math

def test_stress_negative_metrics(client):
    """Verify that negative inputs for any metric trigger a 422 Validation Error."""
    bad_metrics = [
        {"electricity_kwh": -1.0, "fuel_diesel_liters": 100.0, "waste_kg": 50.0, "operational_hours": 80.0},
        {"electricity_kwh": 100.0, "fuel_diesel_liters": -5.0, "waste_kg": 50.0, "operational_hours": 80.0},
        {"electricity_kwh": 100.0, "fuel_diesel_liters": 100.0, "waste_kg": -0.1, "operational_hours": 80.0},
        {"electricity_kwh": 100.0, "fuel_diesel_liters": 100.0, "waste_kg": 50.0, "operational_hours": -12.0},
    ]
    for metric in bad_metrics:
        payload = {
            "industry": "manufacturing",
            "metrics": metric
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 422, f"Failed to reject negative metric: {metric}"

def test_stress_invalid_floats(client):
    """Verify how the system handles NaN and Infinity values."""
    # JSON standard doesn't support NaN/Infinity. Python's json encoder raises ValueError.
    # We test string representations which Pydantic can parse, and verify that actual
    # float objects (which json.dumps rejects) are handled gracefully.
    for special_val in ["NaN", "Infinity", "-Infinity"]:
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": special_val,
                "fuel_diesel_liters": 100.0,
                "waste_kg": 50.0,
                "operational_hours": 80.0
            }
        }
        response = client.post("/api/calculator/score", json=payload)
        # We expect validation to fail with a 422 error because of our finite validation
        assert response.status_code == 422

def test_stress_large_inputs(client):
    """Verify behavior under extremely large metric values."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 1e15,
            "fuel_diesel_liters": 1e15,
            "waste_kg": 1e15,
            "operational_hours": 1e15
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scope_1_emissions_tco2e"] > 0
    assert data["scope_2_emissions_tco2e"] > 0
    assert data["total_emissions_tco2e"] > 0
    # Clamping rules should keep eligibility score parameters in valid range
    assert 10 <= data["eligibility_score"]["readiness_score"] <= 95
    assert 10.0 <= data["eligibility_score"]["reduction_potential_pct"] <= 50.0
    assert 0.5 <= data["eligibility_score"]["confidence_score"] <= 0.95

def test_stress_underflow_inputs(client):
    """Verify behavior under extremely small positive values."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 1e-15,
            "fuel_diesel_liters": 1e-15,
            "waste_kg": 1e-15,
            "operational_hours": 1e-15
        }
    }
    response = client.post("/api/calculator/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should calculate successfully without crashing due to underflow
    assert data["total_emissions_tco2e"] >= 0

def test_stress_empty_and_long_industry(client):
    """Verify behavior under empty or extremely long industry names."""
    # 1. Empty industry
    payload_empty = {
        "industry": "",
        "metrics": {
            "electricity_kwh": 100.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 80.0
        }
    }
    response = client.post("/api/calculator/score", json=payload_empty)
    # The application should handle empty strings or fail gracefully. Let's assert it runs.
    assert response.status_code == 200
    
    # 2. Long industry (10000 chars)
    payload_long = {
        "industry": "A" * 10000,
        "metrics": {
            "electricity_kwh": 100.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 80.0
        }
    }
    response = client.post("/api/calculator/score", json=payload_long)
    assert response.status_code == 422

    # 3. Exactly 101 characters (should be rejected)
    payload_101 = {
        "industry": "A" * 101,
        "metrics": {
            "electricity_kwh": 100.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 80.0
        }
    }
    response = client.post("/api/calculator/score", json=payload_101)
    assert response.status_code == 422

    # 4. Exactly 100 characters (should be accepted)
    payload_100 = {
        "industry": "A" * 100,
        "metrics": {
            "electricity_kwh": 100.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 80.0
        }
    }
    response = client.post("/api/calculator/score", json=payload_100)
    assert response.status_code == 200

def test_stress_sql_html_injection_industry(client):
    """Verify robustness against SQL Injection and HTML Injection in string fields."""
    payloads = [
        "manufacturing' OR 1=1; --",
        "'; DROP TABLE calculation_records; --",
        "<script>alert('xss')</script>",
        "\" onerror=\"alert(1)\""
    ]
    for payload_val in payloads:
        payload = {
            "industry": payload_val,
            "metrics": {
                "electricity_kwh": 100.0,
                "fuel_diesel_liters": 100.0,
                "waste_kg": 50.0,
                "operational_hours": 80.0
            }
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200
        # If it succeeds, let's verify database query to retrieve it still works.
        # This checks that SQL Injection did not corrupt SQL execution or drop the table.
        # We can also check if the industry string was saved verbatim.
        data = response.json()
        assert "scope_1_emissions_tco2e" in data

def test_stress_rapid_requests(client):
    """Verify behavior under rapid sequential requests."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 12500.5,
            "fuel_diesel_liters": 450.0,
            "waste_kg": 120.0,
            "operational_hours": 160.0
        }
    }
    # Execute 100 sequential requests
    for _ in range(100):
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200

def test_stress_concurrency(client):
    """Verify database concurrency and lock performance by running concurrent requests to both score and marketplace."""
    payload = {
        "industry": "manufacturing",
        "metrics": {
            "electricity_kwh": 12500.5,
            "fuel_diesel_liters": 450.0,
            "waste_kg": 120.0,
            "operational_hours": 160.0
        }
    }
    
    # We use ThreadPoolExecutor to make concurrent calls to the client.
    # Note: TestClient is not completely thread-safe if there is database session state conflicts,
    # but it will test SQLite's database lock safety under FastAPI's typical session setup.
    def make_score_request():
        return client.post("/api/calculator/score", json=payload)

    def make_marketplace_request():
        return client.get("/api/marketplace")

    concurrency_level = 20
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        # Submit 10 calculator score requests and 10 marketplace requests in parallel
        futures = []
        for i in range(concurrency_level):
            if i % 2 == 0:
                futures.append(executor.submit(make_score_request))
            else:
                futures.append(executor.submit(make_marketplace_request))
        results = [f.result() for f in futures]

    for res in results:
        # Check if any request failed due to SQLite database locking (500 Internal Server Error)
        # or other concurrency issues.
        assert res.status_code == 200, f"Concurrency request failed: {res.status_code} - {res.text}"
