<script setup lang="ts">
import type { PipelinePhase } from '#shared/types/research'

const props = withDefaults(defineProps<{
  phases: PipelinePhase[]
  currentPhase?: string
  compact?: boolean
}>(), {
  compact: false
})

const phaseIcon = (status: PipelinePhase['status']) => {
  switch (status) {
    case 'completed': return 'lucide:check-circle-2'
    case 'running': return 'lucide:loader-2'
    case 'failed': return 'lucide:x-circle'
    default: return 'lucide:circle'
  }
}

const phaseColor = (status: PipelinePhase['status']) => {
  switch (status) {
    case 'completed': return 'text-success bg-success/10 border-success/30'
    case 'running': return 'text-primary bg-primary/10 border-primary/30 animate-pulse'
    case 'failed': return 'text-error bg-error/10 border-error/30'
    default: return 'text-base-content/40 bg-base-200/50 border-base-300/50'
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <p class="text-[11px] uppercase tracking-[0.28em] text-base-content/45">
        Pipeline
      </p>
      <div class="rounded-full border border-base-300/70 bg-base-100/70 px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.16em] text-base-content/60">
        {{ phases.filter(p => p.status === 'completed').length }}/{{ phases.length }}
      </div>
    </div>

    <div class="rounded-2xl border border-base-300/70 bg-base-100/70 p-3">
      <ol class="space-y-2">
        <li
          v-for="(phase, index) in phases"
          :key="phase.id"
          class="flex items-center gap-3 rounded-xl border p-2.5 transition-all"
          :class="phaseColor(phase.status)"
        >
          <div class="flex h-6 w-6 items-center justify-center rounded-full border text-[10px] font-medium"
               :class="phaseColor(phase.status)">
            <Icon v-if="phase.status === 'running'" name="lucide:loader-2" class="h-3.5 w-3.5 animate-spin" />
            <Icon v-else-if="phase.status === 'completed'" name="lucide:check" class="h-3.5 w-3.5" />
            <Icon v-else-if="phase.status === 'failed'" name="lucide:x" class="h-3.5 w-3.5" />
            <span v-else>{{ index + 1 }}</span>
          </div>
          
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium truncate" :class="phase.status === 'pending' ? 'text-base-content/50' : ''">
              {{ phase.name }}
            </p>
            <p v-if="!compact && phase.description" class="text-[11px] text-base-content/50 truncate">
              {{ phase.description }}
            </p>
          </div>

          <span v-if="phase.duration" class="text-[10px] text-base-content/40">
            {{ (phase.duration / 1000).toFixed(1) }}s
          </span>
        </li>
      </ol>
    </div>
  </div>
</template>
