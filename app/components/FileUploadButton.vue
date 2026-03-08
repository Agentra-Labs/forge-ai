<script setup lang="ts">
const { loggedIn } = useUserSession()

defineProps<{
  open: () => void
}>()
</script>

<template>
  <div class="tooltip tooltip-top" :data-tip="!loggedIn ? 'You need to be logged in to upload files' : ''">
    <button
      class="btn btn-ghost btn-sm"
      :disabled="!loggedIn"
      @click="open()"
    >
      <Icon name="lucide:paperclip" class="w-4 h-4" />
    </button>
  </div>
</template>
