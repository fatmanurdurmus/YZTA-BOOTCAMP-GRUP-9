from pypdf import PdfReader

from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.law_rag.retriever import retrieve_default_references
from carbonpilot.reporting.pdf_report import build_pdf_report


def test_pdf_report_contains_calculation_and_evidence(build_demo_calculation_request):
    output = build_pdf_report(calculate_emissions(build_demo_calculation_request), retrieve_default_references())
    assert output.startswith(b"%PDF")
    text = "\n".join(page.extract_text() or "" for page in PdfReader(__import__("io").BytesIO(output)).pages)
    assert "Izmir Steel Plant" in text
    assert "ERP-FUEL-001" in text
