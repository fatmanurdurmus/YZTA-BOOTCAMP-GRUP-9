import pytest
from pydantic import ValidationError

from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.schemas.activity import ActivityData, Facility, FuelActivity
from carbonpilot.schemas.calculation import CalculationRequest
from carbonpilot.schemas.common import EmissionScope


def test_calculates_scope_1_scope_2_and_cbam_focused_scope_3(build_demo_calculation_request):
    response = calculate_emissions(build_demo_calculation_request)

    totals = {summary.scope: summary.total_tco2e for summary in response.scope_summaries}

    assert totals[EmissionScope.scope_1] == 20.0
    assert totals[EmissionScope.scope_2] == 20.0
    assert totals[EmissionScope.scope_3] == 5.25
    assert response.total_tco2e == 45.25
    assert response.estimated_cbam_cost_eur == 3620.0


def test_every_emission_line_keeps_audit_evidence(build_demo_calculation_request):
    response = calculate_emissions(build_demo_calculation_request)

    assert response.emission_lines
    for line in response.emission_lines:
        assert line.factor_source
        assert line.input_reference
        assert line.formula


def test_negative_activity_data_is_rejected():
    with pytest.raises(ValidationError):
        CalculationRequest(
            activity_data=ActivityData(
                facility=Facility(
                    organization_name="Demo Steel Exporter",
                    facility_name="Izmir Steel Plant",
                    country_code="TR",
                ),
                reporting_period="2026-Q1",
                fuels=[
                    FuelActivity(
                        activity_name="Bad fuel",
                        fuel_type="natural_gas",
                        amount=-1.0,
                        unit="Nm3",
                        emission_factor_kg_co2e_per_unit=2.0,
                        factor_source="Test factor",
                        input_reference="ERP-FUEL-NEG",
                    )
                ],
            )
        )

def test_zero_activity_amount_produces_zero_emission_line():
    request = CalculationRequest(
        activity_data=ActivityData(
            facility=Facility(
                organization_name="Demo Steel Exporter",
                facility_name="Izmir Steel Plant",
                country_code="TR",
            ),
            reporting_period="2026-Q1",
            fuels=[
                FuelActivity(
                    activity_name="Idle furnace",
                    fuel_type="natural_gas",
                    amount=0.0,
                    unit="Nm3",
                    emission_factor_kg_co2e_per_unit=2.0,
                    factor_source="Test factor",
                    input_reference="ERP-FUEL-ZERO",
                )
            ],
        )
    )

    response = calculate_emissions(request)

    assert response.total_tco2e == 0.0
    assert response.emission_lines[0].co2e_tonnes == 0.0


def test_activity_data_with_no_records_is_rejected():
    with pytest.raises(ValidationError):
        ActivityData(
            facility=Facility(
                organization_name="Demo Steel Exporter",
                facility_name="Izmir Steel Plant",
                country_code="TR",
            ),
            reporting_period="2026-Q1",
        )


def test_invalid_reporting_period_format_is_rejected():
    with pytest.raises(ValidationError):
        ActivityData(
            facility=Facility(
                organization_name="Demo Steel Exporter",
                facility_name="Izmir Steel Plant",
                country_code="TR",
            ),
            reporting_period="not-a-period",
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
        )