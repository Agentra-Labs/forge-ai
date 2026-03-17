<script setup lang="ts">
import type { PaperReview } from '#shared/types/research'

const props = defineProps<{
  paper: PaperReview
  compact?: boolean
}>()

const expanded = ref(false)
const relevanceColor = computed(() => {
  const score = props.paper.relevance_score
  if (score >= 0.8) return 'text-success'
  if (score >= 0.6) return 'text-primary'
  if (score >= 0.4) return 'text-warning'
  return 'text-base-content/60'
})

const relevanceLabel = computed(() => {
  const score = props.paper.relevance_score
  if (score >= 0.8) return 'Highly Relevant'
  if (score >= 0.6) return 'Relevant'
  if (score >= 0.4) return 'Moderate'
  return 'Low'
})
</script>

<template>
  <div class="rounded-2xl border border-base-300/70 bg-base-100/70 p-4 transition-all hover:border-primary/30">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <div class="flex items-start gap-2">
          <a 
            :href="paper.url" 
            target="_blank" 
            rel="noopener"
            class="text-sm font-medium leading-snug text-base-content hover:text-primary line-clamp-2"
          >
            {{ paper.title }}
          </a>
        </div>
        
        <div class="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-base-content/55">
          <span v-if="paper.year" class="inline-flex items-center gap-1">
            <Icon name="lucide:calendar" class="h-3 w-3" />
            {{ paper.year }}
          </span>
          <span v-if="paper.citation_count" class="inline-flex items-center gap-1">
            <Icon name="lucide:quote" class="h-3 w-3" />
            {{ paper.citation_count }} citations
          </span>
          <span v-if="paper.venue" class="inline-flex items-center gap-1">
            <Icon name="lucide:building-2" class="h-3 w-3" />
            {{ paper.venue }}
          </span>
          <span v-if="paper.arxiv_id" class="rounded bg-base-200 px-1.5 py-0.5 font-mono text-[10px]">
            arXiv:{{ paper.arxiv_id }}
          </span>
        </div>

        <p v-if="!compact" class="mt-2 text-xs leading-relaxed text-base-content/60 line-clamp-2">
          {{ paper.abstract }}
        </p>
      </div>

      <div class="flex flex-col items-end gap-1">
        <div class="flex items-center gap-1.5 rounded-full border px-2.5 py-1" :class="[
          relevanceColor,
          paper.relevance_score >= 0.6 ? 'border-current/20 bg-current/5' : 'border-base-300/50 bg-base-200/50'
        ]">
          <Icon name="lucide:sparkles" class="h-3 w-3" />
          <span class="text-xs font-medium">{{ (paper.relevance_score * 100).toFixed(0) }}%</span>
        </div>
        <span class="text-[10px] uppercase tracking-wide text-base-content/40">{{ relevanceLabel }}</span>
      </div>
    </div>

    <!-- Expandable details -->
    <div v-if="!compact && (paper.techniques?.length || paper.claims?.length || paper.methods?.length)" class="mt-3">
      <button 
        type="button"
        class="flex items-center gap-1 text-xs text-primary/80 hover:text-primary"
        @click="expanded = !expanded"
      >
        <Icon :name="expanded ? 'lucide:chevron-up' : 'lucide:chevron-down'" class="h-3.5 w-3.5" />
        {{ expanded ? 'Hide details' : 'Show details' }}
      </button>

      <div v-if="expanded" class="mt-2 space-y-2 border-t border-base-300/50 pt-3">
        <div v-if="paper.techniques?.length" class="flex flex-wrap gap-1.5">
          <span class="text-[10px] uppercase tracking-wide text-base-content/40">Techniques:</span>
          <span 
            v-for="tech in paper.techniques.slice(0, 5)" 
            :key="tech"
            class="rounded-full bg-base-200 px-2 py-0.5 text-xs text-base-content/70"
          >
            {{ tech }}
          </span>
        </div>

        <div v-if="paper.methods?.length" class="flex flex-wrap gap-1.5">
          <span class="text-[10px] uppercase tracking-wide text-base-content/40">Methods:</span>
          <span 
            v-for="method in paper.methods.slice(0, 3)" 
            :key="method"
            class="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary/80"
          >
            {{ method }}
          </span>
        </div>

        <div v-if="paper.claims?.length" class="space-y-1">
          <span class="text-[10px] uppercase tracking-wide text-base-content/40">Key Claims:</span>
          <ul class="text-xs text-base-content/60 list-disc list-inside">
            <li v-for="claim in paper.claims.slice(0, 3)" :key="claim">{{ claim }}</li>
          </ul>
        </div>

        <div v-if="paper.limitations?.length" class="space-y-1">
          <span class="text-[10px] uppercase tracking-wide text-warning/70">Limitations:</span>
          <ul class="text-xs text-base-content/60 list-disc list-inside">
            <li v-for="lim in paper.limitations.slice(0, 2)" :key="lim">{{ lim }}</li>
          </ul>
        </div>

        <div v-if="paper.code_url" class="pt-1">
          <a 
            :href="paper.code_url" 
            target="_blank"
            class="inline-flex items-center gap-1.5 rounded-lg bg-base-200 px-2.5 py-1 text-xs text-base-content/70 hover:bg-base-300"
          >
            <Icon name="lucide:github" class="h-3.5 w-3.5" />
            Code
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
