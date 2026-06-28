from carbonpilot.schemas.calculation import CalculationResponse
from carbonpilot.schemas.law import LawReference


def build_json_report(
    calculation: CalculationResponse, law_references: list[LawReference]
) -> dict[str, object]:
    return {
        "product": "CarbonPilot AI",
        "report_type": "cbam_skd_mvp_json",
        "methodology_version": calculation.methodology_version,
        "calculation": calculation.model_dump(mode="json"),
        "law_references": [reference.model_dump(mode="json") for reference in law_references],
        "disclaimer": "Bootcamp MVP output; production use requires expert validation.",
    }
