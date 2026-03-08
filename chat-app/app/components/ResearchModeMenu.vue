<script setup lang="ts">
const { mode, modes } = useResearchMode()

const currentMode = computed(() => modes.find(option => option.value === mode.value) || modes[0])
</script>

<template>
  <div class="dropdown dropdown-top dropdown-end">
    <button type="button" tabindex="0" class="btn btn-ghost btn-sm rounded-full border border-base-300/70 bg-base-100/70 px-3">
      <Icon :name="currentMode.value === 'deep' ? 'lucide:scan-search' : 'lucide:network'" class="h-4 w-4" />
      <span>{{ currentMode.value === 'deep' ? 'Deep' : 'Wide' }}</span>
      <Icon name="lucide:chevrons-up-down" class="h-3.5 w-3.5 text-base-content/50" />
    </button>

    <ul tabindex="0" class="menu dropdown-content z-[1] mb-2 w-56 rounded-2xl border border-base-300/80 bg-base-100 p-2 shadow-xl">
      <li v-for="option in modes" :key="option.value">
        <button
          type="button"
          class="flex items-start gap-3 rounded-xl"
          :class="mode === option.value ? 'bg-base-200' : ''"
          @click="mode = option.value"
        >
          <Icon :name="option.value === 'deep' ? 'lucide:scan-search' : 'lucide:network'" class="mt-0.5 h-4 w-4 shrink-0" />
          <span class="min-w-0">
            <span class="block text-sm font-medium">{{ option.label }}</span>
            <span class="block text-xs leading-5 text-base-content/55">{{ option.description }}</span>
          </span>
        </button>
      </li>
    </ul>
  </div>
</template>
