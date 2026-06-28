from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)


class EmissionScope(str, Enum):
    scope_1 = "scope_1"
    scope_2 = "scope_2"
    scope_3 = "scope_3"


FactorQuality = Literal[
    "supplier_specific",
    "national_default",
    "cbam_default",
    "internal_estimate",
]


class SourceReference(StrictBaseModel):
    source_name: str = Field(min_length=2)
    url: HttpUrl | None = None
    published_on: date | None = None
    retrieved_on: date | None = None
    note: str | None = None
