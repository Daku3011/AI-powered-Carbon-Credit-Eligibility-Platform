from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.marketplace import MarketplaceProjectSchema
from app.models.marketplace import MarketplaceProject

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

DEFAULT_PROJECTS = [
    {
        "id": "solar_transition",
        "title": "Solar PV Transition",
        "description": "Replace grid power with rooftop solar panels",
        "cost_inr": 500000.0,
        "roi_pct": 16.0,
        "payback_years": 6.2,
        "credit_potential": 50.0
    },
    {
        "id": "led_retrofit",
        "title": "LED Lighting Retrofit",
        "description": "Upgrade factory and office lighting to energy-efficient LED fixtures",
        "cost_inr": 100000.0,
        "roi_pct": 25.0,
        "payback_years": 4.0,
        "credit_potential": 15.0
    },
    {
        "id": "hvac_optimization",
        "title": "HVAC System Optimization",
        "description": "Install smart thermostats and variable speed drives for space cooling",
        "cost_inr": 300000.0,
        "roi_pct": 20.0,
        "payback_years": 5.0,
        "credit_potential": 25.0
    },
    {
        "id": "waste_heat_recovery",
        "title": "Waste Heat Recovery",
        "description": "Capture exhaust heat from manufacturing equipment for steam preheating",
        "cost_inr": 1200000.0,
        "roi_pct": 18.0,
        "payback_years": 5.5,
        "credit_potential": 120.0
    },
    {
        "id": "biomass_boiler",
        "title": "Biomass Boiler Upgrade",
        "description": "Convert fuel-oil or diesel boiler to fire agricultural waste and biomass briquettes",
        "cost_inr": 800000.0,
        "roi_pct": 22.0,
        "payback_years": 4.5,
        "credit_potential": 90.0
    }
]

@router.get("", response_model=List[MarketplaceProjectSchema])
def get_marketplace_projects(db: Session = Depends(get_db)):
    return db.query(MarketplaceProject).all()
