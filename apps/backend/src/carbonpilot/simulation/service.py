from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from carbonpilot.schemas.optimization import (
    AnnualTaxSavings,
    CarbonTaxPeriod,
    GreenTransitionOption,
    OptimizationRequest,
    OptimizationResponse,
    TransformationResult,
    TransformationScenario,
    TransitionOptimizationResult,
)
from carbonpilot.schemas.simulation import (
    SliderCalculationEvidence,
    SliderImpactBreakdown,
    SliderSimulationRequest,
    SliderSimulationResponse,
    TransitionLeverAssumptions,
)


TONNES_QUANTUM = Decimal("0.000001")
MONEY_QUANTUM = Decimal("0.01")
PERCENT_QUANTUM = Decimal("0.0001")
ONE = Decimal("1")
ZERO = Decimal("0")
HUNDRED = Decimal("100")

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
class _CarbonTaxImpact:
    baseline_taxable_tco2e: Decimal
    transition_taxable_tco2e: Decimal
    avoided_taxable_tco2e: Decimal
    baseline_carbon_cost_eur: Decimal
    transition_carbon_cost_eur: Decimal
    carbon_tax_savings_eur: Decimal


def _calculate_carbon_tax_impact(
    baseline_emissions_tco2e: Decimal,
    transitioned_emissions_tco2e: Decimal,
    period: CarbonTaxPeriod,
) -> _CarbonTaxImpact:
    """Apply the shared carbon-tax formula without rounding intermediates."""

    baseline_taxable = _taxable_emissions(
        baseline_emissions_tco2e,
        period.covered_emissions_rate,
        period.free_allowance_tco2e,
    )
    transition_taxable = _taxable_emissions(
        transitioned_emissions_tco2e,
        period.covered_emissions_rate,
        period.free_allowance_tco2e,
    )
    baseline_cost = baseline_taxable * period.carbon_price_eur_per_tco2e
    transition_cost = transition_taxable * period.carbon_price_eur_per_tco2e
    return _CarbonTaxImpact(
        baseline_taxable_tco2e=baseline_taxable,
        transition_taxable_tco2e=transition_taxable,
        avoided_taxable_tco2e=baseline_taxable - transition_taxable,
        baseline_carbon_cost_eur=baseline_cost,
        transition_carbon_cost_eur=transition_cost,
        carbon_tax_savings_eur=baseline_cost - transition_cost,
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
        tax_impact = _calculate_carbon_tax_impact(
            request.baseline_tco2e,
            transitioned_emissions,
            period,
        )
        net_cash_flow = (
            tax_impact.carbon_tax_savings_eur
            + option.annual_operating_savings_eur
            - option.annual_operating_cost_eur
        )
        end_of_year_period = period.year - first_year + 1
        discount_factor = (ONE + request.discount_rate) ** end_of_year_period
        discounted_net_cash_flow = net_cash_flow / discount_factor

        total_tax_savings += tax_impact.carbon_tax_savings_eur
        total_net_cash_flow += net_cash_flow
        discounted_cash_flows += discounted_net_cash_flow
        annual_results.append(
            AnnualTaxSavings(
                year=period.year,
                baseline_taxable_tco2e=_quantize(
                    tax_impact.baseline_taxable_tco2e, TONNES_QUANTUM
                ),
                transition_taxable_tco2e=_quantize(
                    tax_impact.transition_taxable_tco2e, TONNES_QUANTUM
                ),
                avoided_taxable_tco2e=_quantize(
                    tax_impact.avoided_taxable_tco2e, TONNES_QUANTUM
                ),
                baseline_carbon_cost_eur=_quantize(
                    tax_impact.baseline_carbon_cost_eur, MONEY_QUANTUM
                ),
                transition_carbon_cost_eur=_quantize(
                    tax_impact.transition_carbon_cost_eur, MONEY_QUANTUM
                ),
                carbon_tax_savings_eur=_quantize(
                    tax_impact.carbon_tax_savings_eur, MONEY_QUANTUM
                ),
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


@dataclass(frozen=True)
class _LeverImpact:
    emissions_reduction_tco2e: Decimal
    transition_cost_eur: Decimal
    annual_operating_cost_eur: Decimal
    annual_operating_savings_eur: Decimal


def _evaluate_slider_lever(
    baseline_scope_emissions_tco2e: Decimal,
    slider_percent: Decimal,
    assumptions: TransitionLeverAssumptions,
) -> _LeverImpact:
    share = slider_percent / HUNDRED
    return _LeverImpact(
        emissions_reduction_tco2e=(
            baseline_scope_emissions_tco2e
            * share
            * assumptions.emission_reduction_factor
        ),
        transition_cost_eur=assumptions.transition_cost_eur_at_100_percent * share,
        annual_operating_cost_eur=(
            assumptions.annual_operating_cost_eur_at_100_percent * share
        ),
        annual_operating_savings_eur=(
            assumptions.annual_operating_savings_eur_at_100_percent * share
        ),
    )


def _slider_evidence(
    lever: str,
    scope: str,
    slider_percent: Decimal,
    assumptions: TransitionLeverAssumptions,
) -> SliderCalculationEvidence:
    return SliderCalculationEvidence(
        lever=lever,
        scope=scope,
        slider_percent=_quantize(slider_percent, PERCENT_QUANTUM),
        formula=(
            "scope_baseline_tco2e * (slider_percent / 100) "
            "* emission_reduction_factor"
        ),
        factor_source=assumptions.factor_source,
        input_reference=assumptions.input_reference,
    )


def simulate_transition_sliders(
    request: SliderSimulationRequest,
) -> SliderSimulationResponse:
    """Calculate one slider position using exact, deterministic arithmetic.

    Energy and material levers operate only on their respective baseline portions,
    preventing double counting. The resulting projected emissions are passed to the
    same carbon-tax primitive used by the optimization engine.
    """

    with localcontext() as context:
        context.prec = 34
        lever_specs = (
            (
                "solar",
                "energy",
                request.baseline_energy_tco2e,
                request.energy_mix.solar_percent,
                request.solar_assumptions,
            ),
            (
                "wind",
                "energy",
                request.baseline_energy_tco2e,
                request.energy_mix.wind_percent,
                request.wind_assumptions,
            ),
            (
                "recycled_material",
                "material",
                request.baseline_material_tco2e,
                request.material_substitution.recycled_percent,
                request.recycled_material_assumptions,
            ),
            (
                "low_carbon_material",
                "material",
                request.baseline_material_tco2e,
                request.material_substitution.low_carbon_percent,
                request.low_carbon_material_assumptions,
            ),
        )
        impacts = [
            _evaluate_slider_lever(baseline, slider, assumptions)
            for _, _, baseline, slider, assumptions in lever_specs
        ]
        reductions = [impact.emissions_reduction_tco2e for impact in impacts]
        energy_reduction = reductions[0] + reductions[1]
        material_reduction = reductions[2] + reductions[3]
        total_reduction = energy_reduction + material_reduction
        projected_emissions = request.baseline_tco2e - total_reduction
        transition_cost = sum(
            (impact.transition_cost_eur for impact in impacts), start=ZERO
        )
        annual_operating_cost = sum(
            (impact.annual_operating_cost_eur for impact in impacts), start=ZERO
        )
        annual_operating_savings = sum(
            (impact.annual_operating_savings_eur for impact in impacts), start=ZERO
        )

        annual_results: list[AnnualTaxSavings] = []
        total_tax_savings = ZERO
        for period in sorted(request.tax_schedule, key=lambda item: item.year):
            tax_impact = _calculate_carbon_tax_impact(
                request.baseline_tco2e,
                projected_emissions,
                period,
            )
            net_cash_flow = (
                tax_impact.carbon_tax_savings_eur
                + annual_operating_savings
                - annual_operating_cost
            )
            total_tax_savings += tax_impact.carbon_tax_savings_eur
            annual_results.append(
                AnnualTaxSavings(
                    year=period.year,
                    baseline_taxable_tco2e=_quantize(
                        tax_impact.baseline_taxable_tco2e, TONNES_QUANTUM
                    ),
                    transition_taxable_tco2e=_quantize(
                        tax_impact.transition_taxable_tco2e, TONNES_QUANTUM
                    ),
                    avoided_taxable_tco2e=_quantize(
                        tax_impact.avoided_taxable_tco2e, TONNES_QUANTUM
                    ),
                    baseline_carbon_cost_eur=_quantize(
                        tax_impact.baseline_carbon_cost_eur, MONEY_QUANTUM
                    ),
                    transition_carbon_cost_eur=_quantize(
                        tax_impact.transition_carbon_cost_eur, MONEY_QUANTUM
                    ),
                    carbon_tax_savings_eur=_quantize(
                        tax_impact.carbon_tax_savings_eur, MONEY_QUANTUM
                    ),
                    net_cash_flow_eur=_quantize(net_cash_flow, MONEY_QUANTUM),
                    discounted_net_cash_flow_eur=_quantize(
                        net_cash_flow, MONEY_QUANTUM
                    ),
                    formula=(
                        f"taxable={TAXABLE_EMISSIONS_FORMULA}; "
                        f"savings={SAVINGS_FORMULA}"
                    ),
                    tax_rate_source=period.tax_rate_source,
                    input_reference=period.input_reference,
                    baseline_input_reference=request.baseline_input_reference,
                )
            )

        period_count = Decimal(len(request.tax_schedule))
        total_operating_cost = annual_operating_cost * period_count
        total_operating_savings = annual_operating_savings * period_count
        net_savings = (
            total_tax_savings
            + total_operating_savings
            - total_operating_cost
            - transition_cost
        )
        total_cost = transition_cost + total_operating_cost
        roi_percent = (
            None if total_cost == ZERO else (net_savings / total_cost) * HUNDRED
        )
        reduction_percent = (
            ZERO
            if request.baseline_tco2e == ZERO
            else total_reduction / request.baseline_tco2e * HUNDRED
        )

        return SliderSimulationResponse(
            baseline_emissions_tco2e=_quantize(
                request.baseline_tco2e, TONNES_QUANTUM
            ),
            projected_emissions_tco2e=_quantize(
                projected_emissions, TONNES_QUANTUM
            ),
            emissions_reduction_tco2e=_quantize(total_reduction, TONNES_QUANTUM),
            emissions_reduction_percent=_quantize(
                reduction_percent, PERCENT_QUANTUM
            ),
            estimated_carbon_tax_savings_eur=_quantize(
                total_tax_savings, MONEY_QUANTUM
            ),
            transition_cost_eur=_quantize(transition_cost, MONEY_QUANTUM),
            total_operating_cost_eur=_quantize(
                total_operating_cost, MONEY_QUANTUM
            ),
            total_operating_savings_eur=_quantize(
                total_operating_savings, MONEY_QUANTUM
            ),
            net_savings_eur=_quantize(net_savings, MONEY_QUANTUM),
            roi_percent=(
                None if roi_percent is None else _quantize(roi_percent, PERCENT_QUANTUM)
            ),
            impact_breakdown=SliderImpactBreakdown(
                energy_reduction_tco2e=_quantize(
                    energy_reduction, TONNES_QUANTUM
                ),
                material_reduction_tco2e=_quantize(
                    material_reduction, TONNES_QUANTUM
                ),
                solar_reduction_tco2e=_quantize(reductions[0], TONNES_QUANTUM),
                wind_reduction_tco2e=_quantize(reductions[1], TONNES_QUANTUM),
                recycled_material_reduction_tco2e=_quantize(
                    reductions[2], TONNES_QUANTUM
                ),
                low_carbon_material_reduction_tco2e=_quantize(
                    reductions[3], TONNES_QUANTUM
                ),
            ),
            annual_results=annual_results,
            calculation_evidence=[
                _slider_evidence(lever, scope, slider, assumptions)
                for lever, scope, _, slider, assumptions in lever_specs
            ],
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
