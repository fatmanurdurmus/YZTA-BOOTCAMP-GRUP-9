from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from carbonpilot.schemas.optimization import (
    AnnualTaxSavings,
    GreenTransitionOption,
    OptimizationRequest,
    OptimizationResponse,
    TransformationResult,
    TransformationScenario,
    TransitionOptimizationResult,
)


TONNES_QUANTUM = Decimal("0.000001")
MONEY_QUANTUM = Decimal("0.01")
ONE = Decimal("1")
ZERO = Decimal("0")

TAXABLE_EMISSIONS_FORMULA = (
    "max(emissions_tco2e * covered_emissions_rate - free_allowance_tco2e, 0)"
)
SAVINGS_FORMULA = (
    "(baseline_taxable_tco2e - transition_taxable_tco2e) "
    "* carbon_price_eur_per_tco2e"
)


def _quantize(value: Decimal, quantum: Decimal) -> Decimal:
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def _taxable_emissions(
    emissions_tco2e: Decimal,
    covered_emissions_rate: Decimal,
    free_allowance_tco2e: Decimal,
) -> Decimal:
    return max(
        emissions_tco2e * covered_emissions_rate - free_allowance_tco2e,
        ZERO,
    )


@dataclass(frozen=True)
class _UnrankedResult:
    ranking_net_present_savings_eur: Decimal
    option_name: str
    transitioned_emissions_tco2e: Decimal
    avoided_emissions_tco2e: Decimal
    total_carbon_tax_savings_eur: Decimal
    net_savings_eur: Decimal
    net_present_savings_eur: Decimal
    annual_results: list[AnnualTaxSavings]


def _evaluate_option(
    request: OptimizationRequest,
    option: GreenTransitionOption,
) -> _UnrankedResult:
    transitioned_emissions = request.baseline_tco2e * (ONE - option.emission_reduction_rate)
    avoided_emissions = request.baseline_tco2e - transitioned_emissions
    first_year = min(period.year for period in request.tax_schedule)
    annual_results: list[AnnualTaxSavings] = []
    total_tax_savings = ZERO
    total_net_cash_flow = ZERO
    discounted_cash_flows = ZERO

    for period in sorted(request.tax_schedule, key=lambda item: item.year):
        baseline_taxable = _taxable_emissions(
            request.baseline_tco2e,
            period.covered_emissions_rate,
            period.free_allowance_tco2e,
        )
        transition_taxable = _taxable_emissions(
            transitioned_emissions,
            period.covered_emissions_rate,
            period.free_allowance_tco2e,
        )
        avoided_taxable = baseline_taxable - transition_taxable
        baseline_cost = baseline_taxable * period.carbon_price_eur_per_tco2e
        transition_cost = transition_taxable * period.carbon_price_eur_per_tco2e
        tax_savings = baseline_cost - transition_cost
        net_cash_flow = (
            tax_savings
            + option.annual_operating_savings_eur
            - option.annual_operating_cost_eur
        )
        end_of_year_period = period.year - first_year + 1
        discount_factor = (ONE + request.discount_rate) ** end_of_year_period
        discounted_net_cash_flow = net_cash_flow / discount_factor

        total_tax_savings += tax_savings
        total_net_cash_flow += net_cash_flow
        discounted_cash_flows += discounted_net_cash_flow
        annual_results.append(
            AnnualTaxSavings(
                year=period.year,
                baseline_taxable_tco2e=_quantize(baseline_taxable, TONNES_QUANTUM),
                transition_taxable_tco2e=_quantize(transition_taxable, TONNES_QUANTUM),
                avoided_taxable_tco2e=_quantize(avoided_taxable, TONNES_QUANTUM),
                baseline_carbon_cost_eur=_quantize(baseline_cost, MONEY_QUANTUM),
                transition_carbon_cost_eur=_quantize(transition_cost, MONEY_QUANTUM),
                carbon_tax_savings_eur=_quantize(tax_savings, MONEY_QUANTUM),
                net_cash_flow_eur=_quantize(net_cash_flow, MONEY_QUANTUM),
                discounted_net_cash_flow_eur=_quantize(
                    discounted_net_cash_flow, MONEY_QUANTUM
                ),
                formula=f"taxable={TAXABLE_EMISSIONS_FORMULA}; savings={SAVINGS_FORMULA}",
                tax_rate_source=period.tax_rate_source,
                input_reference=period.input_reference,
                baseline_input_reference=request.baseline_input_reference,
            )
        )

    return _UnrankedResult(
        ranking_net_present_savings_eur=(
            discounted_cash_flows - option.initial_investment_eur
        ),
        option_name=option.option_name,
        transitioned_emissions_tco2e=_quantize(transitioned_emissions, TONNES_QUANTUM),
        avoided_emissions_tco2e=_quantize(avoided_emissions, TONNES_QUANTUM),
        total_carbon_tax_savings_eur=_quantize(total_tax_savings, MONEY_QUANTUM),
        net_savings_eur=_quantize(
            total_net_cash_flow - option.initial_investment_eur, MONEY_QUANTUM
        ),
        net_present_savings_eur=_quantize(
            discounted_cash_flows - option.initial_investment_eur, MONEY_QUANTUM
        ),
        annual_results=annual_results,
    )


def optimize_green_transition(request: OptimizationRequest) -> OptimizationResponse:
    """Rank transition options by risk-neutral net present savings.

    All intermediate math uses Decimal and remains unrounded. Only auditable output
    values are rounded (half-up) to six decimal tonnes or euro cents.
    """

    with localcontext() as context:
        context.prec = 34
        evaluated = [_evaluate_option(request, option) for option in request.transition_options]

    ranked = sorted(
        evaluated,
        key=lambda result: (
            -result.ranking_net_present_savings_eur,
            result.option_name,
        ),
    )
    results = [
        TransitionOptimizationResult(
            rank=rank,
            option_name=result.option_name,
            transitioned_emissions_tco2e=result.transitioned_emissions_tco2e,
            avoided_emissions_tco2e=result.avoided_emissions_tco2e,
            total_carbon_tax_savings_eur=result.total_carbon_tax_savings_eur,
            net_savings_eur=result.net_savings_eur,
            net_present_savings_eur=result.net_present_savings_eur,
            annual_results=result.annual_results,
        )
        for rank, result in enumerate(ranked, start=1)
    ]
    return OptimizationResponse(
        baseline_tco2e=_quantize(request.baseline_tco2e, TONNES_QUANTUM),
        recommended_option=results[0].option_name,
        results=results,
    )


def simulate_transformation(scenario: TransformationScenario) -> TransformationResult:
    """Run the original single-period contract using decimal intermediates."""

    reduced_tco2e = _quantize(
        Decimal(str(scenario.baseline_tco2e)) * Decimal(str(scenario.reduction_rate)),
        TONNES_QUANTUM,
    )
    avoided_cost = _quantize(
        reduced_tco2e * Decimal(str(scenario.carbon_price_eur_per_tonne)),
        TONNES_QUANTUM,
    )
    net_savings = _quantize(
        avoided_cost - Decimal(str(scenario.annualized_investment_cost_eur)),
        TONNES_QUANTUM,
    )
    return TransformationResult(
        reduced_tco2e=float(reduced_tco2e),
        avoided_carbon_cost_eur=float(avoided_cost),
        net_savings_eur=float(net_savings),
    )
