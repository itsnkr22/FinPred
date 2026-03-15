<template>
  <div class="simulation-page">
    <div class="page-header">
      <div>
        <h1>Simulation</h1>
        <span v-if="isRunning" class="badge badge-running">Live</span>
        <span v-else class="badge badge-draft">Ready</span>
      </div>
      <div class="controls">
        <button v-if="!isRunning" class="btn-primary" @click="handleStart">
          Start Simulation
        </button>
        <button v-else class="btn-danger" @click="handleStop">
          Stop
        </button>
        <NuxtLink v-if="!isRunning && tickMetrics.length > 0" :to="`/analytics/${scenarioId}`">
          <button class="btn-primary">View Analytics</button>
        </NuxtLink>
      </div>
    </div>

    <!-- Status Bar -->
    <div v-if="status" class="card status-bar">
      <div class="status-item">
        <span class="status-label">Tick</span>
        <span class="status-value">{{ status.current_tick }} / {{ status.max_ticks }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">Active Agents</span>
        <span class="status-value">{{ status.agents_active }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">Interactions</span>
        <span class="status-value">{{ status.interactions_count }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
      </div>
    </div>

    <!-- Live Feed -->
    <div class="simulation-grid">
      <div class="card feed-panel">
        <h3>Live Social Feed</h3>
        <div class="feed-list" ref="feedRef">
          <div
            v-for="interaction in [...interactions].reverse().slice(0, 50)"
            :key="interaction.id"
            class="feed-item"
          >
            <div class="feed-header">
              <span class="feed-platform" :class="'platform-' + interaction.platform">
                {{ interaction.platform === 'twitter' ? '[X]' : '[Reddit]' }}
              </span>
              <span class="feed-name">@{{ interaction.agent_name }}</span>
              <span :class="'badge badge-' + interaction.stance.toLowerCase()">
                {{ interaction.stance }}
              </span>
            </div>
            <p class="feed-content">{{ interaction.content }}</p>
            <div class="feed-meta">
              <span>Sentiment: {{ interaction.sentiment.toFixed(2) }}</span>
              <span class="feed-persona">{{ interaction.persona_type }}</span>
            </div>
          </div>
          <div v-if="interactions.length === 0" class="empty-feed">
            Waiting for simulation to start...
          </div>
        </div>
      </div>

      <div class="metrics-panel">
        <div class="card">
          <h3>Sentiment Trend</h3>
          <div class="mini-chart" v-if="tickMetrics.length > 0">
            <div
              v-for="(m, i) in tickMetrics.slice(-20)"
              :key="i"
              class="chart-bar"
              :style="{
                height: Math.abs(m.avg_sentiment * 50) + 'px',
                backgroundColor: m.avg_sentiment >= 0 ? 'var(--color-buy)' : 'var(--color-sell)',
                marginTop: m.avg_sentiment >= 0 ? (50 - m.avg_sentiment * 50) + 'px' : '50px'
              }"
            ></div>
          </div>
          <div v-else class="empty-chart">No data yet</div>
        </div>

        <div class="card">
          <h3>Current Stance</h3>
          <div v-if="latestMetrics" class="stance-bars">
            <div class="stance-row">
              <span class="stance-label">BUY</span>
              <div class="stance-bar">
                <div class="stance-fill buy" :style="{ width: (latestMetrics.stance_ratios.buy_ratio * 100) + '%' }"></div>
              </div>
              <span>{{ (latestMetrics.stance_ratios.buy_ratio * 100).toFixed(0) }}%</span>
            </div>
            <div class="stance-row">
              <span class="stance-label">SELL</span>
              <div class="stance-bar">
                <div class="stance-fill sell" :style="{ width: (latestMetrics.stance_ratios.sell_ratio * 100) + '%' }"></div>
              </div>
              <span>{{ (latestMetrics.stance_ratios.sell_ratio * 100).toFixed(0) }}%</span>
            </div>
            <div class="stance-row">
              <span class="stance-label">HOLD</span>
              <div class="stance-bar">
                <div class="stance-fill hold" :style="{ width: (latestMetrics.stance_ratios.hold_ratio * 100) + '%' }"></div>
              </div>
              <span>{{ (latestMetrics.stance_ratios.hold_ratio * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>

        <div class="card">
          <h3>P_impact</h3>
          <div v-if="latestMetrics" class="p-impact-value" :class="latestMetrics.p_impact >= 0 ? 'bullish' : 'bearish'">
            {{ latestMetrics.p_impact >= 0 ? '+' : '' }}{{ latestMetrics.p_impact.toFixed(4) }}
          </div>
          <div v-else class="empty-chart">--</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const scenarioId = route.params.id as string;

const {
  status,
  interactions,
  tickMetrics,
  isRunning,
  error,
  startSimulation,
  stopSimulation,
  fetchStatus,
} = useSimulation(scenarioId);

const latestMetrics = computed(() =>
  tickMetrics.value.length > 0 ? tickMetrics.value[tickMetrics.value.length - 1] : null
);

const progressPct = computed(() => {
  if (!status.value || status.value.max_ticks === 0) return 0;
  return (status.value.current_tick / status.value.max_ticks) * 100;
});

async function handleStart() {
  try {
    await startSimulation(60, 2000);
  } catch (e) {
    console.error("Failed to start:", e);
  }
}

async function handleStop() {
  await stopSimulation();
}

onMounted(() => {
  fetchStatus();
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  display: inline;
  margin-right: 12px;
}

.controls {
  display: flex;
  gap: 8px;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.status-value {
  font-size: 18px;
  font-weight: 600;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-bg);
  border-radius: 3px;
  min-width: 200px;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.3s;
}

.simulation-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 16px;
}

.feed-panel {
  max-height: 70vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.feed-panel h3 {
  margin-bottom: 12px;
  color: var(--color-primary);
  font-size: 14px;
}

.feed-list {
  overflow-y: auto;
  flex: 1;
}

.feed-item {
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}

.feed-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.feed-platform {
  font-size: 11px;
  font-weight: 600;
}

.platform-twitter { color: #1da1f2; }
.platform-reddit { color: #ff4500; }

.feed-name {
  font-weight: 500;
  font-size: 13px;
}

.feed-content {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  line-height: 1.4;
}

.feed-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--color-text-secondary);
}

.feed-persona {
  text-transform: capitalize;
}

.empty-feed, .empty-chart {
  text-align: center;
  padding: 20px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.metrics-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metrics-panel h3 {
  font-size: 13px;
  color: var(--color-primary);
  margin-bottom: 8px;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 100px;
}

.chart-bar {
  flex: 1;
  min-width: 4px;
  border-radius: 2px;
  transition: height 0.3s;
}

.stance-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stance-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.stance-label {
  width: 36px;
  font-weight: 600;
}

.stance-bar {
  flex: 1;
  height: 16px;
  background: var(--color-bg);
  border-radius: 4px;
  overflow: hidden;
}

.stance-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.stance-fill.buy { background: var(--color-buy); }
.stance-fill.sell { background: var(--color-sell); }
.stance-fill.hold { background: var(--color-hold); }

.p-impact-value {
  font-size: 32px;
  font-weight: 700;
  text-align: center;
  padding: 12px;
}

.p-impact-value.bullish { color: var(--color-buy); }
.p-impact-value.bearish { color: var(--color-sell); }
</style>
