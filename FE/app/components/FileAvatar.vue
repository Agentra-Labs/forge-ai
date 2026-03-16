<script setup lang="ts">
interface FileAvatarProps {
  name: string
  type: string
  previewUrl?: string
  status?: 'idle' | 'uploading' | 'uploaded' | 'error'
  error?: string
  removable?: boolean
}

withDefaults(defineProps<FileAvatarProps>(), {
  status: 'idle',
  removable: false
})

const emit = defineEmits<{
  remove: []
}>()
</script>

<template>
  <div class="relative group">
    <div class="tooltip tooltip-bottom" :data-tip="removeRandomSuffix(name)">
      <div class="avatar transition-opacity" :class="{'opacity-50': status === 'uploading'}">
        <div class="w-16 rounded-lg bg-base-200 relative flex items-center justify-center">
          <img v-if="type.startsWith('image/') && previewUrl" :src="previewUrl" :alt="name" class="object-cover w-full h-full" />
          <Icon v-else :name="getFileIcon(type, name).replace('i-', '').replace('-', ':')" class="w-8 h-8 text-base-content/50" />
        </div>
      </div>
    </div>

    <div
      v-if="status === 'uploading'"
      class="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg"
    >
      <Icon name="lucide:loader-2" class="size-6 animate-spin text-white" />
    </div>

    <div v-if="status === 'error'" class="tooltip tooltip-bottom" :data-tip="error">
      <div class="absolute inset-0 flex items-center justify-center bg-error/50 rounded-lg">
        <Icon name="lucide:alert-circle" class="size-6 text-white" />
      </div>
    </div>

    <button
      v-if="removable && status !== 'uploading'"
      class="btn btn-circle btn-xs btn-ghost bg-base-100 hover:bg-base-200 absolute -top-1 -right-1 opacity-0 group-hover:opacity-100 transition-opacity ring-1 ring-base-300"
      @click="emit('remove')"
    >
      <Icon name="lucide:x" class="w-3 h-3" />
    </button>
  </div>
</template>
