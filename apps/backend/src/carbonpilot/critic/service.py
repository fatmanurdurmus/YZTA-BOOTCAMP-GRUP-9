from carbonpilot.schemas.calculation import CalculationResponse
from carbonpilot.schemas.law import LawReference


def audit_calculation(
    calculation: CalculationResponse, law_references: list[LawReference]
) -> tuple[bool, list[str]]:
    messages: list[str] = []

    if calculation.total_tco2e < 0:
        messages.append("Total emissions cannot be negative.")

    if not calculation.emission_lines:
        messages.append("At least one emission line is required.")

    for line in calculation.emission_lines:
        if not line.factor_source:
            messages.append(f"Missing factor source for {line.activity_name}.")
        if not line.input_reference:
            messages.append(f"Missing input reference for {line.activity_name}.")

    if not law_references:
        messages.append("At least one legal or methodology reference is required.")

    return len(messages) == 0, messages or ["Critic audit passed."]
