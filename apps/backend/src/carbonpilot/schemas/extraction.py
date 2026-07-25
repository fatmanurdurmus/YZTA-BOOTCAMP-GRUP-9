from carbonpilot.schemas.activity import ActivityData
from carbonpilot.schemas.common import StrictBaseModel


class ExtractionResponse(StrictBaseModel):
    candidate_activity_data: ActivityData
    source_filename: str
