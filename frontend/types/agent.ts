export interface Agent {
  id: string;
  scenario_id: string;
  persona_type: string;
  display_name: string;
  capital_weight: number;
  risk_tolerance: number;
  influence_score: number;
  config: Record<string, unknown>;
  created_at: string;
}

export interface AgentListResponse {
  items: Agent[];
  total: number;
}
