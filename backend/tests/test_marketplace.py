import pytest

def test_marketplace_projects_retrieval_and_seeding(client):
    response = client.get("/api/marketplace")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["id"] == "solar_transition"
    assert data[0]["title"] == "Solar PV Transition"

def test_marketplace_projects_returns_valid_schema(client):
    response = client.get("/api/marketplace")
    assert response.status_code == 200
    data = response.json()
    for project in data:
        assert "id" in project
        assert "title" in project
        assert "description" in project
        assert "cost_inr" in project
        assert "roi_pct" in project
        assert "payback_years" in project
        assert "credit_potential" in project
        assert isinstance(project["cost_inr"], (int, float))
        assert isinstance(project["roi_pct"], (int, float))
        assert isinstance(project["payback_years"], (int, float))
        assert isinstance(project["credit_potential"], (int, float))
