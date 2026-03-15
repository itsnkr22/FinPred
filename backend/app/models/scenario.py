import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    seed_event: Mapped[str] = mapped_column(Text, nullable=False)
    environment_vars: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    agent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    agents = relationship("Agent", back_populates="scenario", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="scenario", cascade="all, delete-orphan")
    result = relationship("SimulationResult", back_populates="scenario", uselist=False, cascade="all, delete-orphan")
