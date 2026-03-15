"""Entity relationship mapping for market entities (GraphRAG stub)."""

import logging

logger = logging.getLogger(__name__)


class EntityGraph:
    """Maps relationships between US market entities.

    Example: "Nvidia" -> "AI Data Centers" -> "Retail Sentiment"

    TODO: Implement with a proper graph database or knowledge graph.
    """

    def __init__(self):
        self.entities: dict[str, dict] = {}
        self.edges: list[tuple[str, str, str]] = []
        self._load_defaults()

    def _load_defaults(self):
        """Load default entity relationships for US markets."""
        relationships = [
            ("NVIDIA", "AI_Infrastructure", "primary_provider"),
            ("AI_Infrastructure", "Data_Centers", "requires"),
            ("Data_Centers", "Energy_Demand", "increases"),
            ("Federal_Reserve", "Interest_Rates", "sets"),
            ("Interest_Rates", "Bond_Yields", "affects"),
            ("Interest_Rates", "Housing_Market", "affects"),
            ("Interest_Rates", "Tech_Valuations", "inversely_affects"),
            ("SEC", "Crypto_Regulation", "oversees"),
            ("Crypto_Regulation", "Bitcoin", "impacts"),
            ("Crypto_Regulation", "Ethereum", "impacts"),
            ("CPI_Data", "Fed_Policy", "influences"),
            ("Employment_Data", "Fed_Policy", "influences"),
            ("Retail_Sentiment", "Meme_Stocks", "drives"),
            ("WSB_Reddit", "Retail_Sentiment", "amplifies"),
            ("Finfluencers", "Retail_Sentiment", "shapes"),
        ]

        for source, target, relation in relationships:
            self.add_edge(source, target, relation)

    def add_edge(self, source: str, target: str, relation: str):
        """Add a relationship between two entities."""
        self.edges.append((source, target, relation))
        if source not in self.entities:
            self.entities[source] = {"connections": []}
        if target not in self.entities:
            self.entities[target] = {"connections": []}
        self.entities[source]["connections"].append({"target": target, "relation": relation})

    def get_related_entities(self, entity: str, depth: int = 2) -> list[str]:
        """Get entities related to the given entity up to N hops."""
        visited = set()
        queue = [(entity, 0)]
        related = []

        while queue:
            current, current_depth = queue.pop(0)
            if current in visited or current_depth > depth:
                continue
            visited.add(current)
            if current != entity:
                related.append(current)

            if current in self.entities:
                for conn in self.entities[current]["connections"]:
                    queue.append((conn["target"], current_depth + 1))

        return related

    def get_context_for_event(self, event_text: str) -> str:
        """Extract entity context relevant to a market event."""
        mentioned = []
        event_lower = event_text.lower()

        for entity in self.entities:
            if entity.lower().replace("_", " ") in event_lower:
                related = self.get_related_entities(entity)
                mentioned.append(f"{entity} -> {', '.join(related)}")

        return "; ".join(mentioned) if mentioned else ""


# Singleton
entity_graph = EntityGraph()
