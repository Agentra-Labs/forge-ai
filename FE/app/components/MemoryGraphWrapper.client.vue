<script setup lang="ts">
import { ref, onMounted, watch } from "vue";

// Define props
const props = defineProps<{
  space?: string;
}>();

// Reactive state
const documents = ref<any[]>([]);
const isLoading = ref(false);
const isLoadingMore = ref(false);
const hasMore = ref(true);
const error = ref<string | null>(null);
const currentPage = ref(1);
const LIMIT = 20;

// Fetch documents function
async function fetchDocs(page: number = 1) {
  try {
    isLoading.value = page === 1;
    isLoadingMore.value = page > 1;

    const params = new URLSearchParams({
      page: page.toString(),
      limit: LIMIT.toString(),
      space: props.space || "default",
    });

    const response = await fetch(`/api/graph?${params.toString()}`);
    const data = await response.json();

    if (data.statusCode === 500) {
      throw new Error(data.message || "Failed to fetch documents");
    }

    if (page === 1) {
      documents.value = data.documents || [];
    } else {
      documents.value = [...documents.value, ...(data.documents || [])];
    }

    hasMore.value = data.hasMore || false;
    currentPage.value = page;
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "An unknown error occurred";
  } finally {
    isLoading.value = false;
    isLoadingMore.value = false;
  }
}

// Load more documents
async function loadMore() {
  if (!hasMore.value || isLoadingMore.value) return;
  await fetchDocs(currentPage.value + 1);
}

// Fetch initial documents on mount
onMounted(() => {
  fetchDocs();
});

// Reset and fetch first page when space changes
watch(
  () => props.space,
  () => {
    currentPage.value = 1;
    fetchDocs(1);
  },
);
</script>

<template>
  <div class="memory-graph-wrapper">
    <div v-if="isLoading" class="loading">Loading documents...</div>

    <div v-else-if="error" class="error">Error: {{ error }}</div>

    <div v-else class="graph-container">
      <MemoryGraph
        :documents="documents"
        :space="space"
        @load-more="loadMore"
        :loading="isLoadingMore"
        :has-more="hasMore"
      />
    </div>
  </div>
</template>

<style scoped>
.memory-graph-wrapper {
  width: 100%;
  height: 100%;
}

.loading,
.error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.1rem;
}

.error {
  color: #ef4444;
}

.graph-container {
  height: 100%;
}
</style>
