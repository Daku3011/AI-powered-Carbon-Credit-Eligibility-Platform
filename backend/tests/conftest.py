import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    
    # Seed test database
    from app.models.marketplace import MarketplaceProject
    from app.api.marketplace import DEFAULT_PROJECTS
    db = TestingSessionLocal()
    try:
        if not db.query(MarketplaceProject).first():
            for p_data in DEFAULT_PROJECTS:
                db.add(MarketplaceProject(**p_data))
            db.commit()
    finally:
        db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)
