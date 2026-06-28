from collections import defaultdict

from carbonpilot.schemas.calculation import (
    CalculationRequest,
    CalculationResponse,
    EmissionLine,
    ScopeSummary,
)
from carbonpilot.schemas.common import EmissionScope


def _round_tco2e(value: float) -> float:
    return round(value, 6)


def _kg_to_tonnes(value_kg: float) -> float:
    return value_kg / 1000.0


def calculate_scope_1(request: CalculationRequest) -> list[EmissionLine]:
    activity_data = request.activity_data
    lines: list[EmissionLine] = []

    for fuel in activity_data.fuels:
        co2e_tonnes = _kg_to_tonnes(fuel.amount * fuel.emission_factor_kg_co2e_per_unit)
        lines.append(
            EmissionLine(
                scope=EmissionScope.scope_1,
                category="fuel_combustion",
                activity_name=fuel.activity_name,
                co2e_tonnes=_round_tco2e(co2e_tonnes),
                formula="amount * emission_factor_kg_co2e_per_unit / 1000",
                factor_source=fuel.factor_source,
                input_reference=fuel.input_reference,
            )
        )

    for process in activity_data.processes:
        co2e_tonnes = process.output_tonnes * process.emission_factor_tco2e_per_tonne
        lines.append(
            EmissionLine(
                scope=EmissionScope.scope_1,
                category="process_emissions",
                activity_name=process.activity_name,
                co2e_tonnes=_round_tco2e(co2e_tonnes),
                formula="output_tonnes * emission_factor_tco2e_per_tonne",
                factor_source=process.factor_source,
                input_reference=process.input_reference,
            )
        )

    return lines


def calculate_scope_2(request: CalculationRequest) -> list[EmissionLine]:
    lines: list[EmissionLine] = []

    for electricity in request.activity_data.electricity:
        co2e_tonnes = electricity.electricity_mwh * electricity.emission_factor_tco2e_per_mwh
        lines.append(
            EmissionLine(
                scope=EmissionScope.scope_2,
                category="purchased_electricity",
                activity_name=electricity.activity_name,
                co2e_tonnes=_round_tco2e(co2e_tonnes),
                formula="electricity_mwh * emission_factor_tco2e_per_mwh",
                factor_source=electricity.factor_source,
                input_reference=electricity.input_reference,
            )
        )

    return lines


def calculate_scope_3(request: CalculationRequest) -> list[EmissionLine]:
    activity_data = request.activity_data
    lines: list[EmissionLine] = []

    for purchased_input in activity_data.purchased_inputs:
        co2e_tonnes = (
            purchased_input.mass_tonnes * purchased_input.emission_factor_tco2e_per_tonne
        )
        lines.append(
            EmissionLine(
                scope=EmissionScope.scope_3,
                category="purchased_inputs",
                activity_name=purchased_input.activity_name,
                co2e_tonnes=_round_tco2e(co2e_tonnes),
                formula="mass_tonnes * emission_factor_tco2e_per_tonne",
                factor_source=purchased_input.factor_source,
                input_reference=purchased_input.input_reference,
            )
        )

    for transport in activity_data.transport:
        co2e_tonnes = _kg_to_tonnes(
            transport.mass_tonnes
            * transport.distance_km
            * transport.emission_factor_kg_co2e_per_tonne_km
        )
        lines.append(
            EmissionLine(
                scope=EmissionScope.scope_3,
                category="upstream_transport",
                activity_name=transport.activity_name,
                co2e_tonnes=_round_tco2e(co2e_tonnes),
                formula="mass_tonnes * distance_km * emission_factor_kg_co2e_per_tonne_km / 1000",
                factor_source=transport.factor_source,
                input_reference=transport.input_reference,
            )
        )

    return lines


def calculate_emissions(request: CalculationRequest) -> CalculationResponse:
    lines = [
        *calculate_scope_1(request),
        *calculate_scope_2(request),
        *calculate_scope_3(request),
    ]
    totals_by_scope: dict[EmissionScope, float] = defaultdict(float)

    for line in lines:
        totals_by_scope[line.scope] += line.co2e_tonnes

    summaries = [
        ScopeSummary(scope=scope, total_tco2e=_round_tco2e(totals_by_scope[scope]))
        for scope in EmissionScope
    ]
    total_tco2e = _round_tco2e(sum(line.co2e_tonnes for line in lines))

    return CalculationResponse(
        facility_name=request.activity_data.facility.facility_name,
        reporting_period=request.activity_data.reporting_period,
        scope_summaries=summaries,
        emission_lines=lines,
        total_tco2e=total_tco2e,
        estimated_cbam_cost_eur=_round_tco2e(total_tco2e * request.carbon_price_eur_per_tonne),
    )
