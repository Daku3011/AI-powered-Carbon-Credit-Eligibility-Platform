from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.core.database import Base

class CalculationRecord(Base):
    __tablename__ = "calculation_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    industry = Column(String, nullable=False)
    
    electricity_kwh = Column(Float, nullable=False)
    fuel_diesel_liters = Column(Float, nullable=False)
    waste_kg = Column(Float, nullable=False)
    operational_hours = Column(Float, nullable=False)
    
    scope_1_emissions_tco2e = Column(Float, nullable=False)
    scope_2_emissions_tco2e = Column(Float, nullable=False)
    total_emissions_tco2e = Column(Float, nullable=False)
    
    readiness_score = Column(Integer, nullable=False)
    emissions_rating = Column(String, nullable=False)
    reduction_potential_pct = Column(Float, nullable=False)
    carbon_credit_potential = Column(Float, nullable=False)
    projected_revenue_inr = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    roadmap = relationship("RoadmapRecommendation", back_populates="record", cascade="all, delete-orphan")

class RoadmapRecommendation(Base):
    __tablename__ = "roadmap_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    calculation_record_id = Column(Integer, ForeignKey("calculation_records.id"), nullable=False)
    year = Column(Integer, nullable=False)
    recommendation = Column(String, nullable=False)
    investment_inr = Column(Float, nullable=False)
    savings_inr = Column(Float, nullable=False)
    credits_earned = Column(Float, nullable=False)
    
    record = relationship("CalculationRecord", back_populates="roadmap")
