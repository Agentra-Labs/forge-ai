<script setup lang="ts">
const { model, models } = useModels()
const selectedModel = computed(() => models.find(m => m.value === model.value))
</script>

<template>
  <div class="relative inline-block w-full max-w-xs">
    <div v-if="selectedModel?.icon" class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
      <Icon :name="selectedModel.icon" class="w-4 h-4 text-base-content/50" />
    </div>
    <select
      v-model="model"
      class="select select-sm select-ghost w-full"
      :class="{ 'pl-8': selectedModel?.icon }"
    >
      <option v-for="m in models" :key="m.value" :value="m.value">
        {{ m.label }}
      </option>
    </select>
  </div>
</template>
