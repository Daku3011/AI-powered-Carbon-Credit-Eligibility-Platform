# AI-powered Carbon Intelligence Platform

An AI-powered Carbon Intelligence Platform designed for Indian MSMEs (Micro, Small and Medium Enterprises) to measure, reduce, and monetize their carbon footprint through carbon credits.

## Features

- **Carbon Calculator** -- Calculate Scope 1 (direct fuel combustion) and Scope 2 (electricity) emissions with AI-powered eligibility scoring for carbon credit monetization.
- **OCR Invoice Processing** -- Upload electricity bills or fuel invoices (PDF/PNG/JPG) for automatic metric extraction via Google Gemini API with fallback parser.
- **AI Carbon Consultant** -- RAG-based chatbot providing answers about Indian carbon markets, policies, and registration processes.
- **Project Marketplace** -- Browse decarbonization projects (solar, LED, HVAC, waste heat recovery, biomass) with ROI, payback periods, and carbon credit potential.
- **Benchmarking Dashboard** -- Interactive charts comparing emissions against industry averages using ApexCharts.
- **PDF & Excel Reports** -- Export comprehensive carbon reports with emissions data, eligibility scores, and multi-year reduction roadmaps.

## Architecture

```
                    +-----------------+
                    |   Frontend      |
                    |  Next.js 16     |
                    |  Tailwind CSS   |
                    |  shadcn/ui      |
                    +--------+--------+
                             |
                             | HTTP API
                             v
                    +--------+--------+
                    |    Backend      |
                    |   FastAPI       |
                    |   SQLite DB     |
                    +--------+--------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
     +--------+---+  +------+-----+  +-----+------+
     | Calculator  |  | OCR/RAG    |  | Reports    |
     | Scoring     |  | Gemini API |  | PDF/Excel  |
     +-------------+  +------------+  +------------+
```

## Tech Stack

| Layer     | Technology                                    |
|-----------|-----------------------------------------------|
| Frontend  | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui (base-ui) |
| Backend   | FastAPI, SQLAlchemy, Pydantic, Python 3.11+   |
| Database  | SQLite (auto-created, self-contained)          |
| AI/OCR    | Google Gemini API (gemini-2.0-flash)           |
| Charts    | ApexCharts (react-apexcharts)                 |
| Reports   | reportlab (PDF), openpyxl (Excel)             |
| Testing   | pytest, httpx                                 |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (with npm)
- (Optional) Google Gemini API key for OCR/chatbot features

### 1. Clone and Setup

```bash
git clone <repo-url> && cd ai_carbon_credits
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file (optional - needed for OCR/chatbot)
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend runs on `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` and connects to the backend at `http://localhost:8000`.

### 4. Run Tests

```bash
# Unit/Integration tests (from repo root)
cd backend && python -m pytest tests/ -v

# E2E tests (starts mock server, runs pytest, shuts down)
./tests_e2e/run_e2e.sh
```

## Environment Variables

| Variable             | Required | Default                    | Description                              |
|----------------------|----------|----------------------------|------------------------------------------|
| `GEMINI_API_KEY`     | No*      | `""`                       | Google Gemini API key for OCR/chatbot    |
| `DATABASE_URL`       | No       | `sqlite:///./database.db`  | SQLite connection string                 |
| `NEXT_PUBLIC_API_URL`| No       | `http://localhost:8000`    | Backend API URL for frontend             |

*OCR and chatbot features require a valid `GEMINI_API_KEY`. The calculator and marketplace work without it.

## API Endpoints

| Method | Endpoint                     | Description                              |
|--------|------------------------------|------------------------------------------|
| GET    | `/health`                    | Health check                             |
| POST   | `/api/calculator/score`      | Calculate emissions and eligibility      |
| POST   | `/api/ocr`                   | Extract data from uploaded invoice       |
| POST   | `/api/chatbot/query`         | Query the AI Carbon Consultant           |
| GET    | `/api/marketplace`           | List decarbonization projects            |
| POST   | `/api/reports/export?format=pdf`  | Download PDF report                 |
| POST   | `/api/reports/export?format=xlsx` | Download Excel report                |

## Project Structure

```
ai_carbon_credits/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py           # FastAPI app with lifespan, CORS, router mounting
│   │   ├── core/             # Config (pydantic-settings), DB (SQLAlchemy)
│   │   ├── api/              # API endpoints
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── models/           # SQLAlchemy ORM models
│   │   └── services/         # Business logic
│   ├── tests/                # Unit/Integration tests
│   └── requirements.txt
├── frontend/                 # Next.js Frontend
│   ├── src/app/              # Page routes (App Router)
│   ├── src/components/       # UI components (shadcn/ui)
│   ├── src/lib/              # API client, utilities
│   └── package.json
├── docs/                     # Documentation
├── tests_e2e/                # E2E test suite (4 tiers + adversarial)
├── PROJECT.md                # Architecture and milestone tracking
└── README.md                 # This file
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) -- System design and data flow
- [API Reference](docs/API.md) -- Detailed endpoint documentation
- [Deployment Guide](docs/DEPLOYMENT.md) -- Local development and deployment
- [Developer Onboarding](docs/ONBOARDING.md) -- Setup and coding conventions

## License

Proprietary -- Internal use only.
