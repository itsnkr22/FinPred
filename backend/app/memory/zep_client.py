"""Zep Cloud integration for agent long-term memory."""

import logging
from uuid import UUID

from app.config import settings

logger = logging.getLogger(__name__)


class ZepMemoryClient:
    """Manages Zep Cloud sessions for agent memory persistence.

    Each agent gets a session per scenario, allowing them to "remember"
    earlier events in the simulation.
    """

    def __init__(self):
        self.client = None
        self._initialized = False

    async def initialize(self):
        """Initialize the Zep client."""
        if not settings.zep_api_key:
            logger.warning("Zep API key not configured, memory disabled")
            return

        try:
            from zep_cloud.client import AsyncZep

            self.client = AsyncZep(api_key=settings.zep_api_key)
            self._initialized = True
            logger.info("Zep Cloud client initialized")
        except ImportError:
            logger.warning("zep-cloud package not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Zep: {e}")

    async def create_session(self, agent_id: UUID, scenario_id: UUID) -> str | None:
        """Create a Zep session for an agent in a scenario."""
        if not self._initialized:
            return None

        session_id = f"sim_{scenario_id}_{agent_id}"
        try:
            await self.client.memory.add_session(
                session_id=session_id,
                metadata={"agent_id": str(agent_id), "scenario_id": str(scenario_id)},
            )
            return session_id
        except Exception as e:
            logger.error(f"Failed to create Zep session: {e}")
            return None

    async def add_memory(self, session_id: str, role: str, content: str):
        """Add a memory entry to an agent's session."""
        if not self._initialized or not session_id:
            return

        try:
            from zep_cloud.types import Message

            await self.client.memory.add(
                session_id=session_id,
                messages=[Message(role=role, role_type="user", content=content)],
            )
        except Exception as e:
            logger.error(f"Failed to add Zep memory: {e}")

    async def get_memory(self, session_id: str) -> str:
        """Retrieve relevant memory for an agent's session."""
        if not self._initialized or not session_id:
            return ""

        try:
            memory = await self.client.memory.get(session_id=session_id)
            if memory and memory.summary:
                return memory.summary.content
            return ""
        except Exception as e:
            logger.error(f"Failed to get Zep memory: {e}")
            return ""


# Singleton instance
zep_memory = ZepMemoryClient()
