from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SimulationRunRequest(BaseModel):
    tick_duration_ms: int = 2000
    max_ticks: int = 60


class SimulationStatusResponse(BaseModel):
    scenario_id: UUID
    status: str
    current_tick: int
    max_ticks: int
    agents_active: int
    interactions_count: int


class SimulationResultResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    p_impact: float
    buy_ratio: float
    sell_ratio: float
    hold_ratio: float
    sentiment_timeline: list
    narrative_summary: str | None
    emergent_narratives: list
    top_influencers: list
    raw_metrics: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class HeatmapDataPoint(BaseModel):
    persona_type: str
    tick: int
    avg_sentiment: float
    action_counts: dict


class HeatmapResponse(BaseModel):
    data: list[HeatmapDataPoint]
    personas: list[str]
    ticks: int


class PriceImpactPoint(BaseModel):
    tick: int
    p_impact: float
    by_persona: dict


class PriceImpactResponse(BaseModel):
    data: list[PriceImpactPoint]


class NarrativeResponse(BaseModel):
    summary: str
    emergent_narratives: list[dict]
    top_influencers: list[dict]
