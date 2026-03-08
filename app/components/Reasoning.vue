<script setup lang="ts">
const { isStreaming = false } = defineProps<{
  text: string
  isStreaming?: boolean
}>()

const open = ref(false)

watch(() => isStreaming, () => {
  open.value = isStreaming
}, { immediate: true })

function cleanMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1') // Remove bold
    .replace(/\*(.+?)\*/g, '$1') // Remove italic
    .replace(/`(.+?)`/g, '$1') // Remove inline code
    .replace(/^#+\s+/gm, '') // Remove headers
}

function onToggle(event: Event) {
  const target = event.target as HTMLDetailsElement | null
  open.value = target?.open ?? false
}
</script>

<template>
  <details class="collapse collapse-arrow bg-base-100/50 my-5" :open="open" @toggle="onToggle">
    <summary class="collapse-title text-sm font-medium w-auto inline-flex items-center gap-2 cursor-pointer p-0 group" :class="{ 'pl-0': true, 'pr-6': text.length > 0 }">
      {{ isStreaming ? 'Thinking...' : 'Thoughts' }}
    </summary>
    <div class="collapse-content px-0">
      <div v-for="(value, index) in cleanMarkdown(text).split('\n').filter(Boolean)" :key="index">
        <span class="whitespace-pre-wrap text-sm text-base-content/70 font-normal">{{ value }}</span>
      </div>
    </div>
  </details>
</template>
