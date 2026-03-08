<script setup lang="ts">
withDefaults(defineProps<{
  compact?: boolean
}>(), {
  compact: false
})

const { mode, modes } = useResearchMode()
</script>

<template>
  <div
    class="rounded-2xl border border-base-300 bg-base-100/80 p-1"
    :class="compact ? 'inline-flex' : 'w-full'"
  >
    <div class="grid gap-1" :class="compact ? 'grid-cols-2' : 'grid-cols-1 sm:grid-cols-2'">
      <button
        v-for="option in modes"
        :key="option.value"
        type="button"
        class="rounded-xl px-3 py-2 text-left transition-colors"
        :class="mode === option.value ? 'bg-primary text-primary-content shadow-sm' : 'hover:bg-base-200'"
        @click="mode = option.value"
      >
        <div class="flex items-center gap-2">
          <Icon :name="option.value === 'deep' ? 'lucide:scan-search' : 'lucide:network'" class="h-4 w-4" />
          <span class="text-sm font-medium">{{ option.label }}</span>
        </div>
        <p v-if="!compact" class="mt-1 text-xs leading-5" :class="mode === option.value ? 'text-primary-content/80' : 'text-base-content/60'">
          {{ option.description }}
        </p>
      </button>
    </div>
  </div>
</template>
