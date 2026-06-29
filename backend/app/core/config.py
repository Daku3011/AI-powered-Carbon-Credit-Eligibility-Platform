import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Defaults for Carbon Calculator
    DIESEL_EMISSION_FACTOR: float = 0.00268       # tCO2e per Liter
    INDIA_GRID_EMISSION_FACTOR: float = 0.00082   # tCO2e per kWh
    CARBON_CREDIT_PRICE_INR: float = 800.0        # INR per credit (approx. $10 USD)

    class Config:
        env_file = ".env"

settings = Settings()
