export interface SimulationStatus {
  scenario_id: string;
  status: string;
  current_tick: number;
  max_ticks: number;
  agents_active: number;
  interactions_count: number;
}

export interface SimulationResult {
  id: string;
  scenario_id: string;
  p_impact: number;
  buy_ratio: number;
  sell_ratio: number;
  hold_ratio: number;
  sentiment_timeline: TickMetrics[];
  narrative_summary: string | null;
  emergent_narratives: EmergentNarrative[];
  top_influencers: TopInfluencer[];
  raw_metrics: Record<string, unknown>;
  created_at: string;
}

export interface TickMetrics {
  tick: number;
  avg_sentiment: number;
  by_persona: Record<string, number>;
  p_impact: number;
  stance_ratios: {
    buy_ratio: number;
    sell_ratio: number;
    hold_ratio: number;
  };
  interaction_count: number;
}

export interface TickUpdate {
  type: "tick_update";
  tick: number;
  interactions: TickInteraction[];
  metrics: TickMetrics;
}

export interface TickInteraction {
  id: string;
  agent_name: string;
  persona_type: string;
  platform: string;
  content: string;
  sentiment: number;
  stance: "BUY" | "SELL" | "HOLD";
}

export interface EmergentNarrative {
  type: string;
  description: string;
  severity: string;
}

export interface TopInfluencer {
  name: string;
  persona: string;
  count: number;
}
