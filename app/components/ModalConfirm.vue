<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()

const emit = defineEmits<{ close: [boolean] }>()
</script>

<template>
  <dialog class="modal modal-open">
    <div class="modal-box">
      <h3 class="font-bold text-lg">{{ title }}</h3>
      <p class="py-4">{{ description }}</p>
      <div class="modal-action flex flex-row-reverse justify-start">
        <button class="btn btn-primary" @click="emit('close', true)">Delete</button>
        <button class="btn btn-ghost" @click="emit('close', false)">Cancel</button>
      </div>
    </div>
  </dialog>
</template>
