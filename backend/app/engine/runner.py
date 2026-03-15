"""Core tick-based simulation loop orchestrating agent interactions."""

import asyncio
import logging
import random
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.engine.agent_factory import LLMAgent, create_camel_agent
from app.engine.environment import SimulatedEnvironment
from app.engine.influence import propagate_influence
from app.engine.metrics import aggregate_tick_metrics, calculate_p_impact, calculate_stance_ratios
from app.engine.personas import PERSONA_CONFIGS
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.models.scenario import Scenario
from app.models.simulation_result import SimulationResult

logger = logging.getLogger(__name__)


class SimulationRunner:
    """Orchestrates a tick-based multi-agent market simulation."""

    def __init__(
        self,
        scenario_id: uuid.UUID,
        max_ticks: int,
        tick_duration_ms: int,
    ):
        self.scenario_id = scenario_id
        self.max_ticks = max_ticks
        self.tick_duration_ms = tick_duration_ms
        self.environment: SimulatedEnvironment | None = None
        self.agents: list[dict] = []
        self.llm_agents: dict[str, LLMAgent] = {}
        self.all_interactions: list[dict] = []
        self.sentiment_timeline: list[dict] = []
        self.agent_sentiments: dict[str, float] = {}

    async def initialize(self, db: AsyncSession):
        """Load scenario and agents from database."""
        result = await db.execute(
            select(Scenario).where(Scenario.id == self.scenario_id)
        )
        scenario = result.scalar_one()

        self.environment = SimulatedEnvironment(
            seed_event=scenario.seed_event,
            environment_vars=scenario.environment_vars,
        )

        agent_result = await db.execute(
            select(Agent).where(Agent.scenario_id == self.scenario_id)
        )
        db_agents = agent_result.scalars().all()

        self.agents = []
        for a in db_agents:
            agent_dict = {
                "id": a.id,
                "persona_type": a.persona_type,
                "display_name": a.display_name,
                "capital_weight": a.capital_weight,
                "risk_tolerance": a.risk_tolerance,
                "influence_score": a.influence_score,
                "system_prompt": a.system_prompt,
                "config": a.config or {},
            }
            self.agents.append(agent_dict)
            self.agent_sentiments[str(a.id)] = 0.0

        # Create LLM agents for those marked as LLM-driven
        for agent_dict in self.agents:
            if agent_dict["config"].get("is_llm_driven", False):
                try:
                    llm_agent = await create_camel_agent(agent_dict, scenario.seed_event)
                    self.llm_agents[str(agent_dict["id"])] = llm_agent
                except Exception as e:
                    logger.warning(f"Failed to create LLM agent: {e}")

        logger.info(
            f"Simulation initialized: {len(self.agents)} agents, "
            f"{len(self.llm_agents)} LLM-driven"
        )

    async def run_tick(self, tick: int, db: AsyncSession) -> list[dict]:
        """Execute a single simulation tick.

        1. Activate subset of agents
        2. Each active agent reads feed + decides action
        3. Record interactions
        4. Propagate influence
        5. Compute metrics
        """
        tick_interactions = []
        active_agents = self._get_active_agents(tick)

        # Update simulation state
        from app.api.simulations import update_simulation_state
        update_simulation_state(self.scenario_id, current_tick=tick, agents_active=len(active_agents))

        for agent in active_agents:
            agent_id = str(agent["id"])
            feed_context = self.environment.get_feed_for_agent(
                agent_id=agent["id"],
                persona_type=agent["persona_type"],
                current_tick=tick,
            )

            # Generate response (LLM or rule-based)
            if agent_id in self.llm_agents:
                response = await self.llm_agents[agent_id].generate_response(feed_context)
            else:
                response = self._rule_based_response(agent, tick)

            if response["action"] == "none":
                continue

            # Create interaction record
            interaction = {
                "id": uuid.uuid4(),
                "scenario_id": self.scenario_id,
                "agent_id": agent["id"],
                "parent_id": self._find_parent_post(response.get("platform", "twitter")),
                "platform": response.get("platform", "twitter"),
                "interaction_type": response.get("action", "post"),
                "content": response.get("content", ""),
                "sentiment_score": response.get("sentiment", 0.0),
                "tick": tick,
                "persona_type": agent["persona_type"],
                "display_name": agent["display_name"],
                "influence_score": agent["influence_score"],
                "stance": response.get("stance", "HOLD"),
            }

            tick_interactions.append(interaction)
            self.all_interactions.append(interaction)

            # Update agent sentiment tracker
            self.agent_sentiments[agent_id] = response.get("sentiment", 0.0)

            # Add to environment feed
            self.environment.add_interaction(interaction)

            # Persist to database
            db_interaction = Interaction(
                id=interaction["id"],
                scenario_id=self.scenario_id,
                agent_id=agent["id"],
                parent_id=interaction["parent_id"],
                platform=interaction["platform"],
                interaction_type=interaction["interaction_type"],
                content=interaction["content"],
                sentiment_score=interaction["sentiment_score"],
                tick=tick,
                metadata_={
                    "stance": interaction["stance"],
                    "persona_type": agent["persona_type"],
                },
            )
            db.add(db_interaction)

        # Propagate influence
        sentiment_deltas = propagate_influence(self.agents, tick_interactions, tick)
        for agent_id, delta in sentiment_deltas.items():
            current = self.agent_sentiments.get(agent_id, 0.0)
            self.agent_sentiments[agent_id] = max(-1.0, min(1.0, current + delta))

        # Compute tick metrics
        tick_metrics = aggregate_tick_metrics(tick, self.all_interactions, self.agents)
        self.sentiment_timeline.append(tick_metrics)

        # Update state
        update_simulation_state(
            self.scenario_id,
            interactions_count=len(self.all_interactions),
        )

        await db.commit()

        # Broadcast via WebSocket
        from app.api.simulations import broadcast_to_scenario
        await broadcast_to_scenario(self.scenario_id, {
            "type": "tick_update",
            "tick": tick,
            "interactions": [
                {
                    "id": str(i["id"]),
                    "agent_name": i["display_name"],
                    "persona_type": i["persona_type"],
                    "platform": i["platform"],
                    "content": i["content"],
                    "sentiment": i["sentiment_score"],
                    "stance": i["stance"],
                }
                for i in tick_interactions
            ],
            "metrics": tick_metrics,
        })

        return tick_interactions

    async def finalize(self, db: AsyncSession):
        """Compute final results and save to database."""
        # Aggregate final metrics
        all_stances = [i.get("stance", "HOLD") for i in self.all_interactions]
        ratios = calculate_stance_ratios(all_stances)

        agent_data = [
            {
                "sentiment": self.agent_sentiments.get(str(a["id"]), 0.0),
                "capital_weight": a["capital_weight"],
            }
            for a in self.agents
        ]
        final_p_impact = calculate_p_impact(agent_data)

        # Find top influencers
        influencer_interactions = {}
        for i in self.all_interactions:
            aid = str(i.get("agent_id", ""))
            if aid not in influencer_interactions:
                influencer_interactions[aid] = {"count": 0, "name": i.get("display_name", ""), "persona": i.get("persona_type", "")}
            influencer_interactions[aid]["count"] += 1

        top_influencers = sorted(
            influencer_interactions.values(),
            key=lambda x: x["count"],
            reverse=True,
        )[:10]

        # Generate emergent narratives (simplified)
        narratives = self._extract_narratives()

        sim_result = SimulationResult(
            scenario_id=self.scenario_id,
            p_impact=final_p_impact,
            buy_ratio=ratios["buy_ratio"],
            sell_ratio=ratios["sell_ratio"],
            hold_ratio=ratios["hold_ratio"],
            sentiment_timeline=self.sentiment_timeline,
            narrative_summary=self._generate_summary(ratios, final_p_impact),
            emergent_narratives=narratives,
            top_influencers=top_influencers,
            raw_metrics={
                "total_interactions": len(self.all_interactions),
                "total_ticks": len(self.sentiment_timeline),
                "agents_count": len(self.agents),
            },
        )
        db.add(sim_result)

        # Update scenario status
        result = await db.execute(
            select(Scenario).where(Scenario.id == self.scenario_id)
        )
        scenario = result.scalar_one()
        scenario.status = "completed"
        scenario.completed_at = datetime.utcnow()

        await db.commit()

        # Broadcast completion
        from app.api.simulations import broadcast_to_scenario
        await broadcast_to_scenario(self.scenario_id, {
            "type": "simulation_complete",
            "p_impact": final_p_impact,
            "ratios": ratios,
        })

    def _get_active_agents(self, tick: int) -> list[dict]:
        """Determine which agents are active this tick based on activity probability."""
        active = []
        for agent in self.agents:
            prob = agent["config"].get("activity_probability", 0.3)
            # HFT agents are more active in early ticks
            if agent["persona_type"] == "hft_algo" and tick < 5:
                prob = min(1.0, prob * 2)
            if random.random() < prob:
                active.append(agent)
        return active

    def _rule_based_response(self, agent: dict, tick: int) -> dict:
        """Generate a rule-based response for non-LLM agents."""
        persona = agent["persona_type"]
        config = PERSONA_CONFIGS.get(persona)
        risk = agent["risk_tolerance"]

        # Base sentiment from current agent state + noise
        base_sentiment = self.agent_sentiments.get(str(agent["id"]), 0.0)
        sentiment = base_sentiment + random.gauss(0, 0.15 * risk)
        sentiment = max(-1.0, min(1.0, sentiment))

        # Determine stance based on sentiment
        if sentiment > 0.2:
            stance = "BUY"
        elif sentiment < -0.2:
            stance = "SELL"
        else:
            stance = "HOLD"

        # Action probability
        if random.random() < 0.4:
            action = "none"
        elif random.random() < 0.7:
            action = "post"
        else:
            action = "comment"

        platforms = agent["config"].get("platforms", ["twitter"])
        platform = random.choice(platforms)

        # Generate content based on persona
        content = self._generate_content(persona, stance, sentiment, tick)

        return {
            "action": action,
            "platform": platform,
            "content": content,
            "sentiment": round(sentiment, 4),
            "stance": stance,
        }

    def _generate_content(self, persona: str, stance: str, sentiment: float, tick: int) -> str:
        """Generate persona-appropriate content."""
        templates = {
            "retail_reddit": {
                "BUY": [
                    "Diamond hands! Loading up more shares. This dip is a gift.",
                    "YOLO'd my paycheck. Apes together strong!",
                    "The DD checks out. I'm going all in. Not financial advice.",
                ],
                "SELL": [
                    "Taking profits here, this feels like a top.",
                    "Paper handing out. Something doesn't feel right.",
                    "Sold everything. The hedgies are up to something.",
                ],
                "HOLD": [
                    "Holding steady. Not selling until we moon.",
                    "Nothing has changed. Still bullish long term.",
                    "HODLing. Not letting them shake me out.",
                ],
            },
            "hft_algo": {
                "BUY": ["Signal: BUY | RSI oversold, volume spike +340%, momentum reversal detected."],
                "SELL": ["Signal: SELL | RSI overbought 78.3, volume declining, mean reversion target -2.1%."],
                "HOLD": ["Signal: NEUTRAL | Insufficient conviction. Spread within normal range."],
            },
            "institutional": {
                "BUY": ["Fundamentals remain strong. Adding to core positions on this pullback."],
                "SELL": ["Reducing exposure. Valuation multiples stretched beyond historical norms."],
                "HOLD": ["Maintaining current allocation. Awaiting Q-data before rebalancing."],
            },
            "macro_hedge": {
                "BUY": ["Risk-on positioning. Yield curve steepening signals growth ahead."],
                "SELL": ["Aggressive short. Credit spreads widening, systemic risk elevating."],
                "HOLD": ["Flat. Waiting for FOMC clarity before committing capital."],
            },
            "finfluencer": {
                "BUY": ["THIS CHANGES EVERYTHING! I just went ALL IN. Here's why you should too..."],
                "SELL": ["I'm OUT. Sold everything this morning. This is going to CRASH."],
                "HOLD": ["Everyone calm down. Here's what's REALLY going on behind the scenes..."],
            },
        }

        persona_templates = templates.get(persona, templates["retail_reddit"])
        stance_templates = persona_templates.get(stance, ["Market update noted."])
        return random.choice(stance_templates)

    def _find_parent_post(self, platform: str) -> uuid.UUID | None:
        """Find a recent post to reply to (for comment interactions)."""
        recent = [
            i for i in self.all_interactions[-20:]
            if i["platform"] == platform and i["interaction_type"] == "post"
        ]
        if recent and random.random() < 0.5:
            return random.choice(recent)["id"]
        return None

    def _extract_narratives(self) -> list[dict]:
        """Extract emergent narrative patterns from interactions."""
        narratives = []

        # Check for finfluencer-driven retail movement
        finfluencer_posts = [i for i in self.all_interactions if i.get("persona_type") == "finfluencer"]
        retail_posts = [i for i in self.all_interactions if i.get("persona_type") == "retail_reddit"]

        if finfluencer_posts and retail_posts:
            avg_fin_sentiment = sum(p.get("sentiment_score", 0) for p in finfluencer_posts) / len(finfluencer_posts)
            avg_retail_sentiment = sum(p.get("sentiment_score", 0) for p in retail_posts) / len(retail_posts)

            if abs(avg_fin_sentiment - avg_retail_sentiment) < 0.2:
                narratives.append({
                    "type": "social_contagion",
                    "description": f"Finfluencer sentiment ({avg_fin_sentiment:.2f}) drove retail alignment ({avg_retail_sentiment:.2f})",
                    "severity": "high" if abs(avg_fin_sentiment) > 0.5 else "medium",
                })

        # Check for institutional vs retail divergence
        institutional_posts = [i for i in self.all_interactions if i.get("persona_type") == "institutional"]
        if institutional_posts and retail_posts:
            avg_inst = sum(p.get("sentiment_score", 0) for p in institutional_posts) / len(institutional_posts)
            avg_ret = sum(p.get("sentiment_score", 0) for p in retail_posts) / len(retail_posts)

            if (avg_inst > 0 and avg_ret < 0) or (avg_inst < 0 and avg_ret > 0):
                narratives.append({
                    "type": "institutional_retail_divergence",
                    "description": f"Institutional ({avg_inst:.2f}) and retail ({avg_ret:.2f}) sentiment diverged significantly",
                    "severity": "high",
                })

        return narratives

    def _generate_summary(self, ratios: dict, p_impact: float) -> str:
        """Generate a text summary of the simulation results."""
        dominant = max(ratios, key=ratios.get)
        dominant_label = dominant.replace("_ratio", "").upper()
        dominant_pct = ratios[dominant] * 100

        direction = "bullish" if p_impact > 0 else "bearish" if p_impact < 0 else "neutral"

        return (
            f"Simulation completed with {len(self.all_interactions)} total interactions "
            f"across {len(self.sentiment_timeline)} ticks. "
            f"The dominant market stance was {dominant_label} ({dominant_pct:.1f}%). "
            f"The overall price impact metric was {direction} at {p_impact:.4f}."
        )
