<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modeLabel?: string
  }>(),
  {
    modeLabel: 'Deep Research'
  }
)

const steps = [
  { id: 1, label: 'Wide Scan' },
  { id: 2, label: 'Paper Reading' },
  { id: 3, label: 'Deep Analysis' }
]
</script>

<template>
  <aside class="flex h-full flex-col gap-4">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-[11px] uppercase tracking-[0.28em] text-base-content/45">
          Steps
        </p>
      </div>
      <div class="badge badge-outline rounded-full border-base-300/70 bg-base-100/70 px-3 py-2 text-[11px] font-medium uppercase tracking-[0.16em] text-base-content/60">
        {{ props.modeLabel }}
      </div>
    </div>

    <div class="rounded-2xl border border-base-300/70 bg-base-100/70 p-3">
      <ol class="space-y-2">
        <li
          v-for="step in steps"
          :key="step.id"
          class="flex items-center justify-between gap-3 rounded-xl border border-base-300/70 bg-base-200/70 px-3 py-2 text-sm text-base-content/80"
        >
          <div class="flex items-center gap-2">
            <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-base-100 text-[11px] text-base-content/70">
              {{ step.id }}
            </span>
            <span>
              {{ step.label }}
            </span>
          </div>
        </li>
      </ol>
    </div>
  </aside>
</template>

