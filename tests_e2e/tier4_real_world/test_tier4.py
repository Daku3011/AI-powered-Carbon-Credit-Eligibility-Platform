import pytest
import httpx
import time


@pytest.mark.tier4
class TestRealWorldTier4:
    """Tier 4: Real-world user journey tests."""

    def test_complete_user_journey_manufacturing(self, client):
        """Full journey: OCR -> Calculator -> Chatbot -> Report."""
        # Step 1: Upload utility bill for OCR
        files = {"file": ("electricity_bill.pdf", b"dummy pdf content", "application/pdf")}
        ocr_response = client.post("/api/ocr", files=files)
        assert ocr_response.status_code == 200
        ocr_data = ocr_response.json()
        assert ocr_data["success"] is True

        # Step 2: Use extracted data to calculate emissions
        calc_payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": ocr_data["extracted_data"]["energy_kwh"],
                "fuel_diesel_liters": ocr_data["extracted_data"]["fuel_liters"],
                "waste_kg": 150.0,
                "operational_hours": 180,
            },
        }
        calc_response = client.post("/api/calculator/score", json=calc_payload)
        assert calc_response.status_code == 200
        calc_data = calc_response.json()

        # Step 3: Ask chatbot about reduction strategies
        chatbot_payload = {
            "query": f"My manufacturing facility emits {calc_data['total_emissions_tco2e']} tCO2e. What solar projects can help reduce this?"
        }
        chatbot_response = client.post("/api/chatbot/query", json=chatbot_payload)
        assert chatbot_response.status_code == 200
        chatbot_data = chatbot_response.json()
        assert "solar" in chatbot_data["answer"].lower()

        # Step 4: Browse marketplace for project options
        marketplace_response = client.get("/api/marketplace")
        assert marketplace_response.status_code == 200
        marketplace_data = marketplace_response.json()
        assert len(marketplace_data) > 0

        # Step 5: Generate PDF report
        report_payload = {
            "industry": calc_payload["industry"],
            "metrics": calc_payload["metrics"],
            "eligibility_score": {
                "readiness_score": calc_data["eligibility_score"]["readiness_score"],
                "emissions_rating": calc_data["eligibility_score"]["emissions_rating"],
                "reduction_potential_pct": calc_data["eligibility_score"][
                    "reduction_potential_pct"
                ],
                "carbon_credit_potential": calc_data["eligibility_score"][
                    "carbon_credit_potential"
                ],
                "projected_revenue_inr": calc_data["eligibility_score"][
                    "projected_revenue_inr"
                ],
                "confidence_score": calc_data["eligibility_score"]["confidence_score"],
                "scope_1": calc_data["scope_1_emissions_tco2e"],
                "scope_2": calc_data["scope_2_emissions_tco2e"],
                "total": calc_data["total_emissions_tco2e"],
            },
            "roadmap": [
                {
                    "year": r["year"],
                    "recommendation": r["recommendation"],
                    "investment_inr": r["investment_inr"],
                    "savings_inr": r["savings_inr"],
                    "credits_earned": r["credits_earned"],
                }
                for r in calc_data["roadmap"]
            ],
        }

        pdf_response = client.post(
            "/api/reports/export?format=pdf", json=report_payload
        )
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"

        # Step 6: Generate Excel report
        xlsx_response = client.post(
            "/api/reports/export?format=xlsx", json=report_payload
        )
        assert xlsx_response.status_code == 200

    def test_complete_user_journey_services(self, client):
        """Full journey for services industry."""
        # Step 1: Calculate without OCR (services often don't have fuel bills)
        calc_payload = {
            "industry": "services",
            "metrics": {
                "electricity_kwh": 5000.0,
                "fuel_diesel_liters": 100.0,
                "waste_kg": 50.0,
                "operational_hours": 250,
            },
        }
        calc_response = client.post("/api/calculator/score", json=calc_payload)
        assert calc_response.status_code == 200
        calc_data = calc_response.json()

        # Step 2: Ask chatbot about services-specific policies
        chatbot_payload = {
            "query": "What are the energy efficiency guidelines for IT companies?"
        }
        chatbot_response = client.post("/api/chatbot/query", json=chatbot_payload)
        assert chatbot_response.status_code == 200

        # Step 3: Generate reports
        report_payload = {
            "industry": "services",
            "metrics": calc_payload["metrics"],
            "eligibility_score": {
                "readiness_score": calc_data["eligibility_score"]["readiness_score"],
                "emissions_rating": calc_data["eligibility_score"]["emissions_rating"],
                "reduction_potential_pct": calc_data["eligibility_score"][
                    "reduction_potential_pct"
                ],
                "carbon_credit_potential": calc_data["eligibility_score"][
                    "carbon_credit_potential"
                ],
                "projected_revenue_inr": calc_data["eligibility_score"][
                    "projected_revenue_inr"
                ],
                "confidence_score": calc_data["eligibility_score"]["confidence_score"],
                "scope_1": calc_data["scope_1_emissions_tco2e"],
                "scope_2": calc_data["scope_2_emissions_tco2e"],
                "total": calc_data["total_emissions_tco2e"],
            },
            "roadmap": [
                {
                    "year": r["year"],
                    "recommendation": r["recommendation"],
                    "investment_inr": r["investment_inr"],
                    "savings_inr": r["savings_inr"],
                    "credits_earned": r["credits_earned"],
                }
                for r in calc_data["roadmap"]
            ],
        }

        pdf_response = client.post(
            "/api/reports/export?format=pdf", json=report_payload
        )
        assert pdf_response.status_code == 200

    def test_rapid_calculator_requests(self, client):
        """Test handling of rapid sequential calculator requests."""
        payloads = [
            {
                "industry": "manufacturing",
                "metrics": {
                    "electricity_kwh": 10000.0 + i * 1000,
                    "fuel_diesel_liters": 500.0 + i * 50,
                    "waste_kg": 200.0 + i * 20,
                    "operational_hours": 160,
                },
            }
            for i in range(5)
        ]

        for payload in payloads:
            response = client.post("/api/calculator/score", json=payload)
            assert response.status_code == 200

    def test_concurrent_marketplace_and_calculator(self, client):
        """Test marketplace and calculator work simultaneously."""
        calc_payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }

        calc_response = client.post("/api/calculator/score", json=calc_payload)
        marketplace_response = client.get("/api/marketplace")

        assert calc_response.status_code == 200
        assert marketplace_response.status_code == 200

    def test_health_check_under_load(self, client):
        """Test health endpoint remains responsive during operations."""
        for _ in range(10):
            health_response = client.get("/health")
            assert health_response.status_code == 200

        calc_payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 10000.0,
                "fuel_diesel_liters": 500.0,
                "waste_kg": 200.0,
                "operational_hours": 160,
            },
        }
        calc_response = client.post("/api/calculator/score", json=calc_payload)
        assert calc_response.status_code == 200

        health_response = client.get("/health")
        assert health_response.status_code == 200
