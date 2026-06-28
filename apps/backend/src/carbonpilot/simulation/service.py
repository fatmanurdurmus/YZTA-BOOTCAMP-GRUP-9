from pydantic import Field

from carbonpilot.schemas.common import StrictBaseModel


class TransformationScenario(StrictBaseModel):
    baseline_tco2e: float = Field(ge=0)
    carbon_price_eur_per_tonne: float = Field(ge=0)
    reduction_rate: float = Field(ge=0, le=1)
    annualized_investment_cost_eur: float = Field(ge=0)


class TransformationResult(StrictBaseModel):
    reduced_tco2e: float = Field(ge=0)
    avoided_carbon_cost_eur: float
    net_savings_eur: float


def simulate_transformation(scenario: TransformationScenario) -> TransformationResult:
    reduced_tco2e = round(scenario.baseline_tco2e * scenario.reduction_rate, 6)
    avoided_cost = round(reduced_tco2e * scenario.carbon_price_eur_per_tonne, 6)
    return TransformationResult(
        reduced_tco2e=reduced_tco2e,
        avoided_carbon_cost_eur=avoided_cost,
        net_savings_eur=round(avoided_cost - scenario.annualized_investment_cost_eur, 6),
    )
