import { ref, onUnmounted } from "vue";
import type {
  SimulationStatus,
  TickUpdate,
  TickInteraction,
  TickMetrics,
} from "~/types/simulation";

export function useSimulation(scenarioId: string) {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;

  const status = ref<SimulationStatus | null>(null);
  const interactions = ref<TickInteraction[]>([]);
  const tickMetrics = ref<TickMetrics[]>([]);
  const isRunning = ref(false);
  const error = ref<string | null>(null);

  let ws: WebSocket | null = null;

  async function startSimulation(maxTicks = 60, tickDurationMs = 2000) {
    try {
      const result = await $fetch<SimulationStatus>(
        `${apiBase}/api/v1/simulations/${scenarioId}/run`,
        {
          method: "POST",
          body: { tick_duration_ms: tickDurationMs, max_ticks: maxTicks },
        }
      );
      status.value = result;
      isRunning.value = true;
      connectWebSocket();
      return result;
    } catch (e: any) {
      error.value = e.message || "Failed to start simulation";
      throw e;
    }
  }

  async function stopSimulation() {
    try {
      await $fetch(`${apiBase}/api/v1/simulations/${scenarioId}/stop`, {
        method: "POST",
      });
      isRunning.value = false;
      disconnectWebSocket();
    } catch (e: any) {
      error.value = e.message || "Failed to stop simulation";
    }
  }

  async function fetchStatus() {
    try {
      status.value = await $fetch<SimulationStatus>(
        `${apiBase}/api/v1/simulations/${scenarioId}/status`
      );
    } catch (e: any) {
      error.value = e.message;
    }
  }

  function connectWebSocket() {
    const wsUrl = apiBase
      .replace("http://", "ws://")
      .replace("https://", "wss://");

    ws = new WebSocket(`${wsUrl}/api/v1/simulations/${scenarioId}/ws`);

    ws.onmessage = (event) => {
      const data: TickUpdate = JSON.parse(event.data);

      if (data.type === "tick_update") {
        interactions.value.push(...data.interactions);
        tickMetrics.value.push(data.metrics);

        // Keep only last 200 interactions for performance
        if (interactions.value.length > 200) {
          interactions.value = interactions.value.slice(-200);
        }
      }

      if ((data as any).type === "simulation_complete") {
        isRunning.value = false;
        disconnectWebSocket();
      }
    };

    ws.onerror = () => {
      error.value = "WebSocket connection error";
    };

    ws.onclose = () => {
      isRunning.value = false;
    };
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  onUnmounted(() => {
    disconnectWebSocket();
  });

  return {
    status,
    interactions,
    tickMetrics,
    isRunning,
    error,
    startSimulation,
    stopSimulation,
    fetchStatus,
    connectWebSocket,
  };
}
