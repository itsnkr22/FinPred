"""Analytics aggregation service for simulation results."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interaction import Interaction
from app.models.simulation_result import SimulationResult
from app.schemas.simulation import (
    HeatmapDataPoint,
    HeatmapResponse,
    PriceImpactPoint,
    PriceImpactResponse,
)


async def get_heatmap_data(scenario_id: UUID, db: AsyncSession) -> HeatmapResponse:
    """Generate sentiment heatmap data grouped by persona and tick."""
    result = await db.execute(
        select(Interaction)
        .where(Interaction.scenario_id == scenario_id)
        .order_by(Interaction.tick)
    )
    interactions = result.scalars().all()

    # Group by persona_type and tick
    grouped: dict[tuple[str, int], list[float]] = {}
    personas = set()
    max_tick = 0

    for i in interactions:
        persona = (i.metadata_ or {}).get("persona_type", "unknown")
        key = (persona, i.tick)
        personas.add(persona)
        max_tick = max(max_tick, i.tick)

        if key not in grouped:
            grouped[key] = []
        if i.sentiment_score is not None:
            grouped[key].append(i.sentiment_score)

    data = []
    for (persona, tick), sentiments in grouped.items():
        avg = sum(sentiments) / len(sentiments) if sentiments else 0.0

        # Count stances
        tick_interactions = [
            ix for ix in interactions
            if (ix.metadata_ or {}).get("persona_type") == persona and ix.tick == tick
        ]
        stances = [
            (ix.metadata_ or {}).get("stance", "HOLD")
            for ix in tick_interactions
        ]

        data.append(HeatmapDataPoint(
            persona_type=persona,
            tick=tick,
            avg_sentiment=round(avg, 4),
            action_counts={
                "BUY": stances.count("BUY"),
                "SELL": stances.count("SELL"),
                "HOLD": stances.count("HOLD"),
            },
        ))

    return HeatmapResponse(
        data=data,
        personas=sorted(personas),
        ticks=max_tick + 1,
    )


async def get_price_impact_data(scenario_id: UUID, db: AsyncSession) -> PriceImpactResponse:
    """Get P_impact time series from stored simulation results."""
    result = await db.execute(
        select(SimulationResult).where(SimulationResult.scenario_id == scenario_id)
    )
    sim_result = result.scalar_one_or_none()

    if not sim_result or not sim_result.sentiment_timeline:
        return PriceImpactResponse(data=[])

    data = []
    for tick_data in sim_result.sentiment_timeline:
        data.append(PriceImpactPoint(
            tick=tick_data.get("tick", 0),
            p_impact=tick_data.get("p_impact", 0.0),
            by_persona=tick_data.get("by_persona", {}),
        ))

    return PriceImpactResponse(data=data)
