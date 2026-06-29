import pytest
import httpx


@pytest.mark.tier1
@pytest.mark.calculator
class TestCalculatorTier1:
    """Tier 1: Basic calculator functionality."""

    def test_calculator_success_manufacturing(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert "scope_1_emissions_tco2e" in data
        assert "scope_2_emissions_tco2e" in data
        assert "total_emissions_tco2e" in data
        assert data["scope_1_emissions_tco2e"] == round(500.0 * 0.00268, 2)
        assert data["scope_2_emissions_tco2e"] == round(10000.0 * 0.00082, 2)
        assert data["total_emissions_tco2e"] == round(
            data["scope_1_emissions_tco2e"] + data["scope_2_emissions_tco2e"], 2
        )

        score = data["eligibility_score"]
        assert "readiness_score" in score
        assert "emissions_rating" in score
        assert "reduction_potential_pct" in score
        assert "carbon_credit_potential" in score
        assert "projected_revenue_inr" in score
        assert "confidence_score" in score

        assert len(data["roadmap"]) > 0
        assert data["roadmap"][0]["year"] == 1

    def test_calculator_success_services(self, client):
        payload = {
            "industry": "services",
            "metrics": {
                "electricity_kwh": 2000.0,
                "fuel_diesel_liters": 50.0,
                "waste_kg": 30.0,
                "operational_hours": 200,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["scope_1_emissions_tco2e"] == round(50.0 * 0.00268, 2)
        assert data["scope_2_emissions_tco2e"] == round(2000.0 * 0.00082, 2)

    def test_calculator_success_agriculture(self, client):
        payload = {
            "industry": "agriculture",
            "metrics": {
                "electricity_kwh": 5000.0,
                "fuel_diesel_liters": 1000.0,
                "waste_kg": 500.0,
                "operational_hours": 120,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "scope_1_emissions_tco2e" in data
        assert data["total_emissions_tco2e"] > 0

    def test_calculator_roadmap_structure(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        data = response.json()

        assert len(data["roadmap"]) >= 1
        for i, item in enumerate(data["roadmap"]):
            assert item["year"] == i + 1
            assert "recommendation" in item
            assert "investment_inr" in item
            assert "savings_inr" in item
            assert "credits_earned" in item

    def test_calculator_score_ranges(self, client):
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        response = client.post("/api/calculator/score", json=payload)
        data = response.json()
        score = data["eligibility_score"]

        assert 0 <= score["readiness_score"] <= 100
        assert score["emissions_rating"] in ["Low", "Medium", "High"]
        assert 0 <= score["reduction_potential_pct"] <= 100
        assert score["carbon_credit_potential"] >= 0
        assert score["projected_revenue_inr"] >= 0
        assert 0 <= score["confidence_score"] <= 1


@pytest.mark.tier1
@pytest.mark.ocr
class TestOCRTier1:
    """Tier 1: Basic OCR functionality."""

    def test_ocr_success(self, client):
        files = {"file": ("invoice.pdf", b"dummy pdf content", "application/pdf")}
        response = client.post("/api/ocr", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "extracted_data" in data
        assert data["extracted_data"]["energy_kwh"] == 12500.5
        assert data["extracted_data"]["fuel_liters"] == 450.0
        assert data["extracted_data"]["fuel_type"] == "diesel"

    def test_ocr_png_file(self, client):
        files = {"file": ("invoice.png", b"dummy png content", "image/png")}
        response = client.post("/api/ocr", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["extracted_data"]["energy_kwh"] == 12500.5

    def test_ocr_jpg_file(self, client):
        files = {"file": ("invoice.jpg", b"dummy jpg content", "image/jpeg")}
        response = client.post("/api/ocr", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.tier1
@pytest.mark.chatbot
class TestChatbotTier1:
    """Tier 1: Basic chatbot functionality."""

    def test_chatbot_solar_query(self, client):
        payload = {"query": "Tell me about solar project registration guidelines."}
        response = client.post("/api/chatbot/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "solar" in data["answer"].lower()
        assert "Indian Carbon Market Draft Policy 2023.pdf" in data["sources"]

    def test_chatbot_wind_query(self, client):
        payload = {"query": "What are the wind energy registration requirements?"}
        response = client.post("/api/chatbot/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "wind" in data["answer"].lower()

    def test_chatbot_general_query(self, client):
        payload = {"query": "How do I get started with carbon credits?"}
        response = client.post("/api/chatbot/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_chatbot_response_schema(self, client):
        payload = {"query": "What is the Indian carbon market?"}
        response = client.post("/api/chatbot/query", json=payload)
        data = response.json()
        assert "query" in data
        assert "answer" in data
        assert "sources" in data
        assert data["query"] == payload["query"]


@pytest.mark.tier1
@pytest.mark.marketplace
class TestMarketplaceTier1:
    """Tier 1: Basic marketplace functionality."""

    def test_marketplace_list(self, client):
        response = client.get("/api/marketplace")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_marketplace_project_schema(self, client):
        response = client.get("/api/marketplace")
        data = response.json()
        project = data[0]
        assert "id" in project
        assert "title" in project
        assert "description" in project
        assert "cost_inr" in project
        assert "roi_pct" in project
        assert "payback_years" in project
        assert "credit_potential" in project

    def test_marketplace_solar_project_exists(self, client):
        response = client.get("/api/marketplace")
        data = response.json()
        ids = [p["id"] for p in data]
        assert "solar_transition" in ids

    def test_marketplace_project_values_positive(self, client):
        response = client.get("/api/marketplace")
        data = response.json()
        for project in data:
            assert project["cost_inr"] > 0
            assert project["roi_pct"] > 0
            assert project["payback_years"] > 0
            assert project["credit_potential"] > 0


@pytest.mark.tier1
@pytest.mark.reports
class TestReportsTier1:
    """Tier 1: Basic report export functionality."""

    def _valid_payload(self):
        return {
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
            "roadmap": [
                {
                    "year": 1,
                    "recommendation": "Install rooftop solar",
                    "investment_inr": 500000,
                    "savings_inr": 80000,
                    "credits_earned": 50,
                }
            ],
        }

    def test_export_pdf_report(self, client):
        response = client.post(
            "/api/reports/export?format=pdf", json=self._valid_payload()
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content.startswith(b"%PDF")

    def test_export_excel_report(self, client):
        response = client.post(
            "/api/reports/export?format=xlsx", json=self._valid_payload()
        )
        assert response.status_code == 200
        assert (
            response.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_export_pdf_has_content(self, client):
        response = client.post(
            "/api/reports/export?format=pdf", json=self._valid_payload()
        )
        assert len(response.content) > 0

    def test_export_excel_has_content(self, client):
        response = client.post(
            "/api/reports/export?format=xlsx", json=self._valid_payload()
        )
        assert len(response.content) > 0


@pytest.mark.tier1
class TestHealthTier1:
    """Tier 1: Health endpoint."""

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
