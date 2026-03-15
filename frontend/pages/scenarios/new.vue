<template>
  <div class="new-scenario">
    <h1>Create New Simulation</h1>
    <p class="subtitle">Configure a market event scenario and agent simulation parameters</p>

    <form @submit.prevent="handleSubmit" class="scenario-form">
      <div class="card form-section">
        <h2>Event Injector</h2>
        <div class="form-group">
          <label>Scenario Name</label>
          <input v-model="form.name" type="text" placeholder="e.g., Fed Rate Cut Surprise" required />
        </div>
        <div class="form-group">
          <label>Description (optional)</label>
          <input v-model="form.description" type="text" placeholder="Brief description of the scenario" />
        </div>
        <div class="form-group">
          <label>Seed Event</label>
          <textarea
            v-model="form.seed_event"
            rows="4"
            placeholder="Paste breaking news, SEC filing, or Fed speech transcript..."
            required
          ></textarea>
        </div>
      </div>

      <div class="card form-section">
        <h2>Environment Variables</h2>
        <div class="env-grid">
          <div class="form-group">
            <label>Market Volatility</label>
            <select v-model="form.environment_vars.market_volatility">
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="extreme">Extreme</option>
            </select>
          </div>
          <div class="form-group">
            <label>Sector Focus</label>
            <select v-model="form.environment_vars.sector_focus">
              <option value="general">General</option>
              <option value="tech">Tech</option>
              <option value="finance">Finance</option>
              <option value="energy">Energy</option>
              <option value="crypto">Crypto / Digital Assets</option>
            </select>
          </div>
          <div class="form-group">
            <label>Fed Stance</label>
            <select v-model="form.environment_vars.fed_stance">
              <option value="hawkish">Hawkish</option>
              <option value="neutral">Neutral</option>
              <option value="dovish">Dovish</option>
            </select>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.environment_vars.election_year" />
              Election Year Volatility
            </label>
          </div>
        </div>
      </div>

      <div class="card form-section">
        <h2>Simulation Parameters</h2>
        <div class="params-grid">
          <div class="form-group">
            <label>Duration (minutes)</label>
            <input v-model.number="form.duration_minutes" type="number" min="1" max="1440" />
          </div>
          <div class="form-group">
            <label>Agent Count</label>
            <input v-model.number="form.agent_count" type="number" min="10" max="1000" />
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="submitting">
          {{ submitting ? 'Creating...' : 'Create & Configure' }}
        </button>
        <NuxtLink to="/scenarios">
          <button type="button" class="btn-secondary">Cancel</button>
        </NuxtLink>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { ScenarioCreate, EnvironmentVars } from "~/types/scenario";

const router = useRouter();
const { createScenario } = useScenarios();

const submitting = ref(false);

const form = ref<ScenarioCreate>({
  name: "",
  description: "",
  seed_event: "",
  environment_vars: {
    market_volatility: "normal",
    sector_focus: "general",
    election_year: false,
    fed_stance: "neutral",
  },
  duration_minutes: 60,
  agent_count: 50,
});

async function handleSubmit() {
  submitting.value = true;
  try {
    const scenario = await createScenario(form.value);
    router.push(`/simulation/${scenario.id}`);
  } catch (e) {
    console.error("Failed to create scenario:", e);
    alert("Failed to create scenario. Check the console for details.");
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.new-scenario h1 {
  margin-bottom: 4px;
}

.subtitle {
  color: var(--color-text-secondary);
  margin-bottom: 24px;
}

.scenario-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
}

.form-section h2 {
  font-size: 16px;
  margin-bottom: 16px;
  color: var(--color-primary);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--color-text-secondary);
}

.env-grid, .params-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding-top: 20px;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.form-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
</style>
