from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.schemas.report import ReportRequest
from app.services.report_pdf import generate_pdf_report
from app.services.report_excel import generate_excel_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/export")
def export_report(req: ReportRequest, format: str = Query("pdf", pattern="^(pdf|xlsx)$")):
    elig = req.eligibility_score
    eligibility_dict = {
        "readiness_score": elig.readiness_score,
        "emissions_rating": elig.emissions_rating,
        "reduction_potential_pct": elig.reduction_potential_pct,
        "carbon_credit_potential": elig.carbon_credit_potential,
        "projected_revenue_inr": elig.projected_revenue_inr,
        "confidence_score": elig.confidence_score,
        "scope_1": elig.scope_1,
        "scope_2": elig.scope_2,
        "total": elig.total,
    }

    roadmap_list = [item.model_dump() for item in req.roadmap]

    if format == "pdf":
        content = generate_pdf_report(req.industry, req.metrics, eligibility_dict, roadmap_list)
        return StreamingResponse(
            iter([content]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=carbon_report.pdf"},
        )
    else:
        content = generate_excel_report(req.industry, req.metrics, eligibility_dict, roadmap_list)
        return StreamingResponse(
            iter([content]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=carbon_report.xlsx"},
        )
