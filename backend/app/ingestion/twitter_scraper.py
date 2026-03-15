"""Stub: X/Twitter scraper for financial sentiment."""

import logging

from app.ingestion.base import BaseScraper, MarketDataItem

logger = logging.getLogger(__name__)


class TwitterScraper(BaseScraper):
    """Stub scraper for X/Twitter financial content.

    TODO: Implement via X API v2 or third-party provider.
    """

    async def fetch(self, query: str, limit: int = 50) -> list[MarketDataItem]:
        logger.info(f"TwitterScraper.fetch called (stub): query={query}, limit={limit}")
        return []

    async def health_check(self) -> bool:
        return True
