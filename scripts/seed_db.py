"""Seed the database with sample scenarios and agents."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import settings
from app.database import engine, async_session, Base
from app.models import Scenario, Agent
from app.engine.agent_factory import generate_agents_for_scenario
from app.ingestion.mock_data import SAMPLE_SCENARIOS


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Check if already seeded
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Scenario.id)))
        if result.scalar_one() > 0:
            print("Database already seeded. Skipping.")
            return

        for scenario_data in SAMPLE_SCENARIOS:
            scenario = Scenario(
                name=scenario_data["name"],
                description=scenario_data["description"],
                seed_event=scenario_data["seed_event"],
                environment_vars=scenario_data["environment_vars"],
                duration_minutes=60,
                agent_count=50,
            )
            db.add(scenario)
            await db.flush()

            # Generate agents
            agent_configs = generate_agents_for_scenario(scenario.id, 50)
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

            print(f"Created scenario: {scenario.name} with {len(agent_configs)} agents")

        await db.commit()
        print("\nDatabase seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
