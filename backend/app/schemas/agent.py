from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AgentResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    persona_type: str
    display_name: str
    capital_weight: float
    risk_tolerance: float
    influence_score: float
    config: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    items: list[AgentResponse]
    total: int
