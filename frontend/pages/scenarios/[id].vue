<template>
  <div class="scenario-detail" v-if="scenario">
    <div class="page-header">
      <div>
        <h1>{{ scenario.name }}</h1>
        <span :class="'badge badge-' + scenario.status">{{ scenario.status }}</span>
      </div>
      <div class="header-actions">
        <NuxtLink v-if="scenario.status === 'draft'" :to="`/simulation/${scenario.id}`">
          <button class="btn-primary">Run Simulation</button>
        </NuxtLink>
        <NuxtLink v-if="scenario.status === 'completed'" :to="`/analytics/${scenario.id}`">
          <button class="btn-primary">View Analytics</button>
        </NuxtLink>
      </div>
    </div>

    <div class="detail-grid">
      <div class="card">
        <h3>Seed Event</h3>
        <p class="event-text">{{ scenario.seed_event }}</p>
      </div>

      <div class="card">
        <h3>Environment</h3>
        <div class="env-list">
          <div class="env-item">
            <span class="env-label">Volatility</span>
            <span class="env-value">{{ scenario.environment_vars.market_volatility }}</span>
          </div>
          <div class="env-item">
            <span class="env-label">Sector</span>
            <span class="env-value">{{ scenario.environment_vars.sector_focus }}</span>
          </div>
          <div class="env-item">
            <span class="env-label">Fed Stance</span>
            <span class="env-value">{{ scenario.environment_vars.fed_stance }}</span>
          </div>
          <div class="env-item">
            <span class="env-label">Election Year</span>
            <span class="env-value">{{ scenario.environment_vars.election_year ? 'Yes' : 'No' }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Parameters</h3>
        <div class="env-list">
          <div class="env-item">
            <span class="env-label">Agents</span>
            <span class="env-value">{{ scenario.agent_count }}</span>
          </div>
          <div class="env-item">
            <span class="env-label">Duration</span>
            <span class="env-value">{{ scenario.duration_minutes }} min</span>
          </div>
          <div class="env-item">
            <span class="env-label">Created</span>
            <span class="env-value">{{ new Date(scenario.created_at).toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Scenario } from "~/types/scenario";

const route = useRoute();
const { getScenario } = useScenarios();

const scenario = ref<Scenario | null>(null);

onMounted(async () => {
  try {
    scenario.value = await getScenario(route.params.id as string);
  } catch (e) {
    console.error("Failed to load scenario:", e);
  }
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-header h1 {
  margin-bottom: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-grid > :first-child {
  grid-column: 1 / -1;
}

.event-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-text-secondary);
}

h3 {
  font-size: 14px;
  color: var(--color-primary);
  margin-bottom: 12px;
}

.env-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.env-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.env-label {
  color: var(--color-text-secondary);
}

.env-value {
  font-weight: 500;
  text-transform: capitalize;
}
</style>
