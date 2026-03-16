<script setup lang="ts">
import { ref } from "vue";

// Define available spaces/tabs
const spaces = [
  { id: "default", label: "All Papers" },
  { id: "computer-science", label: "Computer Science" },
  { id: "biology", label: "Biology" },
  { id: "physics", label: "Physics" },
  { id: "mathematics", label: "Mathematics" },
];

// Reactive state for active space
const activeSpace = ref(spaces[0].id);

// Function to switch active space
function setActiveSpace(spaceId: string) {
  activeSpace.value = spaceId;
}
</script>

<template>
  <div class="graph-page">
    <div class="header">
      <h1>Knowledge Graph</h1>
      <p>Visualize relationships between research papers and concepts</p>
    </div>

    <!-- Space tabs navigation -->
    <nav class="space-tabs">
      <button
        v-for="space in spaces"
        :key="space.id"
        :class="{ tab: true, active: activeSpace === space.id }"
        @click="setActiveSpace(space.id)"
      >
        {{ space.label }}
      </button>
    </nav>

    <!-- Graph visualization area -->
    <div class="graph-canvas">
      <MemoryGraphWrapper :space="activeSpace" />
    </div>
  </div>
</template>

<style scoped>
.graph-page {
  padding: 2rem;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.header p {
  color: #666;
}

.space-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 1rem;
}

.tab {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab:hover {
  background: #f5f5f5;
}

.tab.active {
  background: #3b82f6;
  color: white;
}

.graph-canvas {
  flex: 1;
  border: 1px solid #e5e5e5;
  border-radius: 0.5rem;
  overflow: hidden;
  background: white;
}
</style>
