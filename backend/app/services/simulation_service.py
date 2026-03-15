"""Orchestrates the simulation lifecycle as a background task."""

import asyncio
import logging
from uuid import UUID

from sqlalchemy import select

from app.database import async_session
from app.engine.agent_factory import generate_agents_for_scenario
from app.engine.runner import SimulationRunner
from app.models.agent import Agent
from app.models.scenario import Scenario

logger = logging.getLogger(__name__)


async def run_simulation_loop(
    scenario_id: UUID,
    max_ticks: int,
    tick_duration_ms: int,
):
    """Main simulation entry point — runs as an asyncio background task."""
    logger.info(f"Starting simulation for scenario {scenario_id}")

    try:
        async with async_session() as db:
            # Ensure agents exist for this scenario
            agent_count = await _ensure_agents(scenario_id, db)

            # Initialize and run
            runner = SimulationRunner(scenario_id, max_ticks, tick_duration_ms)
            await runner.initialize(db)

            for tick in range(max_ticks):
                logger.info(f"Scenario {scenario_id}: tick {tick + 1}/{max_ticks}")

                await runner.run_tick(tick, db)
                await asyncio.sleep(tick_duration_ms / 1000.0)

            # Finalize results
            await runner.finalize(db)
            logger.info(f"Simulation {scenario_id} completed successfully")

    except asyncio.CancelledError:
        logger.info(f"Simulation {scenario_id} cancelled")
        async with async_session() as db:
            result = await db.execute(
                select(Scenario).where(Scenario.id == scenario_id)
            )
            scenario = result.scalar_one_or_none()
            if scenario:
                scenario.status = "stopped"
                await db.commit()
    except Exception as e:
        logger.error(f"Simulation {scenario_id} failed: {e}", exc_info=True)
        async with async_session() as db:
            result = await db.execute(
                select(Scenario).where(Scenario.id == scenario_id)
            )
            scenario = result.scalar_one_or_none()
            if scenario:
                scenario.status = "failed"
                await db.commit()
    finally:
        from app.api.simulations import remove_simulation
        remove_simulation(scenario_id)


async def _ensure_agents(scenario_id: UUID, db) -> int:
    """Create agents if they don't exist for this scenario."""
    result = await db.execute(
        select(Agent).where(Agent.scenario_id == scenario_id).limit(1)
    )
    if result.scalar_one_or_none():
        count_result = await db.execute(
            select(Agent).where(Agent.scenario_id == scenario_id)
        )
        return len(count_result.scalars().all())

    # Get scenario's agent count
    scenario_result = await db.execute(
        select(Scenario).where(Scenario.id == scenario_id)
    )
    scenario = scenario_result.scalar_one()

    # Generate and insert agents
    agent_configs = generate_agents_for_scenario(scenario_id, scenario.agent_count)

    for config in agent_configs:
        agent = Agent(**{k: v for k, v in config.items() if k != "config"}, config=config.get("config", {}))
        db.add(agent)

    await db.commit()
    logger.info(f"Created {len(agent_configs)} agents for scenario {scenario_id}")
    return len(agent_configs)
