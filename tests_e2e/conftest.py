import os
import time
import pytest
import httpx

@pytest.fixture(scope="session")
def base_url() -> str:
    """Returns the base URL of the application under test."""
    url = os.getenv("APP_URL", "http://127.0.0.1:8000")
    # Strip trailing slash if present
    return url.rstrip("/")

@pytest.fixture(scope="session")
def client(base_url) -> httpx.Client:
    """Provides a synchronous HTTPX client configured with the base URL."""
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client

@pytest.fixture(scope="session")
def async_client(base_url) -> httpx.AsyncClient:
    """Provides an asynchronous HTTPX client configured with the base URL."""
    async def _async_client():
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            yield client
    return _async_client

@pytest.fixture(scope="session", autouse=True)
def wait_for_service(base_url):
    """
    Blocks until the target service is healthy and reachable, 
    with a timeout of 15 seconds.
    """
    health_url = f"{base_url}/health"
    start_time = time.time()
    timeout = 15.0
    
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(health_url)
            if response.status_code == 200:
                return
        except httpx.RequestError:
            pass
        time.sleep(0.5)
        
    pytest.fail(f"Target service at {base_url} did not become healthy in {timeout} seconds.")
