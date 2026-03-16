<script setup lang="ts">
const { model, models } = useModels()
const selectedModel = computed(() => models.find(m => m.value === model.value))
</script>

<template>
  <div class="relative inline-block w-auto min-w-[6rem]">
    <div v-if="selectedModel?.icon" class="absolute inset-y-0 left-0 flex items-center pl-2.5 pointer-events-none">
      <Icon :name="selectedModel.icon" class="w-3.5 h-3.5 text-base-content/60" />
    </div>
    <select
      v-model="model"
      class="select select-sm select-ghost w-auto font-medium text-[13px] text-base-content/80 hover:bg-base-200/50 hover:text-base-content transition-colors pr-6 focus:bg-transparent"
      :class="{ 'pl-7': selectedModel?.icon, 'pl-3': !selectedModel?.icon }"
    >
      <option v-for="m in models" :key="m.value" :value="m.value">
        {{ m.label }}
      </option>
    </select>
  </div>
</template>
