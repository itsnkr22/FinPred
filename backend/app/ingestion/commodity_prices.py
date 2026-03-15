"""Commodity price fetcher for Oil (WTI), Gold, and Silver using yfinance."""

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

import yfinance as yf

logger = logging.getLogger(__name__)

# Yahoo Finance ticker symbols
COMMODITY_TICKERS = {
    "oil": {"symbol": "CL=F", "name": "WTI Crude Oil", "unit": "USD/barrel"},
    "gold": {"symbol": "GC=F", "name": "Gold", "unit": "USD/oz"},
    "silver": {"symbol": "SI=F", "name": "Silver", "unit": "USD/oz"},
}


@dataclass
class CommodityPrice:
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


@dataclass
class CommodityHistoryPoint:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


async def fetch_commodity_latest(commodity: str) -> CommodityPrice | None:
    """Fetch latest price data for a commodity."""
    ticker_info = COMMODITY_TICKERS.get(commodity)
    if not ticker_info:
        return None

    try:
        ticker = yf.Ticker(ticker_info["symbol"])
        hist = ticker.history(period="2d")

        if hist.empty:
            return None

        latest = hist.iloc[-1]
        prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Open"]

        change = latest["Close"] - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0.0

        return CommodityPrice(
            commodity=commodity,
            name=ticker_info["name"],
            unit=ticker_info["unit"],
            price=round(float(latest["Close"]), 2),
            change=round(float(change), 2),
            change_percent=round(float(change_pct), 2),
            high=round(float(latest["High"]), 2),
            low=round(float(latest["Low"]), 2),
            open=round(float(latest["Open"]), 2),
            volume=int(latest["Volume"]),
            timestamp=str(hist.index[-1]),
        )
    except Exception as e:
        logger.error(f"Failed to fetch {commodity} price: {e}")
        return None


async def fetch_commodity_history(
    commodity: str, period: str = "1mo"
) -> list[CommodityHistoryPoint]:
    """Fetch historical price data for a commodity.

    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y
    """
    ticker_info = COMMODITY_TICKERS.get(commodity)
    if not ticker_info:
        return []

    try:
        ticker = yf.Ticker(ticker_info["symbol"])
        hist = ticker.history(period=period)

        return [
            CommodityHistoryPoint(
                date=str(idx.date()),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
                volume=int(row["Volume"]),
            )
            for idx, row in hist.iterrows()
        ]
    except Exception as e:
        logger.error(f"Failed to fetch {commodity} history: {e}")
        return []


async def fetch_all_commodities() -> list[CommodityPrice]:
    """Fetch latest prices for all tracked commodities."""
    results = []
    for commodity in COMMODITY_TICKERS:
        price = await fetch_commodity_latest(commodity)
        if price:
            results.append(price)
    return results


def format_commodity_context(prices: list[CommodityPrice]) -> str:
    """Format commodity prices as context string for agent feeds."""
    if not prices:
        return ""

    lines = ["=== Commodity Prices ==="]
    for p in prices:
        direction = "▲" if p.change >= 0 else "▼"
        lines.append(
            f"{p.name}: ${p.price:.2f} {direction} {abs(p.change):.2f} "
            f"({p.change_percent:+.2f}%) | H: ${p.high:.2f} L: ${p.low:.2f}"
        )
    lines.append("")
    return "\n".join(lines)
