"""Scenario management service."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scenario import Scenario


async def get_scenario_stats(db: AsyncSession) -> dict:
    """Get aggregate stats across all scenarios."""
    total = await db.execute(select(func.count(Scenario.id)))
    completed = await db.execute(
        select(func.count(Scenario.id)).where(Scenario.status == "completed")
    )
    running = await db.execute(
        select(func.count(Scenario.id)).where(Scenario.status == "running")
    )

    return {
        "total": total.scalar_one(),
        "completed": completed.scalar_one(),
        "running": running.scalar_one(),
    }
