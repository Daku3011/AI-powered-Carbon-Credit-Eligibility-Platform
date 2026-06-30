# Deployment Guide

## Local Development

### Prerequisites

- **Python 3.11+** with `pip`
- **Node.js 18+** with `npm`
- **Git**

### Step 1: Clone the Repository

```bash
git clone <repo-url>
cd ai_carbon_credits
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file (optional but recommended)
cat > .env << EOF
DATABASE_URL=sqlite:///./database.db
GEMINI_API_KEY=your_google_gemini_api_key
EOF

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

- API docs: `http://localhost:8000/docs` (Swagger UI)
- Alternative docs: `http://localhost:8000/redoc` (ReDoc)

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Step 4: Verify

1. Open `http://localhost:3000` in your browser
2. Navigate to the Calculator page and submit a calculation
3. Check the Backend health: `curl http://localhost:8000/health`

---

## Environment Variables

### Backend

| Variable         | Required | Default                    | Description                              |
|------------------|----------|----------------------------|------------------------------------------|
| `DATABASE_URL`   | No       | `sqlite:///./database.db`  | SQLAlchemy database URL                   |
| `GEMINI_API_KEY` | No*      | `""`                       | Google Gemini API key for OCR and chatbot |
| `MOCK_PORT`      | No       | `8001`                     | Port for E2E mock server (run_e2e.py)    |
| `MOCK_HOST`      | No       | `127.0.0.1`               | Host for E2E mock server                 |

*The calculator and marketplace endpoints work without `GEMINI_API_KEY`. OCR and chatbot endpoints will return error responses if the key is missing.

### Frontend

| Variable              | Required | Default               | Description                    |
|-----------------------|----------|-----------------------|--------------------------------|
| `NEXT_PUBLIC_API_URL` | No       | `http://localhost:8000` | Backend API base URL for the frontend |

---

## Dependencies

### Backend (`backend/requirements.txt`)

```
fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pytest>=7.0.0
httpx>=0.24.0
google-genai>=1.0.0
python-multipart>=0.0.6
reportlab>=4.0.0
openpyxl>=3.1.0
```

### Frontend (key dependencies)

- `next` 16.2.9 / `react` 19.2.4
- `tailwindcss` v4
- `@base-ui/react` (shadcn/ui base)
- `react-apexcharts` + `apexcharts` (charts)
- `lucide-react` (icons)

---

## Production Deployment

### Backend (Uvicorn with Gunicorn)

```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend (Next.js Build)

```bash
cd frontend
npm run build
npm start
# Serves on port 3000 by default
```

### Docker (Recommended for Production)

A Dockerfile can be created for each service. Example for backend:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Database

- **Engine**: SQLite with WAL journal mode
- **File**: `backend/database.db` (auto-created on first startup)
- **Schema**: Tables are created automatically via `Base.metadata.create_all()` in the lifespan handler on first startup. Note that SQLite does **not** auto-migrate existing tables if new columns (e.g. `scope_3_emissions_tco2e`) are added later.
- **Seeding**: Marketplace projects seeded automatically if table is empty.
- **Reset / Schema Migration**: Delete `database.db` and restart the backend to force it to recreate the tables with the updated schema and re-seed the marketplace projects.

### SQLite Configuration

```python
# Applied on every connection:
PRAGMA journal_mode=WAL
PRAGMA synchronous=NORMAL
connect_args: check_same_thread=False, timeout=30
```

---

## Running Tests

### Unit/Integration Tests

```bash
cd backend
python -m pytest tests/ -v
```

Tests use a separate `test.db` SQLite database that is created and destroyed per test function.

### E2E Tests

```bash
# Using the Python runner (starts mock server, runs pytest, shuts down)
python3 tests_e2e/run_e2e.py

# Or using the bash runner
./tests_e2e/run_e2e.sh

# Run specific tier
./tests_e2e/run_e2e.sh tests_e2e/tier1_feature_coverage/
```

**Important**: E2E tests run against a mock server (`tests_e2e/mock_server.py`) on port 8001 (configurable via `MOCK_PORT`). They do NOT test the real backend.

### Test Tiers

| Tier | Name                  | Focus                                    |
|------|-----------------------|------------------------------------------|
| 1    | Feature Coverage      | Basic endpoint functionality             |
| 2    | Boundary Cases        | Validation, overflow, empty inputs       |
| 3    | Cross-Feature         | Data flow and state consistency          |
| 4    | Real-World            | Comprehensive user journeys              |

---

## Troubleshooting

### Common Issues

**OperationalError: table calculation_records has no column named scope_3_emissions_tco2e**
- **Cause**: The database schema in the code was updated to include new columns (like Scope 3 waste emissions), but the database already existed on disk. SQLite's schema creation does not update existing tables.
- **Fix**: Stop the backend, run `rm backend/database.db` to delete the old SQLite database file, and restart the backend. The server will recreate the database with all correct columns and re-seed the marketplace projects.

**Port 8000 already in use**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill it or use a different port
uvicorn app.main:app --reload --port 8001
```

**E2E mock server fails to start**:
- Default E2E mock port is 8001 (configurable via `MOCK_PORT`)
- If a Docker container occupies port 8000, E2E tests use 8001 instead
- Check `.mock_server.log` for errors

**OCR/chatbot returns errors**:
- Ensure `GEMINI_API_KEY` is set in `backend/.env`
- Verify the API key is valid at Google AI Studio

**Frontend cannot connect to backend**:
- Ensure backend is running on port 8000
- Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` if using a different port
- Check CORS configuration in `backend/app/main.py`
