from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioListResponse,
    ScenarioResponse,
    ScenarioUpdate,
)

router = APIRouter()


@router.get("", response_model=ScenarioListResponse)
async def list_scenarios(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(select(func.count(Scenario.id)))
    total = total_result.scalar_one()

    result = await db.execute(
        select(Scenario).order_by(Scenario.created_at.desc()).offset(skip).limit(limit)
    )
    items = result.scalars().all()
    return ScenarioListResponse(items=items, total=total)


@router.post("", response_model=ScenarioResponse, status_code=201)
async def create_scenario(
    data: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
):
    scenario = Scenario(
        name=data.name,
        description=data.description,
        seed_event=data.seed_event,
        environment_vars=data.environment_vars.model_dump(),
        duration_minutes=data.duration_minutes,
        agent_count=data.agent_count,
    )
    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)
    return scenario


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
    data: ScenarioUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    update_data = data.model_dump(exclude_unset=True)
    if "environment_vars" in update_data and update_data["environment_vars"] is not None:
        update_data["environment_vars"] = data.environment_vars.model_dump()

    for key, value in update_data.items():
        setattr(scenario, key, value)

    await db.commit()
    await db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=204)
async def delete_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    await db.delete(scenario)
    await db.commit()
