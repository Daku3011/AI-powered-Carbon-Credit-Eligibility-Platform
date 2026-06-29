import pytest
import httpx


@pytest.mark.tier2
@pytest.mark.calculator
class TestCalculatorTier2:
    """Tier 2: Boundary and corner case tests for calculator."""

    def test_calculator_negative_metrics(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": -100.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 422

    def test_calculator_zero_metrics(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 0.0,
                "fuel_diesel_liters": 0.0,
                "waste_kg": 0.0,
                "operational_hours": 0.0,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["scope_1_emissions_tco2e"] == 0.0
        assert data["scope_2_emissions_tco2e"] == 0.0
        assert data["total_emissions_tco2e"] == 0.0

    def test_calculator_large_values(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 1000000.0,
                "fuel_diesel_liters": 50000.0,
                "waste_kg": 100000.0,
                "operational_hours": 8760,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_emissions_tco2e"] > 0

    def test_calculator_missing_industry(self, client):
        payload = {
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 422

    def test_calculator_missing_metrics(self, client):
        payload = {"industry": "manufacturing"}
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 422

    def test_calculator_empty_body(self, client):
        response = client.post("/api/calculator/score", json={})
        assert response.status_code == 422

    def test_calculator_invalid_metric_type(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": "not_a_number",
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 422

    def test_calculator_empty_industry(self, client):
        payload = {
            "industry": "",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 422


@pytest.mark.tier2
@pytest.mark.ocr
class TestOCRTier2:
    """Tier 2: Boundary and corner case tests for OCR."""

    def test_ocr_invalid_file(self, client):
        files = {"file": ("invalid_invoice.pdf", b"corrupted data", "application/pdf")}
        response = client.post("/api/ocr", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["extracted_data"] is None
        assert "error" in data

    def test_ocr_zero_values(self, client):
        files = {"file": ("zero_invoice.pdf", b"dummy content", "application/pdf")}
        response = client.post("/api/ocr", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["extracted_data"]["energy_kwh"] == 0.0
        assert data["extracted_data"]["fuel_liters"] == 0.0

    def test_ocr_no_file(self, client):
        response = client.post("/api/ocr")
        assert response.status_code == 422

    def test_ocr_response_schema_valid(self, client):
        files = {"file": ("invoice.pdf", b"dummy content", "application/pdf")}
        response = client.post("/api/ocr", files=files)
        data = response.json()
        assert "success" in data
        assert "extracted_data" in data
        if data["success"]:
            assert "energy_kwh" in data["extracted_data"]
            assert "fuel_liters" in data["extracted_data"]
            assert "cost" in data["extracted_data"]
            assert "fuel_type" in data["extracted_data"]
            assert "billing_period" in data["extracted_data"]


@pytest.mark.tier2
@pytest.mark.chatbot
class TestChatbotTier2:
    """Tier 2: Boundary and corner case tests for chatbot."""

    def test_chatbot_empty_query(self, client):
        payload = {"query": ""}
        response = client.post("/api/chatbot/query", json=payload)
        assert response.status_code == 422

    def test_chatbot_long_query(self, client):
        payload = {"query": "What is " + "carbon " * 500 + "market?"}
        response = client.post("/api/chatbot/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_chatbot_special_characters(self, client):
        payload = {"query": "What about <script>alert('xss')</script> carbon credits?"}
        response = client.post("/api/chatbot/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_chatbot_missing_query(self, client):
        response = client.post("/api/chatbot/query", json={})
        assert response.status_code == 422


@pytest.mark.tier2
@pytest.mark.reports
class TestReportsTier2:
    """Tier 2: Boundary and corner case tests for reports."""

    def _invalid_payload(self):
        return {
            "industry": "",
            "metrics": {
                "electricity_kwh": -1000.0,
                "fuel_diesel_liters": -50.0,
                "waste_kg": -20.0,
                "operational_hours": -10,
            },
            "eligibility_score": {
                "readiness_score": 78,
                "emissions_rating": "Medium",
                "reduction_potential_pct": 25.0,
                "carbon_credit_potential": 150.0,
                "projected_revenue_inr": 120000.0,
                "confidence_score": 0.85,
                "scope_1": 1.34,
                "scope_2": 8.20,
                "total": 9.54,
            },
            "roadmap": [],
        }

    def test_export_invalid_format(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
            "eligibility_score": {
                "readiness_score": 78,
                "emissions_rating": "Medium",
                "reduction_potential_pct": 25.0,
                "carbon_credit_potential": 150.0,
                "projected_revenue_inr": 120000.0,
                "confidence_score": 0.85,
                "scope_1": 1.34,
                "scope_2": 8.20,
                "total": 9.54,
            },
            "roadmap": [],
        }
        response = client.post("/api/reports/export?format=csv", json=payload)
        assert response.status_code == 422

    def test_export_missing_body(self, client):
        response = client.post("/api/reports/export?format=pdf")
        assert response.status_code == 422

    def test_export_empty_roadmap(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
            "eligibility_score": {
                "readiness_score": 78,
                "emissions_rating": "Medium",
                "reduction_potential_pct": 25.0,
                "carbon_credit_potential": 150.0,
                "projected_revenue_inr": 120000.0,
                "confidence_score": 0.85,
                "scope_1": 1.34,
                "scope_2": 8.20,
                "total": 9.54,
            },
            "roadmap": [],
        }
        response = client.post("/api/reports/export?format=pdf", json=payload)
        assert response.status_code == 200
