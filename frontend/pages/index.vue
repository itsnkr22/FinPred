<template>
  <div class="dashboard">
    <h1>MiroFish FinPredict Dashboard</h1>
    <p class="subtitle">Multi-agent AI simulation engine for US market sentiment forecasting</p>

    <div class="stats-grid">
      <div class="card stat-card">
        <div class="stat-value">{{ scenarios.length }}</div>
        <div class="stat-label">Total Scenarios</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ completedCount }}</div>
        <div class="stat-label">Completed</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ runningCount }}</div>
        <div class="stat-label">Running</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">1,000</div>
        <div class="stat-label">Agent Swarm</div>
      </div>
    </div>

    <!-- Commodity Ticker -->
    <div class="section commodity-section">
      <div class="section-header">
        <h2>Commodity Prices</h2>
        <NuxtLink to="/commodities">
          <button class="btn-secondary-sm">View All</button>
        </NuxtLink>
      </div>
      <div v-if="commodities.length > 0" class="commodity-ticker">
        <div v-for="c in commodities" :key="c.commodity" class="card commodity-card">
          <div class="commodity-name">{{ c.name }}</div>
          <div class="commodity-price">${{ c.price.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</div>
          <div class="commodity-change" :class="c.change >= 0 ? 'up' : 'down'">
            {{ c.change >= 0 ? '+' : '' }}{{ c.change_percent.toFixed(2) }}%
          </div>
        </div>
      </div>
      <div v-else class="commodity-ticker">
        <div class="card commodity-card" v-for="i in 3" :key="i">
          <div class="commodity-name loading-text">Loading...</div>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>Recent Scenarios</h2>
        <NuxtLink to="/scenarios/new">
          <button class="btn-primary">+ New Simulation</button>
        </NuxtLink>
      </div>

      <div v-if="loading" class="loading">Loading scenarios...</div>

      <div v-else-if="scenarios.length === 0" class="empty-state card">
        <p>No scenarios yet. Create your first simulation to get started.</p>
        <NuxtLink to="/scenarios/new">
          <button class="btn-primary">Create Scenario</button>
        </NuxtLink>
      </div>

      <div v-else class="scenarios-list">
        <div v-for="scenario in scenarios.slice(0, 5)" :key="scenario.id" class="card scenario-item">
          <div class="scenario-info">
            <h3>{{ scenario.name }}</h3>
            <p class="scenario-event">{{ scenario.seed_event.substring(0, 120) }}...</p>
            <div class="scenario-meta">
              <span :class="'badge badge-' + scenario.status">{{ scenario.status }}</span>
              <span>{{ scenario.agent_count }} agents</span>
              <span>{{ scenario.duration_minutes }} min</span>
            </div>
          </div>
          <div class="scenario-actions">
            <NuxtLink v-if="scenario.status === 'draft'" :to="`/simulation/${scenario.id}`">
              <button class="btn-primary">Run</button>
            </NuxtLink>
            <NuxtLink v-else-if="scenario.status === 'completed'" :to="`/analytics/${scenario.id}`">
              <button class="btn-primary">View Results</button>
            </NuxtLink>
            <NuxtLink v-else :to="`/simulation/${scenario.id}`">
              <button class="btn-primary">View</button>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Scenario } from "~/types/scenario";
import type { CommodityPrice } from "~/types/commodity";

const { listScenarios } = useScenarios();
const { getAllPrices } = useCommodities();

const scenarios = ref<Scenario[]>([]);
const commodities = ref<CommodityPrice[]>([]);
const loading = ref(true);

const completedCount = computed(() => scenarios.value.filter(s => s.status === "completed").length);
const runningCount = computed(() => scenarios.value.filter(s => s.status === "running").length);

onMounted(async () => {
  try {
    const [scenarioResult, commodityResult] = await Promise.allSettled([
      listScenarios(),
      getAllPrices(),
    ]);
    if (scenarioResult.status === "fulfilled") scenarios.value = scenarioResult.value.items;
    if (commodityResult.status === "fulfilled") commodities.value = commodityResult.value;
  } catch (e) {
    console.error("Failed to load dashboard:", e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.dashboard h1 {
  font-size: 28px;
  margin-bottom: 4px;
}

.subtitle {
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}

.stat-card {
  text-align: center;
  padding: 24px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.scenarios-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.scenario-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scenario-info h3 {
  font-size: 16px;
  margin-bottom: 4px;
}

.scenario-event {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.scenario-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}

.commodity-section {
  margin-bottom: 32px;
}

.commodity-ticker {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.commodity-card {
  padding: 16px 20px;
}

.commodity-name {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.commodity-price {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 2px;
}

.commodity-change {
  font-size: 13px;
  font-weight: 600;
}

.commodity-change.up {
  color: var(--color-buy);
}

.commodity-change.down {
  color: var(--color-sell);
}

.btn-secondary-sm {
  padding: 6px 12px;
  font-size: 12px;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
}

.loading-text {
  color: var(--color-text-secondary);
}
</style>
