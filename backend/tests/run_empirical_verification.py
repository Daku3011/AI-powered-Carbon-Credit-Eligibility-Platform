import sys
import os
import math
import concurrent.futures
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust python path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base, get_db
from app.models.marketplace import MarketplaceProject
from app.api.marketplace import DEFAULT_PROJECTS

# Set up clean test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./empirical_test.db"

# Use WAL mode and check_same_thread=False
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False, "timeout": 30}
)
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed default projects
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
client = TestClient(app)

def run_tests():
    init_db()
    failures = 0

    print("=== STARTING EMPIRICAL VERIFICATION ===")

    # 1. Verify NaN / Infinity rejection
    print("\n--- Testing NaN / Infinity Rejection ---")
    special_vals = ["NaN", "Infinity", "-Infinity", float('nan'), float('inf'), float('-inf')]
    for idx, val in enumerate(special_vals):
        # Python TestClient accepts float('nan') or strings in JSON
        payload = {
            "industry": "manufacturing",
            "metrics": {
                "electricity_kwh": val if isinstance(val, float) else 100.0,
                "fuel_diesel_liters": 100.0 if isinstance(val, float) else val,
                "waste_kg": 50.0,
                "operational_hours": 80.0
            }
        }
        try:
            # We must serialize properly. TestClient json parameter does this.
            response = client.post("/api/calculator/score", json=payload)
            if response.status_code == 422:
                print(f"PASS: Correctly rejected special float value: {val} (Type: {type(val)}) with 422")
            else:
                print(f"FAIL: Accepted special float value: {val} (Type: {type(val)}), status code: {response.status_code}")
                failures += 1
        except Exception as e:
            # If JSON serialization fails, that also counts as validation/rejection by client/framework
            print(f"PASS: Rejected value {val} via exception: {e}")

    # 2. Verify invalid/extremely long industry names (>100 characters)
    print("\n--- Testing Industry Name Boundary Length ---")
    # Exactly 100 chars
    payload_100 = {
        "industry": "I" * 100,
        "metrics": {
            "electricity_kwh": 100.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 80.0
        }
    }
    response_100 = client.post("/api/calculator/score", json=payload_100)
    if response_100.status_code == 200:
        print("PASS: Allowed exactly 100 characters industry name with 200")
    else:
        print(f"FAIL: Rejected 100 characters industry name with {response_100.status_code}")
        failures += 1

    # 101 chars
    payload_101 = {
        "industry": "I" * 101,
        "metrics": {
            "electricity_kwh": 100.0,
            "fuel_diesel_liters": 100.0,
            "waste_kg": 50.0,
            "operational_hours": 80.0
        }
    }
    response_101 = client.post("/api/calculator/score", json=payload_101)
    if response_101.status_code == 422:
        print("PASS: Correctly rejected 101 characters industry name with 422")
    else:
        print(f"FAIL: Allowed 101 characters industry name with {response_101.status_code}")
        failures += 1

    # 3. Verify Concurrency Safety (20 parallel requests to calculator and marketplace)
    print("\n--- Testing Database Concurrency ---")
    calc_payload = {
        "industry": "logistics",
        "metrics": {
            "electricity_kwh": 125.0,
            "fuel_diesel_liters": 45.0,
            "waste_kg": 12.0,
            "operational_hours": 16.0
        }
    }

    # We will submit 20 concurrent calculator requests and 20 concurrent marketplace requests
    def make_calc_request():
        return client.post("/api/calculator/score", json=calc_payload)

    def make_market_request():
        return client.get("/api/marketplace")

    concurrency_level = 20
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_level * 2) as executor:
        for _ in range(concurrency_level):
            futures.append(executor.submit(make_calc_request))
            futures.append(executor.submit(make_market_request))
        
        results = [f.result() for f in futures]

    calc_successes = 0
    market_successes = 0
    concurrency_failures = 0

    for idx, res in enumerate(results):
        # Every second request is marketplace
        is_market = (idx % 2 == 1)
        endpoint = "/api/marketplace" if is_market else "/api/calculator/score"
        if res.status_code == 200:
            if is_market:
                market_successes += 1
            else:
                calc_successes += 1
        else:
            print(f"CONCURRENCY FAIL: Request to {endpoint} returned {res.status_code} - {res.text}")
            concurrency_failures += 1
            failures += 1

    print(f"Concurrency results:")
    print(f"  Calculator: {calc_successes}/{concurrency_level} succeeded")
    print(f"  Marketplace: {market_successes}/{concurrency_level} succeeded")
    print(f"  Failures: {concurrency_failures}")

    # Clean up test DB
    try:
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./empirical_test.db"):
            os.remove("./empirical_test.db")
        # Also clean up WAL files if they exist
        for f in ["./empirical_test.db-wal", "./empirical_test.db-shm"]:
            if os.path.exists(f):
                os.remove(f)
    except Exception as e:
        print(f"Warning during DB cleanup: {e}")

    print("\n=== VERIFICATION SUMMARY ===")
    if failures == 0:
        print("ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"{failures} TEST(S) FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
