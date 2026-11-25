
from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class RecommendedPaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    abstract: str | None = None
    doi: str | None = None
    publication_date: date | None = None
    authors: list[str] = Field(default_factory=list)
    venue: str | None = None
    citation_count: int | None = None

    final_score: float
    semantic_score: float
    keyword_score: float
    recency_score: float
    feedback_score: float

    
    matched_keywords: list[str] = Field(default_factory=list)
    matched_interest: str | None = None


class RecommendationListResponse(BaseModel):
    total: int
    recommendations: list[RecommendedPaperResponse]
