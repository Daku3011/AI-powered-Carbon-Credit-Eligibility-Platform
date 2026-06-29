import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_pdf_report(
    industry: str,
    metrics: dict,
    eligibility: dict,
    roadmap: list,
) -> bytes:
    """Generate a PDF report with calculation results, eligibility, and roadmap."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"], fontSize=18, spaceAfter=20
    )
    elements.append(Paragraph("AI Carbon Intelligence Platform - Report", title_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Industry:</b> {industry}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Input Metrics</b>", styles["Heading2"]))
    metrics_data = [
        ["Metric", "Value"],
        ["Electricity (kWh)", f"{metrics.get('electricity_kwh', 0):,.2f}"],
        ["Diesel (Liters)", f"{metrics.get('fuel_diesel_liters', 0):,.2f}"],
        ["Waste (kg)", f"{metrics.get('waste_kg', 0):,.2f}"],
        ["Operational Hours", f"{metrics.get('operational_hours', 0):,.0f}"],
    ]
    metrics_table = Table(metrics_data, colWidths=[3 * inch, 3 * inch])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Emissions Summary</b>", styles["Heading2"]))
    emissions_data = [
        ["Metric", "Value (tCO2e)"],
        ["Scope 1 Emissions", f"{eligibility.get('scope_1', 0):.2f}"],
        ["Scope 2 Emissions", f"{eligibility.get('scope_2', 0):.2f}"],
        ["Total Emissions", f"{eligibility.get('total', 0):.2f}"],
    ]
    emissions_table = Table(emissions_data, colWidths=[3 * inch, 3 * inch])
    emissions_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(emissions_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Eligibility Score</b>", styles["Heading2"]))
    score_data = [
        ["Metric", "Value"],
        ["Readiness Score", f"{eligibility.get('readiness_score', 0)} / 100"],
        ["Emissions Rating", str(eligibility.get("emissions_rating", "N/A"))],
        ["Reduction Potential", f"{eligibility.get('reduction_potential_pct', 0):.1f}%"],
        ["Carbon Credit Potential", f"{eligibility.get('carbon_credit_potential', 0):.0f} credits"],
        ["Projected Revenue", f"INR {eligibility.get('projected_revenue_inr', 0):,.2f}"],
        ["Confidence Score", f"{eligibility.get('confidence_score', 0):.2f}"],
    ]
    score_table = Table(score_data, colWidths=[3 * inch, 3 * inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E65100")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Carbon Reduction Roadmap</b>", styles["Heading2"]))
    roadmap_data = [["Year", "Recommendation", "Investment (INR)", "Savings (INR)", "Credits"]]
    for item in roadmap:
        roadmap_data.append([
            str(item.get("year", "")),
            item.get("recommendation", ""),
            f"{item.get('investment_inr', 0):,.0f}",
            f"{item.get('savings_inr', 0):,.0f}",
            f"{item.get('credits_earned', 0):.0f}",
        ])
    roadmap_table = Table(roadmap_data, colWidths=[0.7 * inch, 2.3 * inch, 1.5 * inch, 1.5 * inch, 0.8 * inch])
    roadmap_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6A1B9A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(roadmap_table)
    elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
