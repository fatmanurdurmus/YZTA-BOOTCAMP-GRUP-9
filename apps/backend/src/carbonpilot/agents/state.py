from typing import TypedDict

from carbonpilot.schemas.calculation import CalculationResponse
from carbonpilot.schemas.law import LawReference


class CarbonPilotState(TypedDict, total=False):
    thread_id: str
    activity_payload: dict[str, object]
    retries: int
    max_retries: int
    calculation: CalculationResponse
    law_references: list[LawReference]
    critic_passed: bool
    messages: list[str]
