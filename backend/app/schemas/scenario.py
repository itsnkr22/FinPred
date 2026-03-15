from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EnvironmentVars(BaseModel):
    market_volatility: str = Field(default="normal", description="low | normal | high | extreme")
    sector_focus: str = Field(default="general", description="tech | finance | energy | crypto | commodities | general")
    election_year: bool = False
    fed_stance: str = Field(default="neutral", description="hawkish | neutral | dovish")


class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    seed_event: str = Field(..., min_length=1, description="The breaking news or event to simulate")
    environment_vars: EnvironmentVars = Field(default_factory=EnvironmentVars)
    duration_minutes: int = Field(default=60, ge=1, le=1440)
    agent_count: int = Field(default=50, ge=10, le=1000)


class ScenarioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    seed_event: str | None = None
    environment_vars: EnvironmentVars | None = None
    duration_minutes: int | None = Field(None, ge=1, le=1440)
    agent_count: int | None = Field(None, ge=10, le=1000)


class ScenarioResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    seed_event: str
    environment_vars: dict
    duration_minutes: int
    agent_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ScenarioListResponse(BaseModel):
    items: list[ScenarioResponse]
    total: int
