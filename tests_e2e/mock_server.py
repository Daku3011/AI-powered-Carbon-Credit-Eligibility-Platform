import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="AI-powered Carbon Intelligence Platform E2E Mock Server",
    description="Mock implementation of core FastAPI APIs to support E2E tests",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---

class Metrics(BaseModel):
    electricity_kwh: float
    fuel_diesel_liters: float
    waste_kg: float
    operational_hours: int

class ScoreRequest(BaseModel):
    industry: str
    metrics: Metrics

class EligibilityScore(BaseModel):
    readiness_score: int
    emissions_rating: str
    reduction_potential_pct: float
    carbon_credit_potential: float
    projected_revenue_inr: float
    confidence_score: float

class RoadmapItem(BaseModel):
    year: int
    recommendation: str
    investment_inr: int
    savings_inr: int
    credits_earned: int

class ScoreResponse(BaseModel):
    scope_1_emissions_tco2e: float
    scope_2_emissions_tco2e: float
    total_emissions_tco2e: float
    eligibility_score: EligibilityScore
    roadmap: List[RoadmapItem]

class ChatbotRequest(BaseModel):
    query: str

class ChatbotResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]

class ProjectItem(BaseModel):
    id: str
    title: str
    description: str
    cost_inr: float
    roi_pct: float
    payback_years: float
    credit_potential: float

class ExportRequest(BaseModel):
    industry: str
    metrics: Metrics
    eligibility_score: EligibilityScore
    roadmap: List[RoadmapItem]


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    filename_lower = file.filename.lower()
    
    # Custom behaviors based on filename to support boundary/error testing
    if "invalid" in filename_lower:
        return {
            "success": False,
            "extracted_data": None,
            "error": "Failed to parse OCR invoice"
        }
    elif "zero" in filename_lower:
        return {
            "success": True,
            "extracted_data": {
                "energy_kwh": 0.0,
                "fuel_liters": 0.0,
                "cost": 0.0,
                "fuel_type": "none",
                "billing_period": "2026-05"
            }
        }
    elif "empty" in filename_lower:
        return {
            "success": True,
            "extracted_data": {}
        }
        
    return {
        "success": True,
        "extracted_data": {
            "energy_kwh": 12500.5,
            "fuel_liters": 450.0,
            "cost": 1250.0,
            "fuel_type": "diesel",
            "billing_period": "2026-05"
        }
    }

@app.post("/api/calculator/score", response_model=ScoreResponse)
def calculate_score(req: ScoreRequest):
    # Validation checks for boundary testing
    if req.metrics.electricity_kwh < 0 or req.metrics.fuel_diesel_liters < 0 or req.metrics.waste_kg < 0 or req.metrics.operational_hours < 0:
        raise HTTPException(status_code=422, detail="Metrics must be non-negative")
    
    if req.industry == "":
        raise HTTPException(status_code=422, detail="Industry cannot be empty")
        
    # Semi-dynamic calculation
    scope_1 = round(req.metrics.fuel_diesel_liters * 0.00268, 2)
    scope_2 = round(req.metrics.electricity_kwh * 0.00082, 2)
    total = round(scope_1 + scope_2, 2)
    
    # Mock eligibility scoring logic
    readiness = 78
    if total > 50:
        rating = "High"
        readiness = 45
    elif total > 10:
        rating = "Medium"
        readiness = 78
    else:
        rating = "Low"
        readiness = 90
        
    return ScoreResponse(
        scope_1_emissions_tco2e=scope_1,
        scope_2_emissions_tco2e=scope_2,
        total_emissions_tco2e=total,
        eligibility_score=EligibilityScore(
            readiness_score=readiness,
            emissions_rating=rating,
            reduction_potential_pct=25.0,
            carbon_credit_potential=round(total * 12.0, 1),
            projected_revenue_inr=round(total * 12.0 * 800, 2),
            confidence_score=0.85
        ),
        roadmap=[
            RoadmapItem(
                year=1,
                recommendation=f"Install rooftop solar for {req.industry} facility",
                investment_inr=500000,
                savings_inr=80000,
                credits_earned=50
            )
        ]
    )

@app.post("/api/chatbot/query", response_model=ChatbotResponse)
def chatbot_query(req: ChatbotRequest):
    if not req.query.strip():
        raise HTTPException(status_code=422, detail="Query cannot be empty")
        
    query_lower = req.query.lower()
    
    # Return different mock answers based on query keywords
    if "solar" in query_lower:
        answer = "To register a solar PV project under the Indian Carbon Market (ICM), developers must submit a project design document (PDD) detailing additionality, baseline emissions, and monitoring methodology to the National Carbon Registry."
        sources = ["Indian Carbon Market Draft Policy 2023.pdf"]
    elif "wind" in query_lower:
        answer = "Wind energy projects follow standard Bureau of Energy Efficiency (BEE) guidelines for registration under the ICM, requiring third-party verification of emission reductions."
        sources = ["BEE Wind Registration Guide 2024.pdf"]
    else:
        answer = "I'm your AI Carbon Consultant. For Indian market inquiries, please specify the technology (e.g., solar, wind) or policy document you are referring to."
        sources = ["Indian Carbon Market Overview.pdf"]
        
    return ChatbotResponse(
        query=req.query,
        answer=answer,
        sources=sources
    )

@app.get("/api/marketplace", response_model=List[ProjectItem])
def get_marketplace_projects():
    return [
        ProjectItem(
            id="solar_transition",
            title="Solar PV Transition",
            description="Replace grid power with rooftop solar panels",
            cost_inr=500000.0,
            roi_pct=16.0,
            payback_years=6.2,
            credit_potential=50.0
        ),
        ProjectItem(
            id="led_retrofit",
            title="LED Lighting Retrofit",
            description="Upgrade industrial facility fixtures to high-efficiency LEDs",
            cost_inr=150000.0,
            roi_pct=24.0,
            payback_years=4.1,
            credit_potential=15.0
        ),
        ProjectItem(
            id="biomass_boiler",
            title="Biomass Boiler Conversion",
            description="Replace fossil-fuel boiler with agricultural waste biomass boiler",
            cost_inr=1200000.0,
            roi_pct=18.5,
            payback_years=5.4,
            credit_potential=120.0
        )
    ]

@app.post("/api/reports/export")
def export_report(req: ExportRequest, format: str = Query(..., regex="^(pdf|xlsx)$")):
    if format == "pdf":
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n..."
        return Response(
            content=dummy_pdf_content, 
            media_type="application/pdf", 
            headers={"Content-Disposition": 'attachment; filename="carbon_report.pdf"'}
        )
    elif format == "xlsx":
        dummy_xlsx_content = b"PK\x03\x04\x14\x00\x08\x00\x08\x00...mock_zip_excel..."
        return Response(
            content=dummy_xlsx_content, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers={"Content-Disposition": 'attachment; filename="carbon_report.xlsx"'}
        )
