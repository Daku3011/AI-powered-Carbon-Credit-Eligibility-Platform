# API Reference

Base URL: `http://localhost:8000`

## Health Check

```
GET /health
```

**Response** `200 OK`:
```json
{
  "status": "healthy"
}
```

---

## Calculator

### Calculate Emissions & Eligibility

```
POST /api/calculator/score
```

**Request Body**:
```json
{
  "industry": "manufacturing",
  "metrics": {
    "electricity_kwh": 12500.5,
    "fuel_diesel_liters": 450.0,
    "waste_kg": 120.0,
    "operational_hours": 160
  }
}
```

| Field                      | Type   | Required | Constraints       | Description                        |
|----------------------------|--------|----------|-------------------|------------------------------------|
| `industry`                 | string | Yes      | max 100 chars     | Industry type (manufacturing, services, etc.) |
| `metrics.electricity_kwh`  | float  | Yes      | >= 0, finite      | Monthly electricity consumption    |
| `metrics.fuel_diesel_liters`| float | Yes      | >= 0, finite      | Monthly diesel consumption         |
| `metrics.waste_kg`         | float  | Yes      | >= 0, finite      | Monthly waste generation           |
| `metrics.operational_hours`| float  | Yes      | >= 0, finite      | Monthly operational hours          |

**Response** `200 OK`:
```json
{
  "scope_1_emissions_tco2e": 1.21,
  "scope_2_emissions_tco2e": 10.25,
  "scope_3_emissions_tco2e": 0.0,
  "total_emissions_tco2e": 11.46,
  "eligibility_score": {
    "readiness_score": 77,
    "emissions_rating": "Medium",
    "reduction_potential_pct": 23.6,
    "carbon_credit_potential": 150.0,
    "projected_revenue_inr": 120000.0,
    "confidence_score": 0.85
  },
  "roadmap": [
    {
      "year": 1,
      "recommendation": "Install rooftop solar",
      "investment_inr": 500000.0,
      "savings_inr": 80000.0,
      "credits_earned": 50.0
    },
    {
      "year": 2,
      "recommendation": "Implement waste heat recovery system",
      "investment_inr": 1200000.0,
      "savings_inr": 216000.0,
      "credits_earned": 120.0
    },
    {
      "year": 3,
      "recommendation": "Establish zero-waste-to-landfill recycling program",
      "investment_inr": 50000.0,
      "savings_inr": 12000.0,
      "credits_earned": 10.0
    }
  ]
}
```

**Emission Factors**:
- Diesel: 0.00268 tCO2e per liter (Scope 1)
- India Grid Electricity: 0.00082 tCO2e per kWh (Scope 2)

**Notes**:
- All calculation records are persisted to SQLite
- Roadmap is industry-aware (manufacturing gets different recommendations than services)
- Eligibility score includes readiness (10-95), emissions rating (Low/Medium/High), and confidence (0.50-0.95)

---

## OCR

### Extract Invoice Data

```
POST /api/ocr
Content-Type: multipart/form-data
```

**Request**: Multipart form with `file` field (PDF, PNG, JPG).

**Response** `200 OK` (success):
```json
{
  "success": true,
  "extracted_data": {
    "energy_kwh": 12500.5,
    "fuel_liters": 450.0,
    "cost": 1250.0,
    "fuel_type": "diesel",
    "billing_period": "2026-05"
  }
}
```

**Response** `200 OK` (failure):
```json
{
  "success": false,
  "extracted_data": null,
  "error": "Failed to extract data from the uploaded document."
}
```

**Notes**:
- Uses Google Gemini API (`gemini-2.0-flash` model) for OCR
- Falls back gracefully if API key is missing or API call fails
- Returns zero values for unfound fields

---

## Chatbot

### Query AI Carbon Consultant

```
POST /api/chatbot/query
```

**Request Body**:
```json
{
  "query": "What is the procedure for registering a solar PV project under the Indian carbon market?"
}
```

| Field   | Type   | Required | Description         |
|---------|--------|----------|---------------------|
| `query` | string | Yes      | User's question     |

**Response** `200 OK`:
```json
{
  "query": "What is the procedure for registering a solar PV project under the Indian carbon market?",
  "answer": "To register a solar PV project under the Indian Carbon Market (ICM), the project developer must prepare a Project Design Document (PDD) demonstrating additionality, calculate baseline emissions, and submit to the Designated Operational Entity (DOE) for validation...",
  "sources": ["Indian Carbon Market Draft Policy 2023.pdf"]
}
```

**Notes**:
- RAG-based system with embedded knowledge base (6 documents on Indian carbon markets)
- Uses numpy TF-IDF vector store for document retrieval (top-3 matches)
- Gemini API generates answers from retrieved context
- Falls back to raw context snippet if Gemini API is unavailable
- Knowledge base covers: ICM policy, BEE guidelines, CII pricing, MoEFCC framework, verification standards

---

## Marketplace

### List Decarbonization Projects

```
GET /api/marketplace
```

**Response** `200 OK`:
```json
[
  {
    "id": "solar_transition",
    "title": "Solar PV Transition",
    "description": "Replace grid power with rooftop solar panels",
    "cost_inr": 500000.0,
    "roi_pct": 16.0,
    "payback_years": 6.2,
    "credit_potential": 50.0
  },
  {
    "id": "led_retrofit",
    "title": "LED Lighting Retrofit",
    "description": "Upgrade factory and office lighting to energy-efficient LED fixtures",
    "cost_inr": 100000.0,
    "roi_pct": 25.0,
    "payback_years": 4.0,
    "credit_potential": 15.0
  },
  {
    "id": "hvac_optimization",
    "title": "HVAC System Optimization",
    "description": "Install smart thermostats and variable speed drives for space cooling",
    "cost_inr": 300000.0,
    "roi_pct": 20.0,
    "payback_years": 5.0,
    "credit_potential": 25.0
  },
  {
    "id": "waste_heat_recovery",
    "title": "Waste Heat Recovery",
    "description": "Capture exhaust heat from manufacturing equipment for steam preheating",
    "cost_inr": 1200000.0,
    "roi_pct": 18.0,
    "payback_years": 5.5,
    "credit_potential": 120.0
  },
  {
    "id": "biomass_boiler",
    "title": "Biomass Boiler Upgrade",
    "description": "Convert fuel-oil or diesel boiler to fire agricultural waste and biomass briquettes",
    "cost_inr": 800000.0,
    "roi_pct": 22.0,
    "payback_years": 4.5,
    "credit_potential": 90.0
  }
]
```

**Notes**:
- Projects are seeded from `DEFAULT_PROJECTS` in `marketplace.py` on first run
- Deleting `database.db` re-seeds the marketplace data
- Data is served from SQLite (persisted)

---

## Reports

### Export PDF Report

```
POST /api/reports/export?format=pdf
Content-Type: application/json
```

### Export Excel Report

```
POST /api/reports/export?format=xlsx
Content-Type: application/json
```

**Request Body**:
```json
{
  "industry": "manufacturing",
  "metrics": {
    "electricity_kwh": 12500.5,
    "fuel_diesel_liters": 450.0,
    "waste_kg": 120.0,
    "operational_hours": 160
  },
  "eligibility_score": {
    "readiness_score": 77,
    "emissions_rating": "Medium",
    "reduction_potential_pct": 23.6,
    "carbon_credit_potential": 150.0,
    "projected_revenue_inr": 120000.0,
    "confidence_score": 0.85,
    "scope_1": 1.21,
    "scope_2": 10.25,
    "total": 11.46
  },
  "roadmap": [
    {
      "year": 1,
      "recommendation": "Install rooftop solar",
      "investment_inr": 500000.0,
      "savings_inr": 80000.0,
      "credits_earned": 50.0
    }
  ]
}
```

**Response** `200 OK`:
- `format=pdf`: `Content-Type: application/pdf`, file `carbon_report.pdf`
- `format=xlsx`: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, file `carbon_report.xlsx`

**Notes**:
- `format` query parameter must be exactly `pdf` or `xlsx` (validated with regex)
- Report includes: input metrics, emissions summary, eligibility score, and reduction roadmap
- PDF uses reportlab with styled tables (green/blue/orange/purple headers)
- Excel uses openpyxl with formatted headers and borders

---

## Error Responses

All endpoints return standard HTTP error codes:

| Code | Description                              |
|------|------------------------------------------|
| 200  | Success                                  |
| 422  | Validation error (invalid request body)  |
| 500  | Internal server error                    |

**Validation Error Example** (`422`):
```json
{
  "detail": [
    {
      "loc": ["body", "metrics", "electricity_kwh"],
      "msg": "Value should be greater than or equal to 0",
      "type": "value_error"
    }
  ]
}
```
