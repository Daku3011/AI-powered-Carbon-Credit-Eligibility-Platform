import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Defaults for Carbon Calculator
    DIESEL_EMISSION_FACTOR: float = 0.00268       # tCO2e per Liter
    INDIA_GRID_EMISSION_FACTOR: float = 0.00082   # tCO2e per kWh
    WASTE_EMISSION_FACTOR: float = 0.00058        # tCO2e per kg (landfill methane)
    CARBON_CREDIT_PRICE_INR: float = 800.0        # INR per credit (approx. $10 USD)

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
