"""Abstract scraper interface for the BettaFish Lite ingestion layer."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketDataItem:
    source: str
    content: str
    author: str
    timestamp: datetime
    sentiment: float | None = None
    url: str | None = None
    engagement: int = 0
    metadata: dict | None = None


class BaseScraper(ABC):
    """Abstract base for all data scrapers."""

    @abstractmethod
    async def fetch(self, query: str, limit: int = 50) -> list[MarketDataItem]:
        """Fetch data items matching the query."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the scraper source is available."""
        ...
