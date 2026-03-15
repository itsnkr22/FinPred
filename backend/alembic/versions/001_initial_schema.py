"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-15
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scenarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("seed_event", sa.Text, nullable=False),
        sa.Column("environment_vars", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("duration_minutes", sa.Integer, nullable=False, server_default=sa.text("60")),
        sa.Column("agent_count", sa.Integer, nullable=False, server_default=sa.text("1000")),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scenario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("persona_type", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("capital_weight", sa.Float, nullable=False),
        sa.Column("risk_tolerance", sa.Float, nullable=False),
        sa.Column("influence_score", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("system_prompt", sa.Text, nullable=False),
        sa.Column("config", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_agents_scenario_persona", "agents", ["scenario_id", "persona_type"])

    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scenario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interactions.id"), nullable=True),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("interaction_type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("sentiment_score", sa.Float),
        sa.Column("tick", sa.Integer, nullable=False),
        sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_interactions_scenario_tick", "interactions", ["scenario_id", "tick"])
    op.create_index("ix_interactions_agent", "interactions", ["agent_id"])

    op.create_table(
        "simulation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scenario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("p_impact", sa.Float, nullable=False),
        sa.Column("buy_ratio", sa.Float, nullable=False),
        sa.Column("sell_ratio", sa.Float, nullable=False),
        sa.Column("hold_ratio", sa.Float, nullable=False),
        sa.Column("sentiment_timeline", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("narrative_summary", sa.Text),
        sa.Column("emergent_narratives", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("top_influencers", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("raw_metrics", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("simulation_results")
    op.drop_table("interactions")
    op.drop_table("agents")
    op.drop_table("scenarios")
