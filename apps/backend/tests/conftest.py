import pytest

from carbonpilot.agents import graph as graph_module
from carbonpilot.schemas.activity import (
    ActivityData,
    ElectricityActivity,
    Facility,
    FuelActivity,
    ProcessActivity,
    PurchasedInputActivity,
    TransportActivity,
)
from carbonpilot.schemas.calculation import CalculationRequest


@pytest.fixture
def require_checkpointer():
    """
    Fails the test (does NOT skip) if a live Postgres checkpointer isn't
    available. Use this in any test that specifically verifies
    persistence/recovery behaviour (CP-34 and later).

    We fail loudly on purpose: `_get_checkpointer()` degrades silently
    to None when Postgres is unreachable so the *rest* of the app keeps
    working, but that same silence would let a persistence test report
    a false "pass" if Docker Postgres isn't running. This project's
    workflow always starts Postgres first (see README), so a missing
    checkpointer here means something is actually wrong, not an
    acceptable fallback.
    """
    checkpointer = graph_module._get_checkpointer()
    assert checkpointer is not None, (
        "No live Postgres checkpointer available. Start it first: "
        "docker compose -f infra/docker-compose.yml up -d postgres"
    )
    return checkpointer


@pytest.fixture
def build_demo_calculation_request() -> CalculationRequest:
    return CalculationRequest(
        carbon_price_eur_per_tonne=80.0,
        activity_data=ActivityData(
            facility=Facility(
                organization_name="Demo Steel Exporter",
                facility_name="Izmir Steel Plant",
                country_code="TR",
            ),
            reporting_period="2026-Q1",
            fuels=[
                FuelActivity(
                    activity_name="Natural gas reheating furnace",
                    fuel_type="natural_gas",
                    amount=1000.0,
                    unit="Nm3",
                    emission_factor_kg_co2e_per_unit=2.0,
                    factor_source="Test factor",
                    input_reference="ERP-FUEL-001",
                )
            ],
            processes=[
                ProcessActivity(
                    activity_name="EAF process emissions",
                    process_type="eaf",
                    output_tonnes=10.0,
                    emission_factor_tco2e_per_tonne=1.8,
                    factor_source="Test process factor",
                    input_reference="PROD-001",
                )
            ],
            electricity=[
                ElectricityActivity(
                    activity_name="Grid electricity",
                    electricity_mwh=50.0,
                    emission_factor_tco2e_per_mwh=0.4,
                    factor_source="Test grid factor",
                    input_reference="UTILITY-001",
                )
            ],
            purchased_inputs=[
                PurchasedInputActivity(
                    activity_name="Purchased steel scrap",
                    material_name="steel_scrap",
                    cn_code="7204",
                    mass_tonnes=25.0,
                    emission_factor_tco2e_per_tonne=0.2,
                    factor_source="Supplier factor",
                    input_reference="SUPPLIER-001",
                )
            ],
            transport=[
                TransportActivity(
                    activity_name="Road delivery of scrap",
                    mode="road",
                    mass_tonnes=25.0,
                    distance_km=100.0,
                    emission_factor_kg_co2e_per_tonne_km=0.1,
                    factor_source="Freight factor",
                    input_reference="CMR-001",
                )
            ],
        ),
    )

@pytest.fixture
def require_database():
    """
    Fails the test (does NOT skip) if a live Postgres connection isn't
    available. Mirrors `require_checkpointer` (see above) — persistence
    tests should fail loudly, not silently pass, when Docker Postgres
    isn't running (see README for `docker compose up -d postgres`).

    Yields a real SQLAlchemy session and rolls back/closes it afterwards.
    """
    from sqlalchemy import text

    from carbonpilot.db.session import SessionLocal

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db.close()
        raise AssertionError(
            "No live Postgres connection available. Start it first: "
            "docker compose -f infra/docker-compose.yml up -d postgres"
        ) from exc

    yield db
    db.rollback()
    db.close()