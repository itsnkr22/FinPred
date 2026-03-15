import type {
  Scenario,
  ScenarioCreate,
  ScenarioListResponse,
} from "~/types/scenario";

export function useScenarios() {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;

  async function listScenarios(
    skip = 0,
    limit = 20
  ): Promise<ScenarioListResponse> {
    const data = await $fetch<ScenarioListResponse>(
      `${apiBase}/api/v1/scenarios?skip=${skip}&limit=${limit}`
    );
    return data;
  }

  async function getScenario(id: string): Promise<Scenario> {
    return await $fetch<Scenario>(`${apiBase}/api/v1/scenarios/${id}`);
  }

  async function createScenario(data: ScenarioCreate): Promise<Scenario> {
    return await $fetch<Scenario>(`${apiBase}/api/v1/scenarios`, {
      method: "POST",
      body: data,
    });
  }

  async function deleteScenario(id: string): Promise<void> {
    await $fetch(`${apiBase}/api/v1/scenarios/${id}`, { method: "DELETE" });
  }

  return { listScenarios, getScenario, createScenario, deleteScenario };
}
