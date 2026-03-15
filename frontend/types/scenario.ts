export interface EnvironmentVars {
  market_volatility: "low" | "normal" | "high" | "extreme";
  sector_focus: "tech" | "finance" | "energy" | "crypto" | "general";
  election_year: boolean;
  fed_stance: "hawkish" | "neutral" | "dovish";
}

export interface Scenario {
  id: string;
  name: string;
  description: string | null;
  seed_event: string;
  environment_vars: EnvironmentVars;
  duration_minutes: number;
  agent_count: number;
  status: "draft" | "running" | "completed" | "failed" | "stopped";
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface ScenarioCreate {
  name: string;
  description?: string;
  seed_event: string;
  environment_vars: EnvironmentVars;
  duration_minutes: number;
  agent_count: number;
}

export interface ScenarioListResponse {
  items: Scenario[];
  total: number;
}
