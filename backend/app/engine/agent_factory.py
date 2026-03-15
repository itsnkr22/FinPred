"""Creates CAMEL-AI ChatAgent instances for each persona type."""

import json
import logging
import random
import uuid

from app.engine.personas import PERSONA_CONFIGS, PersonaConfig

logger = logging.getLogger(__name__)


def generate_agents_for_scenario(
    scenario_id: uuid.UUID,
    agent_count: int = 50,
) -> list[dict]:
    """Generate agent configurations for a scenario.

    Returns a list of dicts ready for database insertion.
    """
    agents = []

    for persona_type, config in PERSONA_CONFIGS.items():
        count = max(1, int(agent_count * config.percentage))

        for i in range(count):
            agent = _create_agent_config(scenario_id, config, i)
            agents.append(agent)

    # Trim or pad to exact count
    if len(agents) > agent_count:
        agents = agents[:agent_count]
    elif len(agents) < agent_count:
        # Fill remaining with retail
        retail_config = PERSONA_CONFIGS["retail_reddit"]
        for i in range(agent_count - len(agents)):
            agents.append(_create_agent_config(scenario_id, retail_config, 1000 + i))

    return agents


def _create_agent_config(
    scenario_id: uuid.UUID,
    config: PersonaConfig,
    index: int,
) -> dict:
    """Create a single agent configuration dict."""
    return {
        "id": uuid.uuid4(),
        "scenario_id": scenario_id,
        "persona_type": config.persona_type,
        "display_name": f"{config.display_prefix}_{index:04d}",
        "capital_weight": random.uniform(*config.capital_weight_range),
        "risk_tolerance": random.uniform(*config.risk_tolerance_range),
        "influence_score": random.uniform(*config.influence_score_range),
        "system_prompt": config.system_prompt,
        "config": {
            "activity_probability": config.activity_probability,
            "platforms": config.platforms,
            "is_llm_driven": index < 5,  # first 5 of each type are LLM-driven
        },
    }


async def create_camel_agent(agent_config: dict, seed_event: str) -> "LLMAgent":
    """Create a CAMEL-AI ChatAgent for an LLM-driven agent.

    Falls back to a lightweight wrapper if CAMEL-AI is not available.
    """
    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType

        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type="gpt-4o-mini",
        )

        system_message = agent_config["system_prompt"] + f"\n\nCurrent market event: {seed_event}"

        camel_agent = ChatAgent(
            system_message=system_message,
            model=model,
        )

        return LLMAgent(
            agent_id=agent_config["id"],
            persona_type=agent_config["persona_type"],
            camel_agent=camel_agent,
        )
    except ImportError:
        logger.warning("CAMEL-AI not available, using stub agent")
        return LLMAgent(
            agent_id=agent_config["id"],
            persona_type=agent_config["persona_type"],
            camel_agent=None,
        )


class LLMAgent:
    """Wrapper around a CAMEL ChatAgent for use in the simulation."""

    def __init__(self, agent_id: uuid.UUID, persona_type: str, camel_agent=None):
        self.agent_id = agent_id
        self.persona_type = persona_type
        self.camel_agent = camel_agent

    async def generate_response(self, feed_context: str) -> dict:
        """Generate a response given the current feed context.

        Returns structured output: {action, platform, content, sentiment, stance}
        """
        if self.camel_agent is None:
            return self._stub_response()

        try:
            from camel.messages import BaseMessage

            user_msg = BaseMessage.make_user_message(
                role_name="MarketSimulator",
                content=f"Based on the current market activity, decide your next action:\n\n{feed_context}\n\nRespond with valid JSON only.",
            )
            response = self.camel_agent.step(user_msg)
            content = response.msgs[0].content if response.msgs else ""

            return self._parse_response(content)
        except Exception as e:
            logger.error(f"Agent {self.agent_id} error: {e}")
            return self._stub_response()

    def _parse_response(self, content: str) -> dict:
        """Parse LLM response into structured output."""
        try:
            # Try to extract JSON from the response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except (json.JSONDecodeError, ValueError):
            pass

        return self._stub_response()

    def _stub_response(self) -> dict:
        """Generate a rule-based fallback response."""
        actions = ["post", "comment", "none", "none"]
        platforms = ["twitter", "reddit"]
        stances = ["BUY", "SELL", "HOLD"]

        return {
            "action": random.choice(actions),
            "platform": random.choice(platforms),
            "content": f"[{self.persona_type}] Market update noted. Adjusting positions.",
            "sentiment": random.uniform(-0.5, 0.5),
            "stance": random.choice(stances),
        }
