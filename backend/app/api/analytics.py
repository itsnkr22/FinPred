from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.simulation_result import SimulationResult
from app.schemas.simulation import (
    HeatmapResponse,
    NarrativeResponse,
    PriceImpactResponse,
    SimulationResultResponse,
)
from app.services.analytics_service import (
    get_heatmap_data,
    get_price_impact_data,
)

router = APIRouter()


@router.get("/{scenario_id}", response_model=SimulationResultResponse)
async def get_analytics(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SimulationResult).where(SimulationResult.scenario_id == scenario_id)
    )
    sim_result = result.scalar_one_or_none()
    if not sim_result:
        raise HTTPException(status_code=404, detail="No results found for this scenario")
    return sim_result


@router.get("/{scenario_id}/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_heatmap_data(scenario_id, db)


@router.get("/{scenario_id}/price-impact", response_model=PriceImpactResponse)
async def get_price_impact(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_price_impact_data(scenario_id, db)


@router.get("/{scenario_id}/narratives", response_model=NarrativeResponse)
async def get_narratives(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SimulationResult).where(SimulationResult.scenario_id == scenario_id)
    )
    sim_result = result.scalar_one_or_none()
    if not sim_result:
        raise HTTPException(status_code=404, detail="No results found")

    return NarrativeResponse(
        summary=sim_result.narrative_summary or "",
        emergent_narratives=sim_result.emergent_narratives or [],
        top_influencers=sim_result.top_influencers or [],
    )


@router.post("/{scenario_id}/report")
async def generate_report(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    from app.services.report_service import generate_b2b_report

    report = await generate_b2b_report(scenario_id, db)
    return {"report": report}
