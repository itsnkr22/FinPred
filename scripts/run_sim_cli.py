"""CLI runner for quick simulation testing without the frontend."""

import asyncio
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import settings
from app.database import engine, async_session, Base
from app.models import Scenario, Agent
from app.engine.agent_factory import generate_agents_for_scenario
from app.engine.runner import SimulationRunner


async def run_cli_simulation(
    seed_event: str = "BREAKING: Federal Reserve announces emergency 50bp rate cut.",
    agent_count: int = 20,
    max_ticks: int = 10,
):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Create scenario
        scenario = Scenario(
            name="CLI Test Simulation",
            description="Quick test via CLI",
            seed_event=seed_event,
            environment_vars={
                "market_volatility": "high",
                "sector_focus": "general",
                "election_year": False,
                "fed_stance": "dovish",
            },
            duration_minutes=30,
            agent_count=agent_count,
            status="running",
        )
        db.add(scenario)
        await db.flush()

        # Generate agents
        agent_configs = generate_agents_for_scenario(scenario.id, agent_count)
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

        print(f"Created scenario: {scenario.id}")
        print(f"Agents: {agent_count}")
        print(f"Seed event: {seed_event[:80]}...")
        print(f"Max ticks: {max_ticks}")
        print("=" * 60)

        # Run simulation
        runner = SimulationRunner(scenario.id, max_ticks, tick_duration_ms=500)
        await runner.initialize(db)

        for tick in range(max_ticks):
            interactions = await runner.run_tick(tick, db)
            print(f"\nTick {tick + 1}/{max_ticks} — {len(interactions)} interactions")

            for ix in interactions[:3]:  # Show first 3
                stance_icon = {"BUY": "+", "SELL": "-", "HOLD": "="}[ix["stance"]]
                print(f"  [{stance_icon}] @{ix['display_name']}: {ix['content'][:80]}")

            if len(interactions) > 3:
                print(f"  ... and {len(interactions) - 3} more")

        await runner.finalize(db)

        print("\n" + "=" * 60)
        print("SIMULATION COMPLETE")
        print("=" * 60)

        # Print results
        from sqlalchemy import select
        from app.models.simulation_result import SimulationResult
        result = await db.execute(
            select(SimulationResult).where(SimulationResult.scenario_id == scenario.id)
        )
        sim_result = result.scalar_one()

        print(f"\nP_impact: {sim_result.p_impact:.4f}")
        print(f"BUY:  {sim_result.buy_ratio:.1%}")
        print(f"SELL: {sim_result.sell_ratio:.1%}")
        print(f"HOLD: {sim_result.hold_ratio:.1%}")
        print(f"\n{sim_result.narrative_summary}")


if __name__ == "__main__":
    event = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_cli_simulation(
        seed_event=event or "BREAKING: Federal Reserve announces emergency 50bp rate cut amid deteriorating economic conditions.",
        agent_count=20,
        max_ticks=10,
    ))
