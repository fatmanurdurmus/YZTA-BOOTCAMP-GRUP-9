from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from carbonpilot.main import app
from carbonpilot.schemas.optimization import (
    CarbonTaxPeriod,
    GreenTransitionOption,
    OptimizationRequest,
    TransformationScenario,
)
from carbonpilot.simulation.service import optimize_green_transition, simulate_transformation


def _period(
    year: int = 2026,
    price: str = "100",
    coverage: str = "1",
    allowance: str = "0",
) -> CarbonTaxPeriod:
    return CarbonTaxPeriod(
        year=year,
        carbon_price_eur_per_tco2e=Decimal(price),
        covered_emissions_rate=Decimal(coverage),
        free_allowance_tco2e=Decimal(allowance),
        tax_rate_source="Configured compliance scenario",
        input_reference=f"TAX-{year}",
    )


def _option(
    name: str = "Electrify furnace",
    reduction: str = "0.4",
    investment: str = "50000",
    operating_cost: str = "5000",
    operating_savings: str = "10000",
) -> GreenTransitionOption:
    return GreenTransitionOption(
        option_name=name,
        emission_reduction_rate=Decimal(reduction),
        initial_investment_eur=Decimal(investment),
        annual_operating_cost_eur=Decimal(operating_cost),
        annual_operating_savings_eur=Decimal(operating_savings),
    )


def test_calculates_tax_savings_net_value_and_audit_evidence():
    request = OptimizationRequest(
        baseline_tco2e=Decimal("1000"),
        baseline_input_reference="CALC-RUN-001",
        discount_rate=Decimal("0.10"),
        tax_schedule=[
            _period(2026, price="100", coverage="0.5", allowance="100"),
            _period(2027, price="150", coverage="1", allowance="100"),
        ],
        transition_options=[_option()],
    )

    response = optimize_green_transition(request)
    result = response.results[0]

    assert result.transitioned_emissions_tco2e == Decimal("600.000000")
    assert result.avoided_emissions_tco2e == Decimal("400.000000")
    assert result.total_carbon_tax_savings_eur == Decimal("80000.00")
    assert result.net_savings_eur == Decimal("40000.00")
    assert result.net_present_savings_eur == Decimal("26446.28")
    assert [annual.carbon_tax_savings_eur for annual in result.annual_results] == [
        Decimal("20000.00"),
        Decimal("60000.00"),
    ]
    for annual in result.annual_results:
        assert annual.formula
        assert annual.tax_rate_source == "Configured compliance scenario"
        assert annual.input_reference == f"TAX-{annual.year}"
        assert annual.baseline_input_reference == "CALC-RUN-001"


def test_ranks_options_by_net_present_savings_not_emissions_reduction():
    request = OptimizationRequest(
        baseline_tco2e=Decimal("1000"),
        baseline_input_reference="CALC-RUN-002",
        tax_schedule=[_period()],
        transition_options=[
            _option("Maximum reduction", "1", investment="200000"),
            _option("Cost-effective reduction", "0.5", investment="1000"),
        ],
    )

    response = optimize_green_transition(request)

    assert response.recommended_option == "Cost-effective reduction"
    assert [result.rank for result in response.results] == [1, 2]
    assert response.results[0].net_present_savings_eur > response.results[1].net_present_savings_eur


def test_ranking_uses_unrounded_values_when_display_values_tie():
    request = OptimizationRequest(
        baseline_tco2e=Decimal("1"),
        baseline_input_reference="CALC-SUBCENT",
        tax_schedule=[_period(price="0.01")],
        transition_options=[
            _option(
                "Lower raw value",
                "0.1",
                investment="0",
                operating_cost="0",
                operating_savings="0",
            ),
            _option(
                "Higher raw value",
                "0.2",
                investment="0",
                operating_cost="0",
                operating_savings="0",
            ),
        ],
    )

    response = optimize_green_transition(request)

    assert response.results[0].net_present_savings_eur == Decimal("0.00")
    assert response.results[1].net_present_savings_eur == Decimal("0.00")
    assert response.recommended_option == "Higher raw value"


def test_zero_emissions_produces_zero_tax_savings():
    request = OptimizationRequest(
        baseline_tco2e=Decimal("0"),
        baseline_input_reference="CALC-ZERO",
        tax_schedule=[_period(price="999999999999.99")],
        transition_options=[_option(reduction="1", investment="0", operating_cost="0")],
    )

    result = optimize_green_transition(request).results[0]

    assert result.avoided_emissions_tco2e == Decimal("0.000000")
    assert result.total_carbon_tax_savings_eur == Decimal("0.00")


def test_allowance_floor_prevents_negative_taxable_emissions():
    request = OptimizationRequest(
        baseline_tco2e=Decimal("10"),
        baseline_input_reference="CALC-ALLOWANCE",
        tax_schedule=[_period(allowance="100")],
        transition_options=[_option(reduction="1", investment="0", operating_cost="0")],
    )

    annual = optimize_green_transition(request).results[0].annual_results[0]

    assert annual.baseline_taxable_tco2e == Decimal("0.000000")
    assert annual.transition_taxable_tco2e == Decimal("0.000000")
    assert annual.carbon_tax_savings_eur == Decimal("0.00")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("baseline_tco2e", Decimal("-1")),
        ("discount_rate", Decimal("-0.01")),
        ("discount_rate", Decimal("1")),
    ],
)
def test_invalid_request_values_are_rejected(field: str, value: Decimal):
    values = {
        "baseline_tco2e": Decimal("1"),
        "baseline_input_reference": "CALC-INVALID",
        "discount_rate": Decimal("0"),
        "tax_schedule": [_period()],
        "transition_options": [_option()],
    }
    values[field] = value

    with pytest.raises(ValidationError):
        OptimizationRequest(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("emission_reduction_rate", Decimal("-0.01")),
        ("emission_reduction_rate", Decimal("1.01")),
        ("initial_investment_eur", Decimal("-1")),
        ("annual_operating_cost_eur", Decimal("-1")),
        ("annual_operating_savings_eur", Decimal("-1")),
    ],
)
def test_invalid_transition_values_are_rejected(field: str, value: Decimal):
    values = {
        "option_name": "Invalid option",
        "emission_reduction_rate": Decimal("0.5"),
        "initial_investment_eur": Decimal("0"),
        "annual_operating_cost_eur": Decimal("0"),
        "annual_operating_savings_eur": Decimal("0"),
    }
    values[field] = value

    with pytest.raises(ValidationError):
        GreenTransitionOption(**values)


def test_duplicate_schedule_years_are_rejected():
    with pytest.raises(ValidationError, match="years must be unique"):
        OptimizationRequest(
            baseline_tco2e=Decimal("1"),
            baseline_input_reference="CALC-DUPLICATE",
            tax_schedule=[_period(), _period()],
            transition_options=[_option()],
        )


def test_uses_decimal_math_before_rounding():
    request = OptimizationRequest(
        baseline_tco2e=Decimal("0.1"),
        baseline_input_reference="CALC-PRECISION",
        tax_schedule=[_period(price="0.2")],
        transition_options=[
            _option(
                reduction="0.3",
                investment="0",
                operating_cost="0",
                operating_savings="0",
            )
        ],
    )

    result = optimize_green_transition(request).results[0]

    assert result.avoided_emissions_tco2e == Decimal("0.030000")
    assert result.total_carbon_tax_savings_eur == Decimal("0.01")


def test_green_transition_endpoint_integrates_strict_schema_and_engine():
    payload = {
        "baseline_tco2e": "1000",
        "baseline_input_reference": "CALC-API-001",
        "discount_rate": "0",
        "tax_schedule": [
            {
                "year": 2026,
                "carbon_price_eur_per_tco2e": "100",
                "covered_emissions_rate": "1",
                "free_allowance_tco2e": "0",
                "tax_rate_source": "Configured API scenario",
                "input_reference": "TAX-API-2026",
            }
        ],
        "transition_options": [
            {
                "option_name": "API option",
                "emission_reduction_rate": "0.25",
                "initial_investment_eur": "0",
                "annual_operating_cost_eur": "0",
                "annual_operating_savings_eur": "0",
            }
        ],
    }

    response = TestClient(app).post("/v1/optimize/green-transition", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["recommended_option"] == "API option"
    assert body["results"][0]["total_carbon_tax_savings_eur"] == "25000.00"


def test_green_transition_endpoint_rejects_negative_values():
    payload = {
        "baseline_tco2e": "-1",
        "baseline_input_reference": "CALC-API-BAD",
        "tax_schedule": [
            {
                "year": 2026,
                "carbon_price_eur_per_tco2e": "100",
                "tax_rate_source": "Configured API scenario",
                "input_reference": "TAX-API-2026",
            }
        ],
        "transition_options": [
            {"option_name": "API option", "emission_reduction_rate": "0.25"}
        ],
    }

    response = TestClient(app).post("/v1/optimize/green-transition", json=payload)

    assert response.status_code == 422


def test_legacy_single_period_simulation_contract_remains_compatible():
    result = simulate_transformation(
        TransformationScenario(
            baseline_tco2e=100.0,
            carbon_price_eur_per_tonne=80.0,
            reduction_rate=0.25,
            annualized_investment_cost_eur=500.0,
        )
    )

    assert result.reduced_tco2e == 25.0
    assert result.avoided_carbon_cost_eur == 2000.0
    assert result.net_savings_eur == 1500.0
