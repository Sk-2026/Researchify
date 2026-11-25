
from pydantic import BaseModel, ConfigDict

from app.models.paper import PaperStatus


class PaperStatusUpdateRequest(BaseModel):
    status: PaperStatus


class PaperStatusResponse(BaseModel):
    paper_id: str
    status: PaperStatus

    model_config = ConfigDict(from_attributes=True)
