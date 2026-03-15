"""Stub: Reddit scraper for r/wallstreetbets and r/investing."""

import logging

from app.ingestion.base import BaseScraper, MarketDataItem

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Stub scraper for Reddit financial subreddits.

    TODO: Implement via Reddit API (PRAW) or Pushshift.
    """

    async def fetch(self, query: str, limit: int = 50) -> list[MarketDataItem]:
        logger.info(f"RedditScraper.fetch called (stub): query={query}, limit={limit}")
        return []

    async def health_check(self) -> bool:
        return True
