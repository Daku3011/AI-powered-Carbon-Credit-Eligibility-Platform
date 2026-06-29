from sqlalchemy import Column, String, Float
from app.core.database import Base

class MarketplaceProject(Base):
    __tablename__ = "marketplace_projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cost_inr = Column(Float, nullable=False)
    roi_pct = Column(Float, nullable=False)
    payback_years = Column(Float, nullable=False)
    credit_potential = Column(Float, nullable=False)
