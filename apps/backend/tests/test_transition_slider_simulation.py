from decimal import Decimal
from time import perf_counter

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from carbonpilot.main import app
from carbonpilot.schemas.optimization import CarbonTaxPeriod
from carbonpilot.schemas.simulation import (
    EnergyMixScenario,
    MaterialSubstitutionScenario,
    SliderSimulationRequest,
    TransitionLeverAssumptions,
)
from carbonpilot.simulation.service import simulate_transition_sliders


def _tax_period(
    year: int,
    price: str,
    *,
    coverage: str = "1",
    allowance: str = "0",
) -> CarbonTaxPeriod:
    return CarbonTaxPeriod(
        year=year,
        carbon_price_eur_per_tco2e=Decimal(price),
        covered_emissions_rate=Decimal(coverage),
        free_allowance_tco2e=Decimal(allowance),
        tax_rate_source=f"tax-source-{year}",
        input_reference=f"tax-input-{year}",
    )


def _assumptions(
    reduction: str,
    *,
    cost: str = "0",
    operating_cost: str = "0",
    operating_savings: str = "0",
    source: str = "factor-source",
) -> TransitionLeverAssumptions:
    return TransitionLeverAssumptions(
        emission_reduction_factor=Decimal(reduction),
        transition_cost_eur_at_100_percent=Decimal(cost),
        annual_operating_cost_eur_at_100_percent=Decimal(operating_cost),
        annual_operating_savings_eur_at_100_percent=Decimal(operating_savings),
        factor_source=source,
        input_reference=f"{source}-input",
    )


def _request(**overrides: object) -> SliderSimulationRequest:
    values: dict[str, object] = {
        "baseline_tco2e": Decimal("1000"),
        "baseline_energy_tco2e": Decimal("400"),
        "baseline_material_tco2e": Decimal("300"),
        "baseline_input_reference": "verified-inventory-2025",
        "energy_mix": EnergyMixScenario(
            solar_percent=Decimal("25"), wind_percent=Decimal("25")
        ),
        "material_substitution": MaterialSubstitutionScenario(
            recycled_percent=Decimal("50"), low_carbon_percent=Decimal("25")
        ),
        "solar_assumptions": _assumptions(
            "0.9", cost="100000", operating_cost="10000", operating_savings="20000"
        ),
        "wind_assumptions": _assumptions(
            "0.8", cost="80000", operating_cost="8000", operating_savings="12000"
        ),
        "recycled_material_assumptions": _assumptions(
            "0.6", cost="60000", operating_cost="5000", operating_savings="9000"
        ),
        "low_carbon_material_assumptions": _assumptions(
            "0.7", cost="40000", operating_cost="4000", operating_savings="6000"
        ),
        "tax_schedule": [_tax_period(2026, "100"), _tax_period(2027, "120")],
    }
    values.update(overrides)
    return SliderSimulationRequest(**values)


def test_combined_slider_scenario_calculates_emissions_tax_savings_and_roi():
    result = simulate_transition_sliders(_request())

    assert result.projected_emissions_tco2e == Decimal("687.500000")
    assert result.emissions_reduction_tco2e == Decimal("312.500000")
    assert result.emissions_reduction_percent == Decimal("31.2500")
    assert result.impact_breakdown.energy_reduction_tco2e == Decimal("170.000000")
    assert result.impact_breakdown.material_reduction_tco2e == Decimal("142.500000")
    assert result.estimated_carbon_tax_savings_eur == Decimal("68750.00")
    assert result.transition_cost_eur == Decimal("85000.00")
    assert result.total_operating_cost_eur == Decimal("16000.00")
    assert result.total_operating_savings_eur == Decimal("28000.00")
    assert result.net_savings_eur == Decimal("-4250.00")
    assert result.roi_percent == Decimal("-4.2079")
    assert [period.net_cash_flow_eur for period in result.annual_results] == [
        Decimal("37250.00"),
        Decimal("43500.00"),
    ]


def test_calculation_retains_factor_tax_and_input_evidence():
    result = simulate_transition_sliders(_request())

    assert [item.lever for item in result.calculation_evidence] == [
        "solar",
        "wind",
        "recycled_material",
        "low_carbon_material",
    ]
    assert result.calculation_evidence[0].scope == "energy"
    assert "slider_percent / 100" in result.calculation_evidence[0].formula
    assert result.annual_results[0].tax_rate_source == "tax-source-2026"
    assert result.annual_results[0].baseline_input_reference == "verified-inventory-2025"


def test_full_green_energy_transition_only_changes_energy_baseline():
    request = _request(
        energy_mix=EnergyMixScenario(solar_percent=Decimal("100")),
        material_substitution=MaterialSubstitutionScenario(),
        solar_assumptions=_assumptions("1"),
        tax_schedule=[_tax_period(2026, "100")],
    )

    result = simulate_transition_sliders(request)

    assert result.impact_breakdown.energy_reduction_tco2e == Decimal("400.000000")
    assert result.impact_breakdown.material_reduction_tco2e == Decimal("0.000000")
    assert result.projected_emissions_tco2e == Decimal("600.000000")


def test_zero_sliders_produce_unchanged_emissions_and_safe_undefined_roi():
    request = _request(
        baseline_tco2e=Decimal("0"),
        baseline_energy_tco2e=Decimal("0"),
        baseline_material_tco2e=Decimal("0"),
        energy_mix=EnergyMixScenario(),
        material_substitution=MaterialSubstitutionScenario(),
        tax_schedule=[_tax_period(2026, "1000000000")],
    )

    result = simulate_transition_sliders(request)

    assert result.projected_emissions_tco2e == Decimal("0.000000")
    assert result.emissions_reduction_percent == Decimal("0.0000")
    assert result.estimated_carbon_tax_savings_eur == Decimal("0.00")
    assert result.net_savings_eur == Decimal("0.00")
    assert result.roi_percent is None


def test_shared_tax_formula_honors_coverage_and_free_allowance_floor():
    request = _request(
        baseline_tco2e=Decimal("100"),
        baseline_energy_tco2e=Decimal("100"),
        baseline_material_tco2e=Decimal("0"),
        energy_mix=EnergyMixScenario(solar_percent=Decimal("100")),
        material_substitution=MaterialSubstitutionScenario(),
        solar_assumptions=_assumptions("1"),
        tax_schedule=[_tax_period(2026, "100", coverage="0.8", allowance="50")],
    )

    result = simulate_transition_sliders(request)

    assert result.annual_results[0].baseline_taxable_tco2e == Decimal("30.000000")
    assert result.annual_results[0].transition_taxable_tco2e == Decimal("0.000000")
    assert result.estimated_carbon_tax_savings_eur == Decimal("3000.00")


@pytest.mark.parametrize(
    ("scenario_type", "values"),
    [
        (EnergyMixScenario, {"solar_percent": Decimal("-0.01")}),
        (EnergyMixScenario, {"wind_percent": Decimal("100.01")}),
        (
            EnergyMixScenario,
            {"solar_percent": Decimal("60"), "wind_percent": Decimal("41")},
        ),
        (MaterialSubstitutionScenario, {"recycled_percent": Decimal("-1")}),
        (
            MaterialSubstitutionScenario,
            {"recycled_percent": Decimal("51"), "low_carbon_percent": Decimal("50")},
        ),
    ],
)
def test_slider_boundaries_and_combined_totals_are_validated(scenario_type, values):
    with pytest.raises(ValidationError):
        scenario_type(**values)


def test_allocated_sector_emissions_cannot_exceed_total_baseline():
    with pytest.raises(ValidationError, match="must not exceed baseline_tco2e"):
        _request(
            baseline_tco2e=Decimal("100"),
            baseline_energy_tco2e=Decimal("60"),
            baseline_material_tco2e=Decimal("41"),
        )


def test_duplicate_tax_years_are_rejected():
    with pytest.raises(ValidationError, match="tax_schedule years must be unique"):
        _request(tax_schedule=[_tax_period(2026, "100"), _tax_period(2026, "120")])


def test_binary_floats_are_rejected_at_the_contract_boundary():
    with pytest.raises(ValidationError, match="JSON strings or integers"):
        EnergyMixScenario(solar_percent=0.1)


def test_subcent_decimal_inputs_are_rounded_only_at_output_boundary():
    request = _request(
        baseline_tco2e=Decimal("0.1"),
        baseline_energy_tco2e=Decimal("0.1"),
        baseline_material_tco2e=Decimal("0"),
        energy_mix=EnergyMixScenario(solar_percent=Decimal("30")),
        material_substitution=MaterialSubstitutionScenario(),
        solar_assumptions=_assumptions("1"),
        tax_schedule=[_tax_period(2026, "0.333333333333333333")],
    )

    result = simulate_transition_sliders(request)

    assert result.emissions_reduction_tco2e == Decimal("0.030000")
    assert result.annual_results[0].carbon_tax_savings_eur == Decimal("0.01")


def test_pure_calculation_averages_below_one_millisecond():
    request = _request()
    simulate_transition_sliders(request)
    iterations = 2_000

    started = perf_counter()
    for _ in range(iterations):
        simulate_transition_sliders(request)
    average_seconds = (perf_counter() - started) / iterations

    assert average_seconds < 0.001


def test_slider_api_returns_real_time_simulation_contract():
    payload = _request().model_dump(mode="json")

    response = TestClient(app).post("/v1/simulate/transition-slider", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["projected_emissions_tco2e"] == "687.500000"
    assert body["estimated_carbon_tax_savings_eur"] == "68750.00"
    assert body["roi_percent"] == "-4.2079"


def test_slider_api_rejects_mix_above_one_hundred_percent():
    payload = _request().model_dump(mode="json")
    payload["energy_mix"] = {"solar_percent": "51", "wind_percent": "50"}

    response = TestClient(app).post("/v1/simulate/transition-slider", json=payload)

    assert response.status_code == 422
