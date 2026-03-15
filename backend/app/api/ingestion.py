from fastapi import APIRouter

from app.ingestion.mock_data import get_mock_market_data

router = APIRouter()

_ingestion_status = {"status": "idle", "last_run": None}


@router.post("/seed")
async def seed_data():
    data = get_mock_market_data()
    _ingestion_status["status"] = "completed"
    return {"status": "seeded", "items": len(data)}


@router.get("/status")
async def ingestion_status():
    return _ingestion_status
