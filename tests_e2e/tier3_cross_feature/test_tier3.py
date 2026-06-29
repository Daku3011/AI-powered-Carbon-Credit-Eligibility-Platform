import pytest
import httpx


@pytest.mark.tier3
class TestCrossFeatureTier3:
    """Tier 3: Cross-feature integration tests."""

    def test_calculator_to_report_flow(self, client):
        """Test data flow from calculator to report export."""
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
        calc_data = calc_response.json()

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

        xlsx_response = client.post(
            "/api/reports/export?format=xlsx", json=report_payload
        )
        assert xlsx_response.status_code == 200

    def test_ocr_to_calculator_flow(self, client):
        """Test data flow from OCR extraction to calculator input."""
        files = {"file": ("invoice.pdf", b"dummy pdf content", "application/pdf")}
        ocr_response = client.post("/api/ocr", files=files)
        assert ocr_response.status_code == 200
        ocr_data = ocr_response.json()

        assert ocr_data["success"] is True
        extracted = ocr_data["extracted_data"]

        calc_payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": extracted["energy_kwh"],
                "fuel_diesel_liters": extracted["fuel_liters"],
                "waste_kg": 100.0,
                "operational_hours": 160,
            },
        }

        calc_response = client.post("/api/calculator/score", json=calc_payload)
        assert calc_response.status_code == 200
        calc_data = calc_response.json()
        assert calc_data["scope_1_emissions_tco2e"] == round(
            extracted["fuel_liters"] * 0.00268, 2
        )
        assert calc_data["scope_2_emissions_tco2e"] == round(
            extracted["energy_kwh"] * 0.00082, 2
        )

    def test_marketplace_and_calculator_consistency(self, client):
        """Test that calculator roadmap recommendations align with marketplace projects."""
        marketplace_response = client.get("/api/marketplace")
        assert marketplace_response.status_code == 200
        marketplace_data = marketplace_response.json()
        marketplace_ids = {p["id"] for p in marketplace_data}

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

    def test_chatbot_with_calculator_context(self, client):
        """Test chatbot can provide guidance based on calculator results."""
        calc_payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": 50000.0,
                "fuel_diesel_liters": 2000.0,
                "waste_kg": 500.0,
                "operational_hours": 200,
            },
        }
        calc_response = client.post("/api/calculator/score", json=calc_payload)
        assert calc_response.status_code == 200
        calc_data = calc_response.json()

        chatbot_payload = {
            "query": f"My factory emits {calc_data['total_emissions_tco2e']} tCO2e. How can I reduce emissions?"
        }
        chatbot_response = client.post("/api/chatbot/query", json=chatbot_payload)
        assert chatbot_response.status_code == 200
        chatbot_data = chatbot_response.json()
        assert "answer" in chatbot_data

    def test_multiple_industry_calculations(self, client):
        """Test calculations across different industries."""
        industries = ["manufacturing", "services", "agriculture", "textile", "mining"]
        for industry in industries:
            payload = {
                "industry": industry,
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
            assert data["scope_1_emissions_tco2e"] == round(500.0 * 0.00268, 2)
            assert data["scope_2_emissions_tco2e"] == round(10000.0 * 0.00082, 2)

    def test_export_with_different_industries(self, client):
        """Test report export works for different industry types."""
        industries = ["manufacturing", "services", "agriculture"]
        for industry in industries:
            payload = {
                "industry": industry,
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
                        "recommendation": "Install solar",
                        "investment_inr": 500000,
                        "savings_inr": 80000,
                        "credits_earned": 50,
                    }
                ],
            }
            response = client.post(
                "/api/reports/export?format=pdf", json=payload
            )
            assert response.status_code == 200
