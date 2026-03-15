"""Anthropic Claude-powered B2B report generation."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.interaction import Interaction
from app.models.simulation_result import SimulationResult

logger = logging.getLogger(__name__)


async def generate_b2b_report(scenario_id: UUID, db: AsyncSession) -> str:
    """Generate a premium client-ready risk report using Claude."""
    # Fetch simulation results
    result = await db.execute(
        select(SimulationResult).where(SimulationResult.scenario_id == scenario_id)
    )
    sim_result = result.scalar_one_or_none()
    if not sim_result:
        return "No simulation results available for report generation."

    # Fetch top interactions for context
    interactions_result = await db.execute(
        select(Interaction)
        .where(Interaction.scenario_id == scenario_id)
        .order_by(Interaction.tick)
        .limit(50)
    )
    interactions = interactions_result.scalars().all()

    interaction_summary = "\n".join([
        f"[Tick {i.tick}] {(i.metadata_ or {}).get('persona_type', 'unknown')}: {i.content[:200] if i.content else 'N/A'} (sentiment: {i.sentiment_score})"
        for i in interactions[:30]
    ])

    prompt = f"""You are a senior financial analyst at a premium Wall Street research firm.
Generate a comprehensive risk analysis report based on the following simulation data.

SIMULATION RESULTS:
- Price Impact (P_impact): {sim_result.p_impact:.4f}
- BUY ratio: {sim_result.buy_ratio:.1%}
- SELL ratio: {sim_result.sell_ratio:.1%}
- HOLD ratio: {sim_result.hold_ratio:.1%}
- Total interactions analyzed: {sim_result.raw_metrics.get('total_interactions', 0)}

NARRATIVE SUMMARY:
{sim_result.narrative_summary}

EMERGENT NARRATIVES:
{sim_result.emergent_narratives}

TOP AGENT INTERACTIONS:
{interaction_summary}

Generate a professional report with these sections:
1. Executive Summary
2. Market Sentiment Analysis
3. Cohort Behavior Breakdown (Retail, Institutional, HFT, Macro, Finfluencer)
4. Risk Assessment & Contagion Analysis
5. Actionable Recommendations
6. Confidence Level & Caveats

Format as a clean, professional document suitable for C-suite presentation."""

    if not settings.anthropic_api_key:
        return _generate_stub_report(sim_result)

    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        message = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Claude report generation failed: {e}")
        return _generate_stub_report(sim_result)


def _generate_stub_report(sim_result: SimulationResult) -> str:
    """Generate a stub report when Claude is unavailable."""
    direction = "BULLISH" if sim_result.p_impact > 0 else "BEARISH"
    dominant = "BUY" if sim_result.buy_ratio > sim_result.sell_ratio else "SELL"

    return f"""
MIROFISH FINPREDICT — SIMULATION RISK REPORT
=============================================

EXECUTIVE SUMMARY
The simulation indicates a {direction} market outlook with a price impact
metric of {sim_result.p_impact:.4f}. The dominant market stance across
all agent cohorts was {dominant}.

SENTIMENT BREAKDOWN
- Buy: {sim_result.buy_ratio:.1%}
- Sell: {sim_result.sell_ratio:.1%}
- Hold: {sim_result.hold_ratio:.1%}

{sim_result.narrative_summary or 'No narrative available.'}

NOTE: This is a stub report. Configure ANTHROPIC_API_KEY for full
AI-generated analysis.
"""
