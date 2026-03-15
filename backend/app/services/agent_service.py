"""Agent management service."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.agent_factory import generate_agents_for_scenario
from app.models.agent import Agent


async def create_agents_for_scenario(
    scenario_id: UUID,
    agent_count: int,
    db: AsyncSession,
) -> int:
    """Create agent records for a scenario."""
    agent_configs = generate_agents_for_scenario(scenario_id, agent_count)

    for config in agent_configs:
        agent = Agent(
            id=config["id"],
            scenario_id=config["scenario_id"],
            persona_type=config["persona_type"],
            display_name=config["display_name"],
            capital_weight=config["capital_weight"],
            risk_tolerance=config["risk_tolerance"],
            influence_score=config["influence_score"],
            system_prompt=config["system_prompt"],
            config=config.get("config", {}),
        )
        db.add(agent)

    await db.commit()
    return len(agent_configs)


async def get_persona_distribution(scenario_id: UUID, db: AsyncSession) -> dict:
    """Get the distribution of persona types for a scenario."""
    result = await db.execute(
        select(Agent.persona_type, func.count(Agent.id))
        .where(Agent.scenario_id == scenario_id)
        .group_by(Agent.persona_type)
    )
    return dict(result.all())
