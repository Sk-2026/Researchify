
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResearchProfileCreateRequest(BaseModel):
    domain: str = Field(min_length=2, max_length=150)
    description: str | None = None
    timezone: str = Field(default="Asia/Kolkata", max_length=100)
    digest_time: str = Field(
        default="08:00",
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
    )


class ResearchProfileUpdateRequest(BaseModel):
    domain: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    timezone: str | None = Field(default=None, max_length=100)
    digest_time: str | None = Field(
        default=None,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
    )


class ResearchKeywordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    keyword: str
    category: str | None
    is_excluded: bool


class ResearchProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    domain: str
    description: str | None
    timezone: str
    digest_time: str
    keywords: list[ResearchKeywordResponse] = []


class ResearchKeywordCreateRequest(BaseModel):
    keyword: str = Field(min_length=2, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    is_excluded: bool = False


class ResearchKeywordCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    keyword: str
    category: str | None
    is_excluded: bool
