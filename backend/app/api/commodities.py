"""API endpoints for commodity price data (Oil, Gold, Silver)."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.ingestion.commodity_prices import (
    COMMODITY_TICKERS,
    fetch_all_commodities,
    fetch_commodity_history,
    fetch_commodity_latest,
)

router = APIRouter()


class CommodityPriceResponse(BaseModel):
    commodity: str
    name: str
    unit: str
    price: float
    change: float
    change_percent: float
    high: float
    low: float
    open: float
    volume: int
    timestamp: str


class CommodityHistoryResponse(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("", response_model=list[CommodityPriceResponse])
async def get_all_commodity_prices():
    """Get latest prices for all tracked commodities (Oil, Gold, Silver)."""
    prices = await fetch_all_commodities()
    if not prices:
        raise HTTPException(status_code=503, detail="Unable to fetch commodity prices")
    return [
        CommodityPriceResponse(
            commodity=p.commodity,
            name=p.name,
            unit=p.unit,
            price=p.price,
            change=p.change,
            change_percent=p.change_percent,
            high=p.high,
            low=p.low,
            open=p.open,
            volume=p.volume,
            timestamp=p.timestamp,
        )
        for p in prices
    ]


@router.get("/tickers")
async def get_available_tickers():
    """List available commodity tickers."""
    return {
        key: {"name": val["name"], "unit": val["unit"]}
        for key, val in COMMODITY_TICKERS.items()
    }


@router.get("/{commodity}", response_model=CommodityPriceResponse)
async def get_commodity_price(commodity: str):
    """Get latest price for a specific commodity (oil, gold, silver)."""
    if commodity not in COMMODITY_TICKERS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown commodity '{commodity}'. Available: {list(COMMODITY_TICKERS.keys())}",
        )

    price = await fetch_commodity_latest(commodity)
    if not price:
        raise HTTPException(status_code=503, detail=f"Unable to fetch {commodity} price")

    return CommodityPriceResponse(
        commodity=price.commodity,
        name=price.name,
        unit=price.unit,
        price=price.price,
        change=price.change,
        change_percent=price.change_percent,
        high=price.high,
        low=price.low,
        open=price.open,
        volume=price.volume,
        timestamp=price.timestamp,
    )


@router.get("/{commodity}/history", response_model=list[CommodityHistoryResponse])
async def get_commodity_history(
    commodity: str,
    period: str = Query(default="1mo", regex="^(1d|5d|1mo|3mo|6mo|1y|5y)$"),
):
    """Get historical prices for a commodity.

    Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y
    """
    if commodity not in COMMODITY_TICKERS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown commodity '{commodity}'. Available: {list(COMMODITY_TICKERS.keys())}",
        )

    history = await fetch_commodity_history(commodity, period)
    if not history:
        raise HTTPException(status_code=503, detail=f"Unable to fetch {commodity} history")

    return [
        CommodityHistoryResponse(
            date=h.date, open=h.open, high=h.high, low=h.low, close=h.close, volume=h.volume
        )
        for h in history
    ]
