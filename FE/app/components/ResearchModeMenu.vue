<script setup lang="ts">
const { mode, modes, currentModeInfo, isIdeateMode } = useResearchMode()

// Group modes for display
const researchModes = computed(() => modes.filter(m => m.group === 'research'))
const ideateMode = computed(() => modes.find(m => m.group === 'ideate'))
</script>

<template>
  <div class="dropdown dropdown-top dropdown-end">
    <button type="button" tabindex="0" class="btn btn-sm rounded-full border border-base-300/80 bg-base-100 px-3.5 shadow-sm text-base-content hover:bg-base-200" :class="{ 'border-primary/40 bg-primary/5': isIdeateMode }">
      <Icon :name="currentModeInfo.icon" class="h-4 w-4" :class="isIdeateMode ? 'text-primary' : ''" />
      <span class="font-medium" :class="isIdeateMode ? 'text-primary' : ''">{{ currentModeInfo.label.split(' ')[0] }}</span>
      <Icon name="lucide:chevrons-up-down" class="h-3.5 w-3.5 text-base-content/60" />
    </button>

    <ul tabindex="0" class="menu dropdown-content z-[1] mb-2 w-60 rounded-2xl border border-base-300/80 bg-base-100 p-2 shadow-xl">
      <!-- Research Modes -->
      <li class="menu-title px-2 py-1.5 text-[10px] uppercase tracking-wider text-base-content/45">
        Research Modes
      </li>
      <li v-for="option in researchModes" :key="option.value">
        <button
          type="button"
          class="flex items-start gap-3 rounded-xl"
          :class="mode === option.value ? 'bg-base-200' : ''"
          @click="mode = option.value"
        >
          <Icon :name="option.icon" class="mt-0.5 h-4 w-4 shrink-0" />
          <span class="min-w-0">
            <span class="block text-sm font-medium">{{ option.label }}</span>
            <span class="block text-xs leading-5 text-base-content/55">{{ option.description }}</span>
          </span>
        </button>
      </li>
      
      <!-- Divider -->
      <li class="my-1 h-px bg-base-300/70"></li>
      
      <!-- Ideate Mode -->
      <li v-if="ideateMode">
        <button
          type="button"
          class="flex items-start gap-3 rounded-xl"
          :class="isIdeateMode ? 'bg-primary/10' : ''"
          @click="mode = ideateMode.value"
        >
          <Icon :name="ideateMode.icon" class="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <span class="min-w-0">
            <span class="block text-sm font-medium" :class="isIdeateMode ? 'text-primary' : ''">{{ ideateMode.label }}</span>
            <span class="block text-xs leading-5 text-base-content/55">{{ ideateMode.description }}</span>
          </span>
        </button>
      </li>
    </ul>
  </div>
</template>
