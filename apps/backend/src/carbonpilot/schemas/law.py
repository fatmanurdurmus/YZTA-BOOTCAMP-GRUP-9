from pydantic import Field, HttpUrl

from carbonpilot.schemas.common import StrictBaseModel


class SourceLocator(StrictBaseModel):
    document_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    paragraph_start: int = Field(ge=1)
    paragraph_end: int = Field(ge=1)


class LawReference(StrictBaseModel):
    title: str = Field(min_length=2)
    jurisdiction: str = Field(min_length=2)
    url: HttpUrl
    relevance: str = Field(min_length=2)
    source_type: str = Field(min_length=2)
    source_locator: SourceLocator | None = None
