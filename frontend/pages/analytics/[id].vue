<template>
  <div class="analytics-page">
    <div class="page-header">
      <h1>Simulation Analytics</h1>
      <div class="header-actions">
        <button class="btn-primary" @click="handleGenerateReport" :disabled="generatingReport">
          {{ generatingReport ? 'Generating...' : 'Generate B2B Report' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading analytics...</div>

    <template v-else-if="result">
      <!-- Summary Cards -->
      <div class="summary-grid">
        <div class="card summary-card">
          <div class="summary-label">Price Impact</div>
          <div class="summary-value" :class="result.p_impact >= 0 ? 'bullish' : 'bearish'">
            {{ result.p_impact >= 0 ? '+' : '' }}{{ result.p_impact.toFixed(4) }}
          </div>
        </div>
        <div class="card summary-card">
          <div class="summary-label">BUY</div>
          <div class="summary-value buy">{{ (result.buy_ratio * 100).toFixed(1) }}%</div>
        </div>
        <div class="card summary-card">
          <div class="summary-label">SELL</div>
          <div class="summary-value sell">{{ (result.sell_ratio * 100).toFixed(1) }}%</div>
        </div>
        <div class="card summary-card">
          <div class="summary-label">HOLD</div>
          <div class="summary-value hold">{{ (result.hold_ratio * 100).toFixed(1) }}%</div>
        </div>
      </div>

      <!-- Narrative Summary -->
      <div class="card narrative-card">
        <h2>Simulation Summary</h2>
        <p>{{ result.narrative_summary }}</p>
      </div>

      <!-- Emergent Narratives -->
      <div v-if="result.emergent_narratives.length > 0" class="card">
        <h2>Emergent Narratives</h2>
        <div class="narratives-list">
          <div v-for="(narrative, i) in result.emergent_narratives" :key="i" class="narrative-item">
            <span :class="'badge badge-' + (narrative.severity === 'high' ? 'sell' : 'hold')">
              {{ narrative.severity }}
            </span>
            <div>
              <div class="narrative-type">{{ narrative.type?.replace(/_/g, ' ') }}</div>
              <p>{{ narrative.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Influencers -->
      <div v-if="result.top_influencers.length > 0" class="card">
        <h2>Top Influencers</h2>
        <div class="influencers-list">
          <div v-for="(inf, i) in result.top_influencers" :key="i" class="influencer-item">
            <span class="influencer-rank">#{{ i + 1 }}</span>
            <span class="influencer-name">{{ inf.name }}</span>
            <span class="influencer-persona">{{ inf.persona }}</span>
            <span class="influencer-count">{{ inf.count }} interactions</span>
          </div>
        </div>
      </div>

      <!-- Report Modal -->
      <div v-if="report" class="card report-card">
        <div class="report-header">
          <h2>B2B Risk Report</h2>
          <button class="btn-secondary" @click="report = null">Close</button>
        </div>
        <pre class="report-content">{{ report }}</pre>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SimulationResult } from "~/types/simulation";

const route = useRoute();
const scenarioId = route.params.id as string;
const { getResults, generateReport } = useAnalytics();

const result = ref<SimulationResult | null>(null);
const loading = ref(true);
const report = ref<string | null>(null);
const generatingReport = ref(false);

onMounted(async () => {
  try {
    result.value = await getResults(scenarioId);
  } catch (e) {
    console.error("Failed to load analytics:", e);
  } finally {
    loading.value = false;
  }
});

async function handleGenerateReport() {
  generatingReport.value = true;
  try {
    report.value = await generateReport(scenarioId);
  } catch (e) {
    console.error("Failed to generate report:", e);
  } finally {
    generatingReport.value = false;
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
  padding: 24px;
}

.summary-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.summary-value {
  font-size: 32px;
  font-weight: 700;
}

.summary-value.bullish { color: var(--color-buy); }
.summary-value.bearish { color: var(--color-sell); }
.summary-value.buy { color: var(--color-buy); }
.summary-value.sell { color: var(--color-sell); }
.summary-value.hold { color: var(--color-hold); }

.narrative-card {
  margin-bottom: 20px;
}

.narrative-card h2, .card h2 {
  font-size: 16px;
  color: var(--color-primary);
  margin-bottom: 12px;
}

.narrative-card p {
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.card { margin-bottom: 20px; }

.narratives-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.narrative-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.narrative-type {
  font-weight: 600;
  text-transform: capitalize;
  margin-bottom: 4px;
}

.narrative-item p {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.influencers-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.influencer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.influencer-rank {
  font-weight: 700;
  color: var(--color-primary);
  width: 24px;
}

.influencer-name { font-weight: 500; flex: 1; }
.influencer-persona { color: var(--color-text-secondary); text-transform: capitalize; }
.influencer-count { color: var(--color-text-secondary); }

.report-card {
  position: fixed;
  top: 5%;
  left: 260px;
  right: 20px;
  bottom: 5%;
  z-index: 100;
  overflow-y: auto;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.report-content {
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}

.btn-secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
</style>
