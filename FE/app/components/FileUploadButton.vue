<script setup lang="ts">
const { isLoaded, isSignedIn } = useAuth()

const canUpload = computed(() => isLoaded.value && isSignedIn.value)

defineProps<{
  open: () => void
}>()
</script>

<template>
  <div class="tooltip tooltip-top" :data-tip="!canUpload ? 'Sign in with Google to upload files' : ''">
    <button
      type="button"
      class="btn btn-ghost btn-circle btn-sm w-8 h-8 min-h-0 shrink-0 text-base-content hover:bg-base-300/50"
      :disabled="!canUpload"
      @click="open()"
    >
      <Icon name="lucide:plus" class="w-4 h-4" />
    </button>
  </div>
</template>
