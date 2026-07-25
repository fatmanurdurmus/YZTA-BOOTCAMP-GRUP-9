from carbonpilot.reporting.integrity import verify_integrity
from carbonpilot.reporting.json_report import build_json_report
from carbonpilot.law_rag.retriever import retrieve_default_references


def test_json_report_hash_is_stable_and_detects_tampering(build_demo_calculation_request):
    from carbonpilot.calculation.engine import calculate_emissions

    calculation = calculate_emissions(build_demo_calculation_request)
    report = build_json_report(calculation, retrieve_default_references())
    assert verify_integrity(report)
    report["calculation"]["total_tco2e"] = 0
    assert not verify_integrity(report)
