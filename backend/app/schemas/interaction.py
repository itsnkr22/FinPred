from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InteractionResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    agent_id: UUID
    parent_id: UUID | None
    platform: str
    interaction_type: str
    content: str | None
    sentiment_score: float | None
    tick: int
    metadata_: dict
    created_at: datetime

    model_config = {"from_attributes": True}
