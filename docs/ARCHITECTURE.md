# Architecture Guide

## Overview

The AI-powered Carbon Intelligence Platform is a full-stack web application designed for Indian MSMEs to measure, reduce, and monetize their carbon footprint. The system consists of a FastAPI backend, a Next.js frontend, and a SQLite database.

## System Components

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|    Frontend      |---->|    Backend       |---->|    Database      |
|  (Next.js 16)   |     |  (FastAPI)       |     |  (SQLite)        |
|  Port: 3000     |     |  Port: 8000      |     |  database.db     |
|                  |     |                  |     |                  |
+------------------+     +--------+---------+     +------------------+
                                  |
                       +----------+----------+
                       |          |          |
                       v          v          v
              +--------+--+ +----+-----+ +--+--------+
              | Gemini API| | Report   | | Knowledge |
              | (OCR/RAG) | | Generators| | Base     |
              +-----------+ +----------+ +-----------+
```

## Backend Architecture

### Entry Point: `backend/app/main.py`

- FastAPI application with lifespan handler
- Creates database tables on startup
- Seeds marketplace projects if empty
- Mounts all API routers under `/api` prefix
- CORS middleware allows all origins (development mode)

### Core Layer: `backend/app/core/`

- **config.py**: Pydantic Settings class loading from `.env` file
  - `DATABASE_URL`: SQLite connection string
  - `GEMINI_API_KEY`: Google Gemini API key
  - Emission factors: diesel (0.00268 tCO2e/L), India grid (0.00082 tCO2e/kWh)
  - Carbon credit price: 800 INR per credit
- **database.py**: SQLAlchemy engine with WAL mode, session factory, `get_db()` dependency

### API Layer: `backend/app/api/`

| Module         | Router Prefix    | Endpoints                        |
|----------------|------------------|----------------------------------|
| calculator.py  | `/calculator`    | `POST /score`                    |
| ocr.py         | `/ocr`           | `POST /` (multipart file upload) |
| chatbot.py     | `/chatbot`       | `POST /query`                    |
| marketplace.py | `/marketplace`   | `GET /`                          |
| reports.py     | `/reports`       | `POST /export?format=pdf\|xlsx`  |

### Services Layer: `backend/app/services/`

- **calculator.py**: Scope 1 (direct), 2 (indirect electricity) & 3 (indirect waste) emission calculations, AI eligibility scoring (readiness score, emissions rating, reduction potential, credit potential, confidence score)
- **roadmap.py**: Industry-aware 3-year reduction roadmap generation
- **ocr.py**: Google Gemini API OCR with JSON extraction and fallback to None
- **chatbot.py**: numpy-based TF-IDF vector store with embedded Indian carbon market knowledge base; Gemini API-enhanced answer generation with fallback
- **report_pdf.py**: PDF generation using reportlab with styled tables
- **report_excel.py**: Excel generation using openpyxl with formatted worksheets

### Models Layer: `backend/app/models/`

- **calculation.py**: `CalculationRecord` (industry, metrics, emissions, scores) with `RoadmapRecommendation` relationship (1:many)
- **marketplace.py**: `MarketplaceProject` (id, title, description, cost, ROI, payback, credit potential)

### Data Flow: Calculator Request

```
Client POST /api/calculator/score
  -> CalculatorRequest (industry, metrics)
  -> calculator service: compute scope_1, scope_2, scope_3, total
  -> calculator service: compute eligibility_score
  -> roadmap service: generate 3-year plan
  -> persist to SQLite (CalculationRecord + RoadmapRecommendations)
  -> return CalculatorResponse
```

### Data Flow: OCR Request

```
Client POST /api/ocr (multipart file)
  -> ocr service: send bytes to Gemini API
  -> Gemini extracts JSON with energy_kwh, fuel_liters, etc.
  -> ocr service: parse and return OCRResponse
  -> Client uses extracted data to pre-fill calculator form
```

### Data Flow: Chatbot Request

```
Client POST /api/chatbot/query
  -> chatbot service: embed query text (hash-based 256-dim vector)
  -> query embedded knowledge base (cosine similarity)
  -> retrieve top-3 matching documents
  -> send context + query to Gemini API for answer generation
  -> fallback: return raw context if Gemini unavailable
  -> return ChatbotResponse (answer + sources)
```

## Frontend Architecture

### Entry Point: `frontend/src/app/layout.tsx`

- Next.js App Router with Geist font family
- Root layout includes Navbar component
- Global CSS with Tailwind CSS v4

### Pages

| Route                    | Description                                  |
|--------------------------|----------------------------------------------|
| `/`                      | Home page with feature cards                 |
| `/calculator`            | Industry selector + manual/OCR data entry    |
| `/calculator/results`    | Emissions summary, eligibility score, roadmap|
| `/marketplace`           | Decarbonization project cards                |
| `/dashboard`             | Benchmarking charts (bar, donut, line)       |
| `/chatbot`               | AI Carbon Consultant chat interface          |

### API Client: `frontend/src/lib/api.ts`

- Configurable base URL via `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`)
- Typed interfaces for all request/response schemas
- Functions: `calculateScore()`, `getMarketplaceProjects()`, `queryChatbot()`, `uploadOcr()`, `exportReport()`

### State Management

- Calculator input stored in `localStorage` before redirect to results page
- Results page reads from `localStorage`, calls API, renders response
- Chatbot uses React `useState` for message history

## Testing Architecture

### Unit/Integration Tests: `backend/tests/`

- Test calculator, marketplace, and stress scenarios
- Override database dependency with test SQLite instance (`test.db`)
- Conftest provides `TestClient` and test database setup

### E2E Tests: `tests_e2e/`

- **Mock Server** (`mock_server.py`): FastAPI app mimicking API responses
- **4 Tiers**:
  - Tier 1: Basic endpoint functionality (feature coverage)
  - Tier 2: Validation, overflow, empty inputs (boundary cases)
  - Tier 3: Data flow and state consistency (cross-feature)
  - Tier 4: Comprehensive user journeys (real-world scenarios)
- **Adversarial Tests** (`test_adversarial_mock.py`): Port binding, overflow, validation bypass
- Tests run against mock server, NOT real backend
- Runner (`run_e2e.py` / `run_e2e.sh`): Starts mock server, waits for health, runs pytest, shuts down

### Database Schema

```sql
-- calculation_records
id INTEGER PRIMARY KEY
timestamp DATETIME
industry VARCHAR
electricity_kwh FLOAT
fuel_diesel_liters FLOAT
waste_kg FLOAT
operational_hours FLOAT
scope_1_emissions_tco2e FLOAT
scope_2_emissions_tco2e FLOAT
scope_3_emissions_tco2e FLOAT
total_emissions_tco2e FLOAT
readiness_score INTEGER
emissions_rating VARCHAR
reduction_potential_pct FLOAT
carbon_credit_potential FLOAT
projected_revenue_inr FLOAT
confidence_score FLOAT

-- roadmap_recommendations
id INTEGER PRIMARY KEY
calculation_record_id INTEGER FK->calculation_records.id
year INTEGER
recommendation VARCHAR
investment_inr FLOAT
savings_inr FLOAT
credits_earned FLOAT

-- marketplace_projects
id VARCHAR PRIMARY KEY
title VARCHAR
description VARCHAR
cost_inr FLOAT
roi_pct FLOAT
payback_years FLOAT
credit_potential FLOAT
```

## Key Design Decisions

1. **SQLite**: Chosen for zero-config, self-contained deployment. WAL mode enabled for concurrent reads.
2. **Gemini API with Fallback**: OCR and chatbot gracefully degrade if API key is missing or API fails.
3. **numpy Vector Store**: Lightweight RAG implementation without heavy ML dependencies. Hash-based embedding with cosine similarity.
4. **Mock E2E Server**: Allows testing API contracts without running real backend or depending on external services.
5. **localStorage for Calculator Flow**: Simple state passing between calculator input and results pages without backend session management.
