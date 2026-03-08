<script setup lang="ts">
/**
 * PaperCard - Display a single paper review card.
 * Shows title, authors, relevance score, technique tags, and expandable review.
 */

const props = defineProps<{
  title: string
  authors?: string[]
  year?: number
  url?: string
  arxivId?: string
  relevanceScore?: number
  techniques?: string[]
  claims?: string[]
  limitations?: string[]
  reviewPass?: 1 | 2 | 3
  critique?: string
  codeUrl?: string
}>()

const expanded = ref(false)

const scoreColor = computed(() => {
  const s = props.relevanceScore ?? 0
  if (s >= 0.7) return 'badge-success'
  if (s >= 0.4) return 'badge-warning'
  return 'badge-ghost'
})

const passLabel = computed(() => {
  switch (props.reviewPass) {
    case 1: return 'Skim'
    case 2: return 'Structure'
    case 3: return 'Deep'
    default: return ''
  }
})
</script>

<template>
  <div class="card card-border border-base-300/70 bg-base-100/80 shadow-sm transition-all hover:shadow-md">
    <div class="card-body p-4">
      <!-- Header -->
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0 flex-1">
          <h3 class="card-title text-sm font-semibold leading-snug">
            <a
              v-if="url"
              :href="url"
              target="_blank"
              rel="noopener"
              class="link-hover link-primary"
            >{{ title }}</a>
            <span v-else>{{ title }}</span>
          </h3>
          <p v-if="authors?.length" class="mt-1 text-xs text-base-content/60">
            {{ authors.slice(0, 3).join(', ') }}
            <span v-if="(authors?.length ?? 0) > 3"> +{{ (authors?.length ?? 0) - 3 }} more</span>
            <span v-if="year" class="ml-2 text-base-content/40">· {{ year }}</span>
          </p>
        </div>

        <div class="flex shrink-0 items-center gap-1.5">
          <span v-if="reviewPass" class="badge badge-outline badge-xs">{{ passLabel }}</span>
          <span
            v-if="relevanceScore !== undefined"
            class="badge badge-sm font-mono"
            :class="scoreColor"
          >{{ (relevanceScore * 100).toFixed(0) }}%</span>
        </div>
      </div>

      <!-- Technique Tags -->
      <div v-if="techniques?.length" class="mt-2 flex flex-wrap gap-1">
        <span
          v-for="tech in techniques.slice(0, 6)"
          :key="tech"
          class="badge badge-primary badge-outline badge-xs"
        >{{ tech }}</span>
        <span v-if="(techniques?.length ?? 0) > 6" class="badge badge-ghost badge-xs">
          +{{ (techniques?.length ?? 0) - 6 }}
        </span>
      </div>

      <!-- Quick Info -->
      <div v-if="claims?.length || limitations?.length" class="mt-2 flex gap-3 text-xs text-base-content/60">
        <span v-if="claims?.length" class="flex items-center gap-1">
          <Icon name="lucide:check-circle" class="h-3 w-3 text-success" />
          {{ claims.length }} claims
        </span>
        <span v-if="limitations?.length" class="flex items-center gap-1">
          <Icon name="lucide:alert-triangle" class="h-3 w-3 text-warning" />
          {{ limitations.length }} limitations
        </span>
        <a v-if="codeUrl" :href="codeUrl" target="_blank" rel="noopener" class="flex items-center gap-1 link-hover">
          <Icon name="lucide:github" class="h-3 w-3" />
          Code
        </a>
      </div>

      <!-- Expandable Details -->
      <div v-if="claims?.length || limitations?.length || critique" class="mt-2">
        <button
          class="btn btn-ghost btn-xs gap-1"
          @click="expanded = !expanded"
        >
          <Icon :name="expanded ? 'lucide:chevron-up' : 'lucide:chevron-down'" class="h-3 w-3" />
          {{ expanded ? 'Less' : 'More' }}
        </button>

        <div v-if="expanded" class="mt-2 space-y-2 text-xs">
          <div v-if="claims?.length">
            <p class="font-semibold text-success/80">Key Claims:</p>
            <ul class="list-inside list-disc text-base-content/70">
              <li v-for="claim in claims" :key="claim">{{ claim }}</li>
            </ul>
          </div>
          <div v-if="limitations?.length">
            <p class="font-semibold text-warning/80">Limitations:</p>
            <ul class="list-inside list-disc text-base-content/70">
              <li v-for="lim in limitations" :key="lim">{{ lim }}</li>
            </ul>
          </div>
          <div v-if="critique">
            <p class="font-semibold text-info/80">Critique:</p>
            <p class="text-base-content/70">{{ critique }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
