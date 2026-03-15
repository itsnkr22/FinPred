<template>
  <div class="scenarios-page">
    <div class="page-header">
      <h1>Scenarios</h1>
      <NuxtLink to="/scenarios/new">
        <button class="btn-primary">+ New Scenario</button>
      </NuxtLink>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="scenarios-grid">
      <div v-for="scenario in scenarios" :key="scenario.id" class="card scenario-card">
        <div class="card-header">
          <h3>{{ scenario.name }}</h3>
          <span :class="'badge badge-' + scenario.status">{{ scenario.status }}</span>
        </div>
        <p class="seed-event">{{ scenario.seed_event.substring(0, 150) }}...</p>
        <div class="card-meta">
          <span>{{ scenario.agent_count }} agents</span>
          <span>{{ scenario.duration_minutes }} min</span>
          <span>{{ new Date(scenario.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="card-actions">
          <NuxtLink :to="`/scenarios/${scenario.id}`">
            <button class="btn-primary">Details</button>
          </NuxtLink>
          <NuxtLink v-if="scenario.status === 'draft'" :to="`/simulation/${scenario.id}`">
            <button class="btn-primary">Run</button>
          </NuxtLink>
          <NuxtLink v-if="scenario.status === 'completed'" :to="`/analytics/${scenario.id}`">
            <button class="btn-primary">Analytics</button>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Scenario } from "~/types/scenario";

const { listScenarios } = useScenarios();
const scenarios = ref<Scenario[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const result = await listScenarios(0, 50);
    scenarios.value = result.items;
  } catch (e) {
    console.error("Failed to load scenarios:", e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.scenario-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.seed-event {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.card-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}
</style>
