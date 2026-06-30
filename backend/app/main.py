from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import SessionLocal, engine, Base
from app.core.logging_config import setup_logging, log_requests_middleware
from app.api.calculator import router as calculator_router
from app.api.marketplace import router as marketplace_router, DEFAULT_PROJECTS
from app.api.ocr import router as ocr_router
from app.api.chatbot import router as chatbot_router
from app.api.reports import router as reports_router
from app.models.marketplace import MarketplaceProject

# Initialize structured logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Seed if empty
    db = SessionLocal()
    try:
        if not db.query(MarketplaceProject).first():
            for p_data in DEFAULT_PROJECTS:
                db.add(MarketplaceProject(**p_data))
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(
    title="AI-powered Carbon Intelligence Platform Backend",
    description="Core calculation and database service APIs",
    version="1.0.0",
    lifespan=lifespan
)

# Register request/response logging middleware
app.middleware("http")(log_requests_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator_router, prefix="/api")
app.include_router(marketplace_router, prefix="/api")
app.include_router(ocr_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "healthy"}
