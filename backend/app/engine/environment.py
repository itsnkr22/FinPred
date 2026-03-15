"""Simulated dual-feed environment (X/Twitter + Reddit) for agent interactions."""

import random
from uuid import UUID


class SimulatedEnvironment:
    """Maintains two concurrent feeds and serves personalized content to agents."""

    def __init__(self, seed_event: str, environment_vars: dict):
        self.seed_event = seed_event
        self.environment_vars = environment_vars
        self.twitter_feed: list[dict] = []
        self.reddit_feed: list[dict] = []
        self._initialize_feeds()

    def _initialize_feeds(self):
        """Seed the feeds with the initial event."""
        self.twitter_feed.append({
            "id": "seed_tweet",
            "agent_id": None,
            "content": f"BREAKING: {self.seed_event}",
            "platform": "twitter",
            "type": "post",
            "sentiment": 0.0,
            "tick": 0,
            "engagement": 100,
        })
        self.reddit_feed.append({
            "id": "seed_reddit",
            "agent_id": None,
            "content": f"[Breaking News] {self.seed_event}\n\nWhat are your thoughts? How does this affect your positions?",
            "platform": "reddit",
            "type": "post",
            "sentiment": 0.0,
            "tick": 0,
            "engagement": 50,
        })

    def add_interaction(self, interaction: dict):
        """Add a new interaction to the appropriate feed."""
        entry = {
            "id": str(interaction.get("id", "")),
            "agent_id": str(interaction.get("agent_id", "")),
            "content": interaction.get("content", ""),
            "platform": interaction.get("platform", "twitter"),
            "type": interaction.get("interaction_type", "post"),
            "sentiment": interaction.get("sentiment_score", 0.0),
            "tick": interaction.get("tick", 0),
            "engagement": 0,
            "persona_type": interaction.get("persona_type", ""),
            "display_name": interaction.get("display_name", ""),
        }

        if entry["platform"] == "twitter":
            self.twitter_feed.append(entry)
        else:
            self.reddit_feed.append(entry)

        # Update engagement for existing posts (likes, comments increase engagement)
        if interaction.get("interaction_type") in ("comment", "like", "repost"):
            self._boost_engagement(interaction.get("parent_id"))

    def get_feed_for_agent(
        self,
        agent_id: UUID,
        persona_type: str,
        current_tick: int,
        max_items: int = 10,
    ) -> str:
        """Get a personalized feed view for an agent.

        Returns a formatted string of recent activity the agent can see.
        """
        # Combine feeds, weighted by persona preferences
        all_items = []

        if persona_type in ("retail_reddit", "finfluencer"):
            # These personas see both feeds
            all_items.extend(self.twitter_feed[-20:])
            all_items.extend(self.reddit_feed[-20:])
        elif persona_type == "hft_algo":
            # HFT only sees Twitter (news-like)
            all_items.extend(self.twitter_feed[-15:])
        else:
            # Institutional and macro see Twitter primarily
            all_items.extend(self.twitter_feed[-15:])
            all_items.extend(self.reddit_feed[-5:])

        # Sort by engagement (trending algorithm)
        all_items.sort(key=lambda x: x.get("engagement", 0), reverse=True)

        # Take top items
        top_items = all_items[:max_items]

        # Format as readable feed
        lines = [f"=== Market Feed (Tick {current_tick}) ==="]
        lines.append(f"Environment: Volatility={self.environment_vars.get('market_volatility', 'normal')}, "
                     f"Sector={self.environment_vars.get('sector_focus', 'general')}")
        lines.append("")

        for item in top_items:
            platform_tag = "[X]" if item["platform"] == "twitter" else "[Reddit]"
            name = item.get("display_name", "System")
            lines.append(f"{platform_tag} @{name}: {item['content']}")
            lines.append(f"  Engagement: {item.get('engagement', 0)} | Sentiment: {item.get('sentiment', 0):.2f}")
            lines.append("")

        return "\n".join(lines)

    def _boost_engagement(self, parent_id):
        """Increase engagement score for a parent post."""
        if not parent_id:
            return
        parent_str = str(parent_id)
        for feed in (self.twitter_feed, self.reddit_feed):
            for item in feed:
                if item["id"] == parent_str:
                    item["engagement"] = item.get("engagement", 0) + 1
                    return

    def get_trending_topics(self) -> list[str]:
        """Extract trending topics from recent high-engagement posts."""
        all_items = self.twitter_feed[-50:] + self.reddit_feed[-50:]
        all_items.sort(key=lambda x: x.get("engagement", 0), reverse=True)
        topics = []
        for item in all_items[:5]:
            content = item.get("content", "")[:100]
            if content:
                topics.append(content)
        return topics
