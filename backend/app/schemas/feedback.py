
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.feedback import FeedbackType


class FeedbackCreateRequest(BaseModel):
    feedback_type: FeedbackType
    matched_interest: str | None = Field(
        default=None,
        max_length=200,
    )


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    paper_id: UUID
    feedback_type: FeedbackType
    matched_interest: str | None = None
