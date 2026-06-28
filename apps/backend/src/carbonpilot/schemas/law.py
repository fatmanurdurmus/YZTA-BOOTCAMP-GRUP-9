from pydantic import Field, HttpUrl

from carbonpilot.schemas.common import StrictBaseModel


class LawReference(StrictBaseModel):
    title: str = Field(min_length=2)
    jurisdiction: str = Field(min_length=2)
    url: HttpUrl
    relevance: str = Field(min_length=2)
    source_type: str = Field(min_length=2)
