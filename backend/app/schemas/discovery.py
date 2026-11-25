
from pydantic import BaseModel


class DiscoveryRunResponse(BaseModel):
    message: str
    discovered_count: int
    inserted_count: int
    updated_count: int
    sources_added: int
