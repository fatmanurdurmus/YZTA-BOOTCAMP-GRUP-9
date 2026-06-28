from pydantic import Field

from carbonpilot.schemas.activity import ActivityData
from carbonpilot.schemas.common import EmissionScope, StrictBaseModel


class EmissionLine(StrictBaseModel):
    scope: EmissionScope
    category: str = Field(min_length=2)
    activity_name: str = Field(min_length=2)
    co2e_tonnes: float = Field(ge=0)
    formula: str = Field(min_length=2)
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)


class ScopeSummary(StrictBaseModel):
    scope: EmissionScope
    total_tco2e: float = Field(ge=0)


class CalculationRequest(StrictBaseModel):
    activity_data: ActivityData
    carbon_price_eur_per_tonne: float = Field(default=80.0, ge=0)


class CalculationResponse(StrictBaseModel):
    facility_name: str
    reporting_period: str
    scope_summaries: list[ScopeSummary]
    emission_lines: list[EmissionLine]
    total_tco2e: float = Field(ge=0)
    estimated_cbam_cost_eur: float = Field(ge=0)
    methodology_version: str = "carbonpilot-mvp-2026-06"
