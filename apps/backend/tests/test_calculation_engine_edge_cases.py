"""CP-51: additional formula edge-case and schema rejection tests.

test_calculation_engine.py already covers the happy path, the demo baseline,
and a first round of rejection tests (negative fuel amount, zero fuel
amount, missing activity records, malformed reporting period). This file
extends that coverage to the parts that were still untested: negative
values for every activity type (not just fuel), strict-schema rejection of
unknown fields and invalid enum values, and formula behaviour at numeric
extremes (very large inputs, rounding precision, zero carbon price).
"""

import pytest
from pydantic import ValidationError

from carbonpilot.calculation.engine import calculate_emissions
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


def _facility() -> Facility:
    return Facility(
        organization_name="Demo Steel Exporter",
        facility_name="Izmir Steel Plant",
        country_code="TR",
    )


@pytest.mark.parametrize(
    "activity_kwargs_factory",
    [
        lambda: {
            "processes": [
                ProcessActivity(
                    activity_name="EAF process",
                    process_type="eaf",
                    output_tonnes=-1.0,
                    emission_factor_tco2e_per_tonne=1.8,
                    factor_source="Test factor",
                    input_reference="PROC-NEG",
                )
            ]
        },
        lambda: {
            "electricity": [
                ElectricityActivity(
                    activity_name="Grid electricity",
                    electricity_mwh=-5.0,
                    emission_factor_tco2e_per_mwh=0.4,
                    factor_source="Test factor",
                    input_reference="ELEC-NEG",
                )
            ]
        },
        lambda: {
            "purchased_inputs": [
                PurchasedInputActivity(
                    activity_name="Purchased scrap",
                    material_name="steel_scrap",
                    cn_code="7204",
                    mass_tonnes=-10.0,
                    emission_factor_tco2e_per_tonne=0.2,
                    factor_source="Test factor",
                    input_reference="INPUT-NEG",
                )
            ]
        },
        lambda: {
            "transport": [
                TransportActivity(
                    activity_name="Road delivery",
                    mode="road",
                    mass_tonnes=10.0,
                    distance_km=-50.0,
                    emission_factor_kg_co2e_per_tonne_km=0.1,
                    factor_source="Test factor",
                    input_reference="TRANSPORT-NEG",
                )
            ]
        },
    ],
    ids=["process", "electricity", "purchased_input", "transport"],
)
def test_negative_values_are_rejected_for_every_activity_type(activity_kwargs_factory):
    """Sprint 1 only proved this for `fuels`; every other activity type
    shares the same `Field(ge=0)` constraint and must reject negatives too.
    """
    with pytest.raises(ValidationError):
        ActivityData(
            facility=_facility(),
            reporting_period="2026-Q1",
            **activity_kwargs_factory(),
        )


def test_schema_rejects_unknown_extra_field():
    """`StrictBaseModel` sets `extra="forbid"`; an unexpected field (e.g. a
    typo, or a client sending a field from a newer API version) must be
    rejected rather than silently ignored.
    """
    with pytest.raises(ValidationError):
        FuelActivity(
            activity_name="Natural gas reheating furnace",
            fuel_type="natural_gas",
            amount=1000.0,
            unit="Nm3",
            emission_factor_kg_co2e_per_unit=2.0,
            factor_source="Test factor",
            input_reference="ERP-FUEL-001",
            unexpected_field="should not be accepted",
        )


def test_invalid_unit_literal_is_rejected():
    with pytest.raises(ValidationError):
        FuelActivity(
            activity_name="Natural gas reheating furnace",
            fuel_type="natural_gas",
            amount=1000.0,
            unit="gallons",  # not in the allowed Literal set
            emission_factor_kg_co2e_per_unit=2.0,
            factor_source="Test factor",
            input_reference="ERP-FUEL-001",
        )


def test_invalid_transport_mode_is_rejected():
    with pytest.raises(ValidationError):
        TransportActivity(
            activity_name="Road delivery",
            mode="teleport",  # not in the allowed Literal set
            mass_tonnes=10.0,
            distance_km=50.0,
            emission_factor_kg_co2e_per_tonne_km=0.1,
            factor_source="Test factor",
            input_reference="TRANSPORT-001",
        )


def test_invalid_country_code_length_is_rejected():
    with pytest.raises(ValidationError):
        Facility(
            organization_name="Demo Steel Exporter",
            facility_name="Izmir Steel Plant",
            country_code="TUR",  # must be exactly 2 characters
        )


def test_large_activity_values_produce_finite_correct_result():
    """The formula must stay correct (not overflow, not silently truncate)
    for a facility reporting genuinely large industrial volumes.
    """
    request = CalculationRequest(
        activity_data=ActivityData(
            facility=_facility(),
            reporting_period="2026-Q1",
            fuels=[
                FuelActivity(
                    activity_name="Blast furnace gas",
                    fuel_type="natural_gas",
                    amount=1_000_000_000.0,
                    unit="Nm3",
                    emission_factor_kg_co2e_per_unit=2.0,
                    factor_source="Test factor",
                    input_reference="ERP-FUEL-LARGE",
                )
            ],
        )
    )

    response = calculate_emissions(request)

    assert response.total_tco2e == 2_000_000.0
    import math

    assert math.isfinite(response.total_tco2e)


def test_rounding_precision_to_six_decimals():
    """`_round_tco2e` rounds to 6 decimal places; a value with more
    precision than that must come out rounded, not truncated arbitrarily.
    """
    request = CalculationRequest(
        activity_data=ActivityData(
            facility=_facility(),
            reporting_period="2026-Q1",
            fuels=[
                FuelActivity(
                    activity_name="Precision test fuel",
                    fuel_type="natural_gas",
                    amount=1.0,
                    unit="Nm3",
                    emission_factor_kg_co2e_per_unit=1.23456789,
                    factor_source="Test factor",
                    input_reference="ERP-FUEL-PRECISION",
                )
            ],
        )
    )

    response = calculate_emissions(request)

    assert response.emission_lines[0].co2e_tonnes == round(1.23456789 / 1000.0, 6)


def test_zero_carbon_price_yields_zero_cbam_cost(build_demo_calculation_request):
    calculation_request = build_demo_calculation_request
    zero_price_request = CalculationRequest(
        activity_data=calculation_request.activity_data,
        carbon_price_eur_per_tonne=0.0,
    )

    response = calculate_emissions(zero_price_request)

    assert response.total_tco2e == 45.25
    assert response.estimated_cbam_cost_eur == 0.0