"""Simulation metrics calculation — P_impact, sentiment scoring, and aggregation."""


def calculate_p_impact(agents_with_sentiment: list[dict]) -> float:
    """Calculate the price impact metric.

    P_impact = sum(Sentiment_i * CapitalWeight_i)
    """
    return sum(
        agent.get("sentiment", 0.0) * agent.get("capital_weight", 0.0)
        for agent in agents_with_sentiment
    )


def calculate_stance_ratios(stances: list[str]) -> dict[str, float]:
    """Calculate BUY/SELL/HOLD ratios from agent stances."""
    if not stances:
        return {"buy_ratio": 0.0, "sell_ratio": 0.0, "hold_ratio": 0.0}

    total = len(stances)
    buy = sum(1 for s in stances if s == "BUY") / total
    sell = sum(1 for s in stances if s == "SELL") / total
    hold = sum(1 for s in stances if s == "HOLD") / total

    return {"buy_ratio": round(buy, 4), "sell_ratio": round(sell, 4), "hold_ratio": round(hold, 4)}


def aggregate_tick_metrics(
    tick: int,
    interactions: list[dict],
    agents: list[dict],
) -> dict:
    """Aggregate metrics for a single tick."""
    # Per-persona sentiment
    persona_sentiments: dict[str, list[float]] = {}
    stances: list[str] = []

    for interaction in interactions:
        if interaction.get("tick") != tick:
            continue

        persona = interaction.get("persona_type", "unknown")
        sentiment = interaction.get("sentiment_score", 0.0)

        if persona not in persona_sentiments:
            persona_sentiments[persona] = []
        persona_sentiments[persona].append(sentiment)

        stance = interaction.get("stance")
        if stance:
            stances.append(stance)

    # Calculate averages per persona
    by_persona = {}
    for persona, sentiments in persona_sentiments.items():
        by_persona[persona] = round(sum(sentiments) / len(sentiments), 4) if sentiments else 0.0

    # Overall average sentiment
    all_sentiments = [s for ss in persona_sentiments.values() for s in ss]
    avg_sentiment = round(sum(all_sentiments) / len(all_sentiments), 4) if all_sentiments else 0.0

    # Calculate P_impact for this tick
    agent_sentiments = []
    for agent in agents:
        agent_id = str(agent.get("id", ""))
        # Find most recent sentiment for this agent
        agent_interactions = [
            i for i in interactions
            if str(i.get("agent_id", "")) == agent_id and i.get("tick") == tick
        ]
        if agent_interactions:
            latest = agent_interactions[-1]
            agent_sentiments.append({
                "sentiment": latest.get("sentiment_score", 0.0),
                "capital_weight": agent.get("capital_weight", 0.0),
            })

    p_impact = calculate_p_impact(agent_sentiments)

    return {
        "tick": tick,
        "avg_sentiment": avg_sentiment,
        "by_persona": by_persona,
        "p_impact": round(p_impact, 6),
        "stance_ratios": calculate_stance_ratios(stances),
        "interaction_count": len([i for i in interactions if i.get("tick") == tick]),
    }
