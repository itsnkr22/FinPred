import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db
from app.models.interaction import Interaction
from app.models.scenario import Scenario
from app.schemas.simulation import SimulationRunRequest, SimulationStatusResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory tracking of running simulations
_running_simulations: dict[UUID, dict] = {}
_websocket_connections: dict[UUID, list[WebSocket]] = {}


@router.post("/{scenario_id}/run", response_model=SimulationStatusResponse)
async def run_simulation(
    scenario_id: UUID,
    request: SimulationRunRequest = SimulationRunRequest(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if scenario_id in _running_simulations:
        raise HTTPException(status_code=409, detail="Simulation already running")

    scenario.status = "running"
    await db.commit()

    _running_simulations[scenario_id] = {
        "current_tick": 0,
        "max_ticks": request.max_ticks,
        "agents_active": 0,
        "interactions_count": 0,
        "task": None,
    }

    # Launch simulation in background
    from app.services.simulation_service import run_simulation_loop

    task = asyncio.create_task(
        run_simulation_loop(scenario_id, request.max_ticks, request.tick_duration_ms)
    )
    _running_simulations[scenario_id]["task"] = task

    return SimulationStatusResponse(
        scenario_id=scenario_id,
        status="running",
        current_tick=0,
        max_ticks=request.max_ticks,
        agents_active=0,
        interactions_count=0,
    )


@router.get("/{scenario_id}/status", response_model=SimulationStatusResponse)
async def get_simulation_status(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    sim_state = _running_simulations.get(scenario_id)
    if sim_state:
        return SimulationStatusResponse(
            scenario_id=scenario_id,
            status="running",
            current_tick=sim_state["current_tick"],
            max_ticks=sim_state["max_ticks"],
            agents_active=sim_state["agents_active"],
            interactions_count=sim_state["interactions_count"],
        )

    count_result = await db.execute(
        select(func.count(Interaction.id)).where(Interaction.scenario_id == scenario_id)
    )
    interactions_count = count_result.scalar_one()

    return SimulationStatusResponse(
        scenario_id=scenario_id,
        status=scenario.status,
        current_tick=0,
        max_ticks=0,
        agents_active=0,
        interactions_count=interactions_count,
    )


@router.post("/{scenario_id}/stop")
async def stop_simulation(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    sim_state = _running_simulations.get(scenario_id)
    if not sim_state:
        raise HTTPException(status_code=404, detail="No running simulation found")

    task = sim_state.get("task")
    if task:
        task.cancel()

    del _running_simulations[scenario_id]

    result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if scenario:
        scenario.status = "stopped"
        await db.commit()

    return {"status": "stopped"}


@router.websocket("/{scenario_id}/ws")
async def simulation_websocket(websocket: WebSocket, scenario_id: UUID):
    await websocket.accept()

    if scenario_id not in _websocket_connections:
        _websocket_connections[scenario_id] = []
    _websocket_connections[scenario_id].append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _websocket_connections[scenario_id].remove(websocket)
        if not _websocket_connections[scenario_id]:
            del _websocket_connections[scenario_id]


async def broadcast_to_scenario(scenario_id: UUID, data: dict):
    connections = _websocket_connections.get(scenario_id, [])
    for ws in connections:
        try:
            await ws.send_json(data)
        except Exception:
            pass


def update_simulation_state(scenario_id: UUID, **kwargs):
    if scenario_id in _running_simulations:
        _running_simulations[scenario_id].update(kwargs)


def remove_simulation(scenario_id: UUID):
    _running_simulations.pop(scenario_id, None)
