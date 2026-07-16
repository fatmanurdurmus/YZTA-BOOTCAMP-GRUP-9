from decimal import Decimal
from typing import Annotated

from pydantic import BeforeValidator, Field, model_validator

from carbonpilot.schemas.common import StrictBaseModel


ZERO = Decimal("0")
ONE = Decimal("1")


def _parse_exact_decimal(value: object) -> object:
    """Accept exact JSON representations without passing through binary floats."""

    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise ValueError("boolean is not a decimal value")
    if isinstance(value, (str, int)):
        try:
            return Decimal(value)
        except Exception as exc:
            raise ValueError("value must be a valid decimal string or integer") from exc
    raise ValueError("decimal values must be sent as JSON strings or integers")


ExactDecimal = Annotated[Decimal, BeforeValidator(_parse_exact_decimal)]


class CarbonTaxPeriod(StrictBaseModel):
    """Configurable tax assumptions for one compliance year."""

    year: int = Field(ge=2000, le=2200)
    carbon_price_eur_per_tco2e: ExactDecimal = Field(ge=ZERO)
    covered_emissions_rate: ExactDecimal = Field(default=ONE, ge=ZERO, le=ONE)
    free_allowance_tco2e: ExactDecimal = Field(default=ZERO, ge=ZERO)
    tax_rate_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)


class GreenTransitionOption(StrictBaseModel):
    option_name: str = Field(min_length=2)
    emission_reduction_rate: ExactDecimal = Field(ge=ZERO, le=ONE)
    initial_investment_eur: ExactDecimal = Field(default=ZERO, ge=ZERO)
    annual_operating_cost_eur: ExactDecimal = Field(default=ZERO, ge=ZERO)
    annual_operating_savings_eur: ExactDecimal = Field(default=ZERO, ge=ZERO)


class OptimizationRequest(StrictBaseModel):
    baseline_tco2e: ExactDecimal = Field(ge=ZERO)
    baseline_input_reference: str = Field(min_length=2)
    discount_rate: ExactDecimal = Field(default=ZERO, ge=ZERO, lt=ONE)
    tax_schedule: list[CarbonTaxPeriod] = Field(min_length=1)
    transition_options: list[GreenTransitionOption] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_inputs(self) -> "OptimizationRequest":
        years = [period.year for period in self.tax_schedule]
        if len(years) != len(set(years)):
            raise ValueError("tax_schedule years must be unique")

        names = [option.option_name for option in self.transition_options]
        if len(names) != len(set(names)):
            raise ValueError("transition option names must be unique")
        return self


class AnnualTaxSavings(StrictBaseModel):
    year: int
    baseline_taxable_tco2e: Decimal = Field(ge=ZERO)
    transition_taxable_tco2e: Decimal = Field(ge=ZERO)
    avoided_taxable_tco2e: Decimal = Field(ge=ZERO)
    baseline_carbon_cost_eur: Decimal = Field(ge=ZERO)
    transition_carbon_cost_eur: Decimal = Field(ge=ZERO)
    carbon_tax_savings_eur: Decimal = Field(ge=ZERO)
    net_cash_flow_eur: Decimal
    discounted_net_cash_flow_eur: Decimal
    formula: str
    tax_rate_source: str
    input_reference: str
    baseline_input_reference: str


class TransitionOptimizationResult(StrictBaseModel):
    rank: int = Field(ge=1)
    option_name: str
    transitioned_emissions_tco2e: Decimal = Field(ge=ZERO)
    avoided_emissions_tco2e: Decimal = Field(ge=ZERO)
    total_carbon_tax_savings_eur: Decimal = Field(ge=ZERO)
    net_savings_eur: Decimal
    net_present_savings_eur: Decimal
    annual_results: list[AnnualTaxSavings]


class OptimizationResponse(StrictBaseModel):
    baseline_tco2e: Decimal = Field(ge=ZERO)
    recommended_option: str
    results: list[TransitionOptimizationResult]
    methodology_version: str = "carbonpilot-green-transition-2026-07"


class TransformationScenario(StrictBaseModel):
    """Legacy single-period simulation contract retained for compatibility."""

    baseline_tco2e: float = Field(ge=0)
    carbon_price_eur_per_tonne: float = Field(ge=0)
    reduction_rate: float = Field(ge=0, le=1)
    annualized_investment_cost_eur: float = Field(ge=0)


class TransformationResult(StrictBaseModel):
    reduced_tco2e: float = Field(ge=0)
    avoided_carbon_cost_eur: float
    net_savings_eur: float
