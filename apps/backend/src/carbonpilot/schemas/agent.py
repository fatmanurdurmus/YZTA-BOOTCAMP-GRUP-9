from pydantic import Field

from carbonpilot.schemas.activity import ActivityData
from carbonpilot.schemas.calculation import CalculationResponse
from carbonpilot.schemas.common import StrictBaseModel


class AgentRunRequest(StrictBaseModel):
    thread_id: str = Field(min_length=3)
    activity_data: ActivityData
    carbon_price_eur_per_tonne: float = Field(default=80.0, ge=0)
    max_retries: int = Field(default=2, ge=0, le=5)
    timeout_seconds: int = Field(default=30, ge=1, le=300)


class AgentRunResponse(StrictBaseModel):
    thread_id: str
    status: str
    calculation: CalculationResponse
    law_reference_count: int
    critic_passed: bool
    messages: list[str]
