from fastapi.testclient import TestClient

from carbonpilot.ingestion import extractor
from carbonpilot.main import create_app
from carbonpilot.schemas.activity import ActivityData, FuelActivity


def _form_data():
    return {"organization_name": "Demo Steel", "facility_name": "Izmir Plant", "country_code": "TR", "reporting_period": "2026-Q1"}


def _candidate() -> ActivityData:
    return ActivityData.model_validate({
        "facility": {"organization_name": "Demo Steel", "facility_name": "Izmir Plant", "country_code": "TR"},
        "reporting_period": "2026-Q1",
        "fuels": [FuelActivity(activity_name="Gas", fuel_type="natural_gas", amount=1.0, unit="Nm3", emission_factor_kg_co2e_per_unit=2.0, factor_source="Invoice", input_reference="invoice.pdf:p1")],
    })


def test_extract_rejects_unsupported_document_type():
    response = TestClient(create_app()).post("/v1/documents/extract", data=_form_data(), files={"file": ("data.csv", b"x", "text/csv")})
    assert response.status_code == 415


def test_extract_returns_503_without_gemini(monkeypatch):
    from carbonpilot.api import routes

    monkeypatch.setattr(extractor, "get_settings", lambda: type("Settings", (), {"gemini_api_key": None})())
    monkeypatch.setattr(routes, "extract_document_text", lambda *args: [(1, "Natural gas 1 Nm3")])
    response = TestClient(create_app()).post("/v1/documents/extract", data=_form_data(), files={"file": ("source.pdf", b"not-a-real-pdf", "application/pdf")})
    assert response.status_code == 503


def test_extract_returns_strict_candidate_without_persistence(monkeypatch):
    from carbonpilot.api import routes

    monkeypatch.setattr(routes, "extract_document_text", lambda *args: [(1, "Natural gas 1 Nm3")])
    monkeypatch.setattr(routes, "extract_candidate_activity", lambda **kwargs: _candidate())
    response = TestClient(create_app()).post("/v1/documents/extract", data=_form_data(), files={"file": ("invoice.pdf", b"pdf", "application/pdf")})
    assert response.status_code == 200
    assert response.json()["candidate_activity_data"]["fuels"][0]["input_reference"] == "invoice.pdf:p1"
