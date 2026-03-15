from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentListResponse, AgentResponse

router = APIRouter()


@router.get("/scenarios/{scenario_id}/agents", response_model=AgentListResponse)
async def list_agents(
    scenario_id: UUID,
    persona_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(Agent).where(Agent.scenario_id == scenario_id)
    count_query = select(func.count(Agent.id)).where(Agent.scenario_id == scenario_id)

    if persona_type:
        query = query.where(Agent.persona_type == persona_type)
        count_query = count_query.where(Agent.persona_type == persona_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    return AgentListResponse(items=items, total=total)


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
