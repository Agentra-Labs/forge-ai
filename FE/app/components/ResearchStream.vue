<script setup lang="ts">
/**
 * ResearchStream - Live step-by-step progress display during research.
 * Shows workflow phases, progress indicators, and intermediate results.
 */

defineProps<{
  steps: ReadonlyArray<{ name: string, status: string, content: string }>
  currentStep: string
  isRunning: boolean
  content: string
  error: string | null
}>()
</script>

<template>
  <div class="space-y-3">
    <!-- Step Progress -->
    <div v-if="steps.length > 0" class="rounded-2xl border border-base-300/70 bg-base-200/50 p-4">
      <div class="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary/80">
        <Icon name="lucide:workflow" class="h-3.5 w-3.5" />
        <span>Research Pipeline</span>
      </div>

      <ul class="steps steps-vertical lg:steps-horizontal w-full">
        <li
          v-for="(step, i) in steps"
          :key="i"
          class="step"
          :class="{
            'step-primary': step.status === 'completed',
            'step-warning': step.status === 'running',
            'step-error': step.status === 'failed'
          }"
        >
          <span class="text-xs">{{ step.name }}</span>
        </li>
      </ul>
    </div>

    <!-- Current Activity -->
    <div v-if="isRunning && currentStep" class="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 px-4 py-2.5">
      <span class="loading loading-spinner loading-xs text-primary"></span>
      <span class="text-sm text-primary/90">{{ currentStep }}</span>
    </div>

    <!-- Error Display -->
    <div v-if="error" role="alert" class="alert alert-error">
      <Icon name="lucide:alert-circle" class="h-4 w-4" />
      <span class="text-sm">{{ error }}</span>
    </div>

    <!-- Streaming Content -->
    <div v-if="content" class="rounded-2xl border border-base-300/75 bg-base-100/72 p-4 shadow-sm">
      <MDCCached
        :value="content"
        cache-key="research-stream"
        class="prose prose-sm max-w-none *:first:mt-0 *:last:mb-0"
      />
    </div>

    <!-- Loading placeholder when no content yet -->
    <div v-else-if="isRunning && !content" class="flex items-center gap-3 rounded-2xl border border-base-300/75 bg-base-100/72 p-4 shadow-sm">
      <span class="loading loading-dots loading-sm text-primary"></span>
      <span class="text-sm text-base-content/60">Analyzing papers and synthesizing results...</span>
    </div>
  </div>
</template>
