# Agent Instructions

## Project Overview
AI-powered Carbon Intelligence Platform for Indian MSMEs. FastAPI backend (Python) + Next.js frontend (TypeScript, Tailwind, shadcn/ui). SQLite database. Google Gemini API for OCR/RAG.

## Quick Commands

### Backend Tests (unit/integration)
```bash
cd backend && python -m pytest tests/ -v
```

### E2E Tests (mock server)
```bash
# Starts mock server on :8000, runs pytest, then shuts down
./tests_e2e/run_e2e.sh
# Or pass specific tests:
./tests_e2e/run_e2e.sh tests_e2e/tier1_feature_coverage/
```

### Run Backend Server
```bash
cd backend && uvicorn app.main:app --reload --port 8000
```

### Run Frontend
```bash
cd frontend && npm run dev
# Frontend runs on http://localhost:3000
# Backend API expected on http://localhost:8000
```

### Frontend Build & Lint
```bash
cd frontend && npm run build
cd frontend && npm run lint
```

## Architecture Notes

- **Backend entrypoint**: `backend/app/main.py` (FastAPI app with lifespan)
- **Frontend entrypoint**: `frontend/src/app/layout.tsx` (Next.js App Router)
- **Database**: SQLite at `backend/database.db` (auto-created on startup)
- **E2E tests use a separate mock server** (`tests_e2e/mock_server.py`) that mimics API responses - not the real backend
- **M3 (OCR/RAG) is IN_PROGRESS** - Gemini API integration incomplete
- **Frontend pages**: `/calculator`, `/marketplace`, `/dashboard`, `/chatbot`

## Key Conventions

- Backend uses **pydantic-settings** for config; env vars in `.env` (not committed)
- `GEMINI_API_KEY` is required for OCR/chatbot features but not for calculator
- E2E conftest waits for `/health` endpoint with 15s timeout before tests run
- Unit tests override DB dependency with test SQLite instance (`test.db`)
- Carbon emission factors hardcoded in `backend/app/core/config.py` - not from external API
- Frontend uses **shadcn/ui** components (base-ui based) - no `asChild` prop, use `render` instead
- Frontend API client at `frontend/src/lib/api.ts` - configurable via `NEXT_PUBLIC_API_URL`

## Testing Quirks

- E2E mock server responds to filenames containing "invalid", "zero", "empty" for boundary testing
- E2E tests hit mock server (port 8000), NOT the real backend
- `pytest.ini` at repo root sets `pythonpath = .` - run pytest from repo root
- Backend unit tests create/destroy `test.db` per test function

## Common Pitfalls

- Don't run E2E tests against real backend without mocking Gemini API calls
- `database.db` is gitignored but schema auto-migrates on startup
- Marketplace data is seeded on first run - deleting `database.db` re-seeds
- Frontend connects to real backend by default - OCR/chatbot features need M3 completion
