"""Stub: US financial news scraper (Bloomberg, WSJ, CNBC)."""

import logging

from app.ingestion.base import BaseScraper, MarketDataItem

logger = logging.getLogger(__name__)


class NewsScraper(BaseScraper):
    """Stub scraper for US financial news sources.

    TODO: Implement real scraping via NewsAPI, RSS feeds, or vendor APIs.
    """

    async def fetch(self, query: str, limit: int = 50) -> list[MarketDataItem]:
        logger.info(f"NewsScraper.fetch called (stub): query={query}, limit={limit}")
        return []

    async def health_check(self) -> bool:
        return True
