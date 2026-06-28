from carbonpilot.schemas.activity import ActivityData


def validate_candidate_activity_payload(payload: dict[str, object]) -> ActivityData:
    return ActivityData.model_validate(payload, strict=True)
