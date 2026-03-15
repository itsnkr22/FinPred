import type { SimulationResult } from "~/types/simulation";

export function useAnalytics() {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;

  async function getResults(scenarioId: string): Promise<SimulationResult> {
    return await $fetch<SimulationResult>(
      `${apiBase}/api/v1/analytics/${scenarioId}`
    );
  }

  async function getHeatmap(scenarioId: string) {
    return await $fetch(`${apiBase}/api/v1/analytics/${scenarioId}/heatmap`);
  }

  async function getPriceImpact(scenarioId: string) {
    return await $fetch(
      `${apiBase}/api/v1/analytics/${scenarioId}/price-impact`
    );
  }

  async function getNarratives(scenarioId: string) {
    return await $fetch(
      `${apiBase}/api/v1/analytics/${scenarioId}/narratives`
    );
  }

  async function generateReport(scenarioId: string): Promise<string> {
    const result = await $fetch<{ report: string }>(
      `${apiBase}/api/v1/analytics/${scenarioId}/report`,
      { method: "POST" }
    );
    return result.report;
  }

  return { getResults, getHeatmap, getPriceImpact, getNarratives, generateReport };
}
