# Developer Onboarding Guide

## Welcome

This guide will help you get started as a developer on the AI-powered Carbon Intelligence Platform project.

## Project Overview

We are building an AI-powered platform that helps Indian MSMEs measure, reduce, and monetize their carbon footprint. The platform includes:

- A **FastAPI backend** with SQLite database
- A **Next.js frontend** with Tailwind CSS and shadcn/ui
- **Google Gemini API** integration for OCR and RAG chatbot
- **E2E test suite** with 4 tiers of test coverage

## Quick Setup

```bash
# 1. Clone the repo
git clone <repo-url> && cd ai_carbon_credits

# 2. Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend && npm install && npm run dev

# 4. Verify
curl http://localhost:8000/health
open http://localhost:3000
```

## Project Structure

```
ai_carbon_credits/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── core/             # Config, database
│   │   ├── api/              # API route handlers
│   │   ├── schemas/          # Pydantic models (request/response)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   └── services/         # Business logic
│   ├── tests/                # Unit/integration tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Page routes (App Router)
│   │   ├── components/       # React components
│   │   └── lib/              # API client, utilities
│   └── package.json
├── docs/                     # Documentation
├── tests_e2e/                # E2E test suite
├── TASK_BOARD.md             # Agent coordination board
├── PROJECT.md                # Architecture & milestones
└── AGENTS.md                 # Agent instructions
```

## Coding Conventions

### Backend (Python)

- **Style**: Follow PEP 8
- **Type Hints**: Use type hints on all function signatures
- **Pydantic**: Use Pydantic models for all request/response schemas
- **Error Handling**: Services return dicts; API routers handle serialization
- **Database**: Use SQLAlchemy ORM; never raw SQL in services
- **Config**: Use `pydantic-settings` via `app.core.config.settings`
- **Testing**: Create `test.db` per test function; clean up after

```python
# Good example
from app.core.config import settings

def calculate_emissions(kwh: float, diesel: float) -> float:
    scope_1 = diesel * settings.DIESEL_EMISSION_FACTOR
    scope_2 = kwh * settings.INDIA_GRID_EMISSION_FACTOR
    return round(scope_1 + scope_2, 2)
```

### Frontend (TypeScript/React)

- **Framework**: Next.js 16 App Router with React 19
- **Styling**: Tailwind CSS v4 with shadcn/ui components
- **Components**: Place reusable UI in `src/components/ui/`
- **Pages**: Place page components in `src/app/<route>/page.tsx`
- **API Client**: Use typed functions from `src/lib/api.ts`
- **State**: Use `useState`/`useEffect`; `localStorage` for cross-page state
- **Build Check**: Always run `npm run build` before committing

```typescript
// Good example
import { calculateScore, type ScoreRequest } from "@/lib/api";

const handleCalculate = async (data: ScoreRequest) => {
  const result = await calculateScore(data);
  // result is fully typed
};
```

### Testing

- **Unit Tests**: Place in `backend/tests/`; use `pytest` with `TestClient`
- **E2E Tests**: Place in `tests_e2e/tier*/`; use `httpx` client against mock server
- **Test Markers**: Use `@pytest.mark.tier1`, `@pytest.mark.calculator`, etc.
- **Mock Server**: Do NOT modify `mock_server.py` without updating test assertions

## Key Files to Know

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app setup, CORS, router mounting |
| `backend/app/core/config.py` | All settings and emission factors |
| `backend/app/services/calculator.py` | Core calculation and scoring logic |
| `backend/app/services/chatbot.py` | RAG knowledge base and Gemini integration |
| `frontend/src/lib/api.ts` | Typed API client for all endpoints |
| `frontend/src/app/calculator/page.tsx` | Main calculator form with OCR |
| `tests_e2e/mock_server.py` | Mock API for E2E tests |
| `TASK_BOARD.md` | Task coordination board |
| `AGENTS.md` | Agent instructions and conventions |

## Workflow

1. **Read TASK_BOARD.md** at session start to find your assigned task
2. **Update Status** to `in-progress` when starting work
3. **Write code** following the conventions above
4. **Run tests** before marking as done:
   - Backend: `cd backend && python -m pytest tests/ -v`
   - E2E: `./tests_e2e/run_e2e.sh`
   - Frontend: `cd frontend && npm run build && npm run lint`
5. **Update Status** to `done` with notes in TASK_BOARD.md
6. **Docs Engineer** will update documentation automatically

## Environment Setup

### Required
- Python 3.11+, Node.js 18+, pip, npm

### Optional (for full functionality)
- Google Gemini API key (for OCR and chatbot)
  - Get one at: https://aistudio.google.com/apikey
  - Set in `backend/.env`: `GEMINI_API_KEY=your_key_here`

### Database
- SQLite (no installation needed)
- Database file: `backend/database.db` (auto-created)
- Delete to reset/seeding marketplace data

## Getting Help

- Read `AGENTS.md` for agent-specific instructions
- Check `docs/API.md` for endpoint details
- Check `docs/ARCHITECTURE.md` for system design
- Check `docs/DEPLOYMENT.md` for setup and troubleshooting
