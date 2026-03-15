import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    p_impact: Mapped[float] = mapped_column(Float, nullable=False)
    buy_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    sell_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    hold_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment_timeline: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    narrative_summary: Mapped[str | None] = mapped_column(Text)
    emergent_narratives: Mapped[dict] = mapped_column(JSONB, default=list)
    top_influencers: Mapped[dict] = mapped_column(JSONB, default=list)
    raw_metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scenario = relationship("Scenario", back_populates="result")
