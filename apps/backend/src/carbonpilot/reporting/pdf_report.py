"""Downloadable, evidence-preserving CBAM/SKDM PDF report renderer."""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from carbonpilot.schemas.calculation import CalculationResponse
from carbonpilot.schemas.law import LawReference


def build_pdf_report(calculation: CalculationResponse, law_references: list[LawReference]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("CarbonPilot AI - CBAM/SKDM Emissions Report", styles["Title"]), Paragraph(f"Facility: {calculation.facility_name}<br/>Reporting period: {calculation.reporting_period}<br/>Methodology: {calculation.methodology_version}", styles["BodyText"]), Spacer(1, 8 * mm)]
    rows = [["Scope", "Category", "Activity", "tCO2e", "Evidence"]]
    rows.extend([[line.scope.value, line.category, line.activity_name, f"{line.co2e_tonnes:.4f}", f"{line.factor_source}; {line.input_reference}"] for line in calculation.emission_lines])
    table = Table(rows, colWidths=[20 * mm, 31 * mm, 40 * mm, 20 * mm, 63 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163d2b")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, 0), 7)]))
    story.extend([Paragraph(f"Total emissions: <b>{calculation.total_tco2e:.4f} tCO2e</b><br/>Estimated CBAM cost: <b>EUR {calculation.estimated_cbam_cost_eur:.2f}</b>", styles["Heading2"]), table, Spacer(1, 8 * mm), Paragraph("Legal references", styles["Heading2"])])
    story.extend(Paragraph(f"{reference.title} ({reference.jurisdiction}): {reference.url}", styles["BodyText"]) for reference in law_references)
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Bootcamp MVP output; production use requires expert validation.", styles["Italic"]))
    document.build(story)
    return buffer.getvalue()
