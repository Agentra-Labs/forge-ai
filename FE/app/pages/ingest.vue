<script setup lang="ts">
import { ref, reactive } from "vue";

// Form state
const query = ref("");
const containerTag = ref("");
const mode = ref("standard");
const maxCandidates = ref(10);
const jobId = ref<string | null>(null);
const logs = ref<string[]>([]);
const result = ref<any>(null);
const polling = ref(false);

// Preset configurations
const presets = [
  { label: "AI Research", tag: "ai-research", query: "artificial intelligence machine learning" },
  { label: "Climate Science", tag: "climate-science", query: "climate change global warming carbon emissions" },
  { label: "Biotechnology", tag: "biotech", query: "gene therapy biotechnology CRISPR" },
];

// Function to start ingestion process
async function startIngest() {
  logs.value = ["Starting ingestion process..."];
  result.value = null;
  jobId.value = null;

  try {
    const res = await fetch("/api/ingest", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query.value,
        container_tag: containerTag.value,
        max_candidates: maxCandidates.value,
        citation_expansion: mode.value === "expanded",
      }),
    });

    const data = await res.json();

    if (data.error) {
      throw new Error(data.error);
    }

    jobId.value = data.job_id;
    logs.value.push(`Job started with ID: ${jobId.value}`);

    // Start polling for job status
    pollJob();
  } catch (error: any) {
    logs.value.push(`Error: ${error.message}`);
  }
}

// Function to poll job status
async function pollJob() {
  if (!jobId.value) return;

  polling.value = true;

  try {
    const jobResponse = await fetch(`/api/ingest/${jobId.value}`);
    const job = await jobResponse.json();

    if (job.error) {
      throw new Error(job.error);
    }

    if (job.status === "completed") {
      polling.value = false;
      result.value = job.result;
      logs.value.push("Ingestion completed successfully!");
    } else if (job.status === "failed") {
      polling.value = false;
      logs.value.push(`Job failed: ${job.error}`);
    } else {
      // Still processing, continue polling
      logs.value.push(`Processing... ${job.progress}%`);
      setTimeout(pollJob, 2000); // Poll every 2 seconds
    }
  } catch (error: any) {
    polling.value = false;
    logs.value.push(`Polling error: ${error.message}`);
  }
}

// Function to apply preset
function applyPreset(preset: typeof presets[0]) {
  containerTag.value = preset.tag;
  query.value = preset.query;
}
</script>

<template>
  <div class="ingest-page">
    <h1>Paper Ingestion</h1>

    <div class="presets">
      <h2>Quick Start Presets</h2>
      <button
        v-for="preset in presets"
        :key="preset.label"
        @click="applyPreset(preset)"
        class="preset-button"
      >
        {{ preset.label }}
      </button>
    </div>

    <div class="form-section">
      <div class="form-group">
        <label for="query">Search Query</label>
        <input
          id="query"
          v-model="query"
          type="text"
          placeholder="Enter search terms..."
        >
      </div>

      <div class="form-group">
        <label for="containerTag">Container Tag</label>
        <input
          id="containerTag"
          v-model="containerTag"
          type="text"
          placeholder="Tag for organizing papers"
        >
      </div>

      <div class="form-group">
        <label>Mode</label>
        <div class="mode-buttons">
          <button
            :class="{ active: mode === 'standard' }"
            @click="mode = 'standard'"
          >
            Standard
          </button>
          <button
            :class="{ active: mode === 'expanded' }"
            @click="mode = 'expanded'"
          >
            Expanded Search
          </button>
        </div>
      </div>

      <div class="form-group">
        <label for="maxCandidates">Max Candidates</label>
        <input
          id="maxCandidates"
          v-model.number="maxCandidates"
          type="number"
          min="1"
          max="100"
        >
      </div>

      <button
        @click="startIngest"
        :disabled="polling || !query || !containerTag"
        class="submit-button"
      >
        {{ polling ? 'Processing...' : 'Start Ingestion' }}
      </button>
    </div>

    <div class="results-section">
      <div class="logs">
        <h3>Process Logs</h3>
        <div v-for="(log, index) in logs" :key="index" class="log-entry">
          {{ log }}
        </div>
      </div>

      <div v-if="result" class="result-summary">
        <h3>Ingestion Results</h3>
        <p><strong>Processed Papers:</strong> {{ result.processed_count }}</p>
        <p><strong>Synthesized Summary:</strong></p>
        <blockquote>{{ result.synthesis }}</blockquote>

        <NuxtLink to="/graph" class="view-graph-link">
          View in Knowledge Graph
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ingest-page {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.presets {
  margin-bottom: 2rem;
}

.presets h2 {
  margin-bottom: 1rem;
}

.preset-button {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f0f0f0;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.preset-button:hover {
  background: #e0e0e0;
}

.form-section {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
}

.mode-buttons {
  display: flex;
  gap: 1rem;
}

.mode-buttons button {
  padding: 0.5rem 1rem;
  background: #e0e0e0;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.mode-buttons button.active {
  background: #3b82f6;
  color: white;
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
}

.submit-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.results-section {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 0.5rem;
}

.logs {
  margin-bottom: 2rem;
}

.log-entry {
  padding: 0.25rem 0;
  font-family: monospace;
  font-size: 0.9rem;
}

.result-summary blockquote {
  background: white;
  padding: 1rem;
  border-left: 4px solid #3b82f6;
  margin: 1rem 0;
  border-radius: 0 0.25rem 0.25rem 0;
}

.view-graph-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #10b981;
  color: white;
  text-decoration: none;
  border-radius: 0.25rem;
}
</style>
