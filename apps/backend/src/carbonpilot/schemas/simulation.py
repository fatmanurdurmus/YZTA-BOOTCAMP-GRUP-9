from decimal import Decimal

from pydantic import Field, model_validator

from carbonpilot.schemas.common import StrictBaseModel
from carbonpilot.schemas.optimization import AnnualTaxSavings, CarbonTaxPeriod, ExactDecimal


ZERO = Decimal("0")
HUNDRED = Decimal("100")
ONE = Decimal("1")


class EnergyMixScenario(StrictBaseModel):
    """Energy shares selected by the interactive sliders."""

    solar_percent: ExactDecimal = Field(default=ZERO, ge=ZERO, le=HUNDRED)
    wind_percent: ExactDecimal = Field(default=ZERO, ge=ZERO, le=HUNDRED)

    @model_validator(mode="after")
    def validate_total_mix(self) -> "EnergyMixScenario":
        if self.solar_percent + self.wind_percent > HUNDRED:
            raise ValueError("solar_percent + wind_percent must not exceed 100")
        return self


class MaterialSubstitutionScenario(StrictBaseModel):
    """Material shares selected by the interactive sliders."""

    recycled_percent: ExactDecimal = Field(default=ZERO, ge=ZERO, le=HUNDRED)
    low_carbon_percent: ExactDecimal = Field(default=ZERO, ge=ZERO, le=HUNDRED)

    @model_validator(mode="after")
    def validate_total_substitution(self) -> "MaterialSubstitutionScenario":
        if self.recycled_percent + self.low_carbon_percent > HUNDRED:
            raise ValueError(
                "recycled_percent + low_carbon_percent must not exceed 100"
            )
        return self


class TransitionLeverAssumptions(StrictBaseModel):
    """Auditable impact and cost assumptions for one slider lever at 100%."""

    emission_reduction_factor: ExactDecimal = Field(ge=ZERO, le=ONE)
    transition_cost_eur_at_100_percent: ExactDecimal = Field(default=ZERO, ge=ZERO)
    annual_operating_cost_eur_at_100_percent: ExactDecimal = Field(
        default=ZERO, ge=ZERO
    )
    annual_operating_savings_eur_at_100_percent: ExactDecimal = Field(
        default=ZERO, ge=ZERO
    )
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)


class SliderSimulationRequest(StrictBaseModel):
    baseline_tco2e: ExactDecimal = Field(ge=ZERO)
    baseline_energy_tco2e: ExactDecimal = Field(ge=ZERO)
    baseline_material_tco2e: ExactDecimal = Field(ge=ZERO)
    baseline_input_reference: str = Field(min_length=2)
    energy_mix: EnergyMixScenario
    material_substitution: MaterialSubstitutionScenario
    solar_assumptions: TransitionLeverAssumptions
    wind_assumptions: TransitionLeverAssumptions
    recycled_material_assumptions: TransitionLeverAssumptions
    low_carbon_material_assumptions: TransitionLeverAssumptions
    tax_schedule: list[CarbonTaxPeriod] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_baseline_and_schedule(self) -> "SliderSimulationRequest":
        allocated = self.baseline_energy_tco2e + self.baseline_material_tco2e
        if allocated > self.baseline_tco2e:
            raise ValueError(
                "baseline_energy_tco2e + baseline_material_tco2e "
                "must not exceed baseline_tco2e"
            )

        years = [period.year for period in self.tax_schedule]
        if len(years) != len(set(years)):
            raise ValueError("tax_schedule years must be unique")
        return self


class SliderImpactBreakdown(StrictBaseModel):
    energy_reduction_tco2e: Decimal = Field(ge=ZERO)
    material_reduction_tco2e: Decimal = Field(ge=ZERO)
    solar_reduction_tco2e: Decimal = Field(ge=ZERO)
    wind_reduction_tco2e: Decimal = Field(ge=ZERO)
    recycled_material_reduction_tco2e: Decimal = Field(ge=ZERO)
    low_carbon_material_reduction_tco2e: Decimal = Field(ge=ZERO)


class SliderCalculationEvidence(StrictBaseModel):
    lever: str
    scope: str
    slider_percent: Decimal = Field(ge=ZERO, le=HUNDRED)
    formula: str
    factor_source: str
    input_reference: str


class SliderSimulationResponse(StrictBaseModel):
    baseline_emissions_tco2e: Decimal = Field(ge=ZERO)
    projected_emissions_tco2e: Decimal = Field(ge=ZERO)
    emissions_reduction_tco2e: Decimal = Field(ge=ZERO)
    emissions_reduction_percent: Decimal = Field(ge=ZERO, le=HUNDRED)
    estimated_carbon_tax_savings_eur: Decimal = Field(ge=ZERO)
    transition_cost_eur: Decimal = Field(ge=ZERO)
    total_operating_cost_eur: Decimal = Field(ge=ZERO)
    total_operating_savings_eur: Decimal = Field(ge=ZERO)
    net_savings_eur: Decimal
    roi_percent: Decimal | None
    impact_breakdown: SliderImpactBreakdown
    annual_results: list[AnnualTaxSavings]
    calculation_evidence: list[SliderCalculationEvidence]
    methodology_version: str = "carbonpilot-transition-slider-2026-07"
