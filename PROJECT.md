# Project: AI-powered Carbon Intelligence Platform

## Architecture
- **Frontend**: Next.js 16 (React 19, TypeScript, Tailwind CSS v4) with shadcn/ui components (base-ui based).
- **Backend**: FastAPI (Python) for business logic, OCR, calculator, RAG chatbot, and report generation.
- **Database**: SQLite for persistent storage of user inputs, eligibility scores, and marketplace status. Completely self-contained.
- **OCR & RAG**: Google Gemini API for document analysis/OCR and RAG queries, with a self-contained local vector index (using numpy/embeddings) stored in-memory.
- **Exports**: openpyxl (Excel) and reportlab (PDF) for document exports.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | E2E Test Suite | Design E2E test harness and implement comprehensive test cases (Tiers 1-4) | None | DONE |
| 2 | Backend Core & Calculator | Set up FastAPI backend, SQLite database schemas, Scope 1 & 2 carbon accounting formulas, and AI eligibility scoring engine | None | DONE |
| 3 | AI OCR & RAG Chatbot | Implement Gemini API OCR invoice processing and numpy-based RAG chatbot with Indian policy knowledge base | M2 | DONE |
| 4 | PDF & Excel Reporting | Implement PDF (reportlab) and Excel (openpyxl) report generators | M2 | DONE |
| 5 | Frontend UI & Dashboard | Build Next.js application with tailored industry questionnaires, benchmarking charts, and chatbot page | M2, M3, M4 | DONE |
| 6 | E2E Integration & Verification | Integrate frontend with backend, pass all E2E tests, and perform adversarial coverage hardening (Tier 5) | M1, M5 | DONE |

## Code Layout
```
ai_carbon_credits/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py           # FastAPI Entrypoint (lifespan, CORS, router mounting)
│   │   ├── core/             # Configuration (pydantic-settings), DB connection (SQLAlchemy)
│   │   │   ├── config.py     # Settings: DATABASE_URL, GEMINI_API_KEY, emission factors
│   │   │   └── database.py   # SQLAlchemy engine, session, Base
│   │   ├── api/              # API router endpoints
│   │   │   ├── calculator.py # POST /api/calculator/score
│   │   │   ├── ocr.py        # POST /api/ocr
│   │   │   ├── chatbot.py    # POST /api/chatbot/query
│   │   │   ├── marketplace.py# GET /api/marketplace
│   │   │   └── reports.py    # POST /api/reports/export?format=pdf|xlsx
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── calculation.py# CalculationRecord, RoadmapRecommendation
│   │   │   └── marketplace.py# MarketplaceProject
│   │   └── services/         # Business logic
│   │       ├── calculator.py # Carbon calculation & eligibility scoring
│   │       ├── roadmap.py    # Multi-year reduction roadmap generation
│   │       ├── ocr.py        # Gemini API OCR with fallback
│   │       ├── chatbot.py    # numpy-based RAG chatbot with knowledge base
│   │       ├── report_pdf.py # PDF generation (reportlab)
│   │       └── report_excel.py# Excel generation (openpyxl)
│   ├── tests/                # Unit/Integration tests
│   ├── docs/                 # (empty - knowledge base docs go here)
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js Frontend
│   ├── src/
│   │   ├── app/              # Page routes (App Router)
│   │   │   ├── page.tsx      # Home page with feature cards
│   │   │   ├── calculator/   # Carbon calculator with OCR upload
│   │   │   │   ├── page.tsx
│   │   │   │   └── results/page.tsx
│   │   │   ├── marketplace/  # Decarbonization project marketplace
│   │   │   ├── dashboard/    # Benchmarking charts (ApexCharts)
│   │   │   ├── chatbot/      # AI Carbon Consultant chatbot
│   │   │   ├── layout.tsx    # Root layout with Navbar
│   │   │   └── globals.css   # Global styles
│   │   ├── components/       # UI components
│   │   │   ├── navbar.tsx    # Navigation bar
│   │   │   └── ui/           # shadcn/ui components (base-ui based)
│   │   └── lib/              # Client utilities
│   │       ├── api.ts        # API client (configurable via NEXT_PUBLIC_API_URL)
│   │       └── utils.ts      # cn() utility
│   ├── package.json          # Node dependencies
│   └── tailwind.config.js    # Styling configuration
├── docs/                     # Documentation (architecture, API, deployment guides)
├── tests_e2e/                # Dual-track opaque-box E2E test suite
│   ├── mock_server.py        # Mock FastAPI server mimicking API responses
│   ├── conftest.py           # Pytest fixtures (base_url, httpx client, health wait)
│   ├── run_e2e.py            # Python E2E runner (starts mock server, runs pytest)
│   ├── run_e2e.sh            # Bash E2E runner
│   ├── tier1_feature_coverage/  # Basic endpoint functionality tests
│   ├── tier2_boundary/          # Validation, overflow, empty input tests
│   ├── tier3_cross_feature/     # Data flow and state consistency tests
│   ├── tier4_real_world/        # Comprehensive user journey tests
│   └── test_adversarial_mock.py # Adversarial mock server tests
└── PROJECT.md                # Project architecture and tracking
```

## Interface Contracts
### 1. OCR Document Extraction
- **Endpoint**: `POST /api/ocr`
- **Request**: Multipart Form Data (file: PDF/PNG/JPG)
- **Response**:
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

### 2. Carbon Calculation & Eligibility Scoring
- **Endpoint**: `POST /api/calculator/score`
- **Request**:
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
- **Response**:
  ```json
  {
    "scope_1_emissions_tco2e": 1.21,
    "scope_2_emissions_tco2e": 10.25,
    "total_emissions_tco2e": 11.46,
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
  ```

### 3. AI Carbon Consultant Chatbot
- **Endpoint**: `POST /api/chatbot/query`
- **Request**:
  ```json
  {
    "query": "What is the procedure for registering a solar PV project under the Indian carbon market?"
  }
  ```
- **Response**:
  ```json
  {
    "query": "What is the procedure for registering a solar PV project under the Indian carbon market?",
    "answer": "To register a solar PV project under the Indian Carbon Market (ICM)...",
    "sources": ["Indian Carbon Market Draft Policy 2023.pdf"]
  }
  ```

### 4. Marketplace Projects
- **Endpoint**: `GET /api/marketplace`
- **Response**:
  ```json
  [
    {
      "id": "solar_transition",
      "title": "Solar PV Transition",
      "description": "Replace grid power with rooftop solar panels",
      "cost_inr": 500000,
      "roi_pct": 16.0,
      "payback_years": 6.2,
      "credit_potential": 50
    }
  ]
  ```

### 5. PDF & Excel Exports
- **Endpoint**: `POST /api/reports/export?format=pdf` or `POST /api/reports/export?format=xlsx`
- **Request**: Same payload as `POST /api/calculator/score` plus the generated roadmap and eligibility score (including scope_1, scope_2, total fields).
- **Response**: File download stream (PDF or Excel based on query parameter).
