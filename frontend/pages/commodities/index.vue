<template>
  <div class="commodities-page">
    <h1>Commodity Prices</h1>
    <p class="subtitle">Live Oil, Gold &amp; Silver prices from futures markets</p>

    <div v-if="loading" class="loading">Loading commodity prices...</div>

    <template v-else>
      <!-- Price Cards -->
      <div class="price-grid">
        <div v-for="p in prices" :key="p.commodity" class="card price-card" @click="selectCommodity(p.commodity)">
          <div class="price-header">
            <span class="commodity-icon">{{ icons[p.commodity] }}</span>
            <span class="commodity-name">{{ p.name }}</span>
          </div>
          <div class="price-value">${{ p.price.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</div>
          <div class="price-change" :class="p.change >= 0 ? 'up' : 'down'">
            {{ p.change >= 0 ? '+' : '' }}{{ p.change.toFixed(2) }}
            ({{ p.change_percent >= 0 ? '+' : '' }}{{ p.change_percent.toFixed(2) }}%)
          </div>
          <div class="price-details">
            <span>H: ${{ p.high.toFixed(2) }}</span>
            <span>L: ${{ p.low.toFixed(2) }}</span>
            <span>O: ${{ p.open.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Chart Section -->
      <div class="card chart-section">
        <div class="chart-header">
          <h2>{{ selectedName }} Price History</h2>
          <div class="period-tabs">
            <button
              v-for="p in periods"
              :key="p.value"
              :class="{ active: period === p.value }"
              @click="changePeriod(p.value)"
            >
              {{ p.label }}
            </button>
          </div>
        </div>
        <div v-if="chartLoading" class="loading">Loading chart...</div>
        <div v-else class="chart-container">
          <Line :data="chartData" :options="chartOptions" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Line } from "vue-chartjs";
import type { CommodityPrice, CommodityHistory } from "~/types/commodity";

const { getAllPrices, getHistory } = useCommodities();

const icons: Record<string, string> = {
  oil: "\u{1F6E2}\u{FE0F}",
  gold: "\u{1F947}",
  silver: "\u{1FA99}",
};

const periods = [
  { label: "1W", value: "5d" },
  { label: "1M", value: "1mo" },
  { label: "3M", value: "3mo" },
  { label: "6M", value: "6mo" },
  { label: "1Y", value: "1y" },
];

const prices = ref<CommodityPrice[]>([]);
const history = ref<CommodityHistory[]>([]);
const loading = ref(true);
const chartLoading = ref(false);
const selected = ref("gold");
const period = ref("1mo");

const selectedName = computed(() => {
  const p = prices.value.find((c) => c.commodity === selected.value);
  return p?.name ?? selected.value;
});

const chartData = computed(() => ({
  labels: history.value.map((h) => h.date),
  datasets: [
    {
      label: `${selectedName.value} (USD)`,
      data: history.value.map((h) => h.close),
      borderColor: selected.value === "gold" ? "#f59e0b" : selected.value === "silver" ? "#94a3b8" : "#3b82f6",
      backgroundColor: "transparent",
      tension: 0.3,
      pointRadius: 0,
      borderWidth: 2,
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: {
      grid: { color: "rgba(255,255,255,0.06)" },
      ticks: { color: "#888", maxTicksLimit: 12 },
    },
    y: {
      grid: { color: "rgba(255,255,255,0.06)" },
      ticks: { color: "#888" },
    },
  },
};

async function selectCommodity(commodity: string) {
  selected.value = commodity;
  await loadHistory();
}

async function changePeriod(p: string) {
  period.value = p;
  await loadHistory();
}

async function loadHistory() {
  chartLoading.value = true;
  try {
    history.value = await getHistory(selected.value, period.value);
  } catch (e) {
    console.error("Failed to load history:", e);
  } finally {
    chartLoading.value = false;
  }
}

onMounted(async () => {
  try {
    prices.value = await getAllPrices();
    await loadHistory();
  } catch (e) {
    console.error("Failed to load commodity prices:", e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.commodities-page h1 {
  font-size: 28px;
  margin-bottom: 4px;
}

.subtitle {
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.price-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.price-card {
  cursor: pointer;
  transition: border-color 0.2s;
}

.price-card:hover {
  border-color: var(--color-primary);
}

.price-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.commodity-icon {
  font-size: 24px;
}

.commodity-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.price-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.price-change {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.price-change.up {
  color: var(--color-buy);
}

.price-change.down {
  color: var(--color-sell);
}

.price-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.chart-section {
  margin-bottom: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h2 {
  font-size: 16px;
  color: var(--color-primary);
}

.period-tabs {
  display: flex;
  gap: 4px;
}

.period-tabs button {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 6px;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
}

.period-tabs button.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.chart-container {
  height: 400px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}
</style>
