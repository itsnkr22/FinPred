"""Influence propagation mechanics between agents."""

import random


def propagate_influence(
    agents: list[dict],
    interactions: list[dict],
    tick: int,
) -> dict[str, float]:
    """Calculate sentiment shifts based on agent influence.

    Higher-influence agents (finfluencers, institutional) can shift
    the sentiment of lower-influence agents (retail).

    Returns a mapping of agent_id -> sentiment_delta.
    """
    sentiment_deltas: dict[str, float] = {}

    # Build influence map from this tick's interactions
    influencer_posts = [
        i for i in interactions
        if i["tick"] == tick
        and i["interaction_type"] == "post"
        and i.get("influence_score", 0) > 0.3
    ]

    if not influencer_posts:
        return sentiment_deltas

    # Calculate average influencer sentiment
    avg_influencer_sentiment = sum(
        p.get("sentiment_score", 0) for p in influencer_posts
    ) / len(influencer_posts)

    # Apply influence to susceptible agents
    for agent in agents:
        agent_id = str(agent["id"]) if isinstance(agent.get("id"), object) else agent.get("id", "")

        # Retail agents are most susceptible to influence
        susceptibility = _get_susceptibility(agent.get("persona_type", ""))
        if susceptibility <= 0:
            continue

        # Influence is proportional to susceptibility and influencer strength
        influence_strength = max(p.get("influence_score", 0) for p in influencer_posts)
        delta = avg_influencer_sentiment * susceptibility * influence_strength

        # Add noise
        delta += random.gauss(0, 0.05)
        delta = max(-0.3, min(0.3, delta))  # clamp

        sentiment_deltas[str(agent_id)] = delta

    return sentiment_deltas


def _get_susceptibility(persona_type: str) -> float:
    """How susceptible a persona type is to influence from others."""
    return {
        "retail_reddit": 0.7,
        "hft_algo": 0.0,  # algos don't care about social influence
        "institutional": 0.1,
        "macro_hedge": 0.15,
        "finfluencer": 0.2,  # finfluencers influence each other slightly
    }.get(persona_type, 0.3)


def calculate_agent_influence_update(
    agent_id: str,
    interactions_this_tick: list[dict],
) -> float:
    """Update an agent's influence score based on engagement they received."""
    engagement = sum(
        1 for i in interactions_this_tick
        if str(i.get("parent_agent_id", "")) == agent_id
    )
    return min(engagement * 0.01, 0.1)  # small incremental boost
