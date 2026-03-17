<script setup lang="ts">
import type { IdeateJob, IdeateJobStart } from '#shared/types/research'

const props = defineProps<{
  chatId: string
}>()

const emit = defineEmits<{
  started: [jobId: string, arxivId: string]
  completed: [result: string]
  error: [message: string]
}>()

const toast = useToast()
const { csrf, headerName } = useCsrf()

const arxivInput = ref('')
const loading = ref(false)
const jobId = ref<string | null>(null)
const jobStatus = ref<IdeateJob | null>(null)
const pollInterval = ref<NodeJS.Timeout | null>(null)

const arxivPattern = /^(\d{4}\.\d{4,5}(v\d+)?|[a-z-]+\/\d{7})$/i
const isValidArxivId = computed(() => arxivPattern.test(arxivInput.value.trim()))

function extractArxivId(input: string): string {
  const trimmed = input.trim()
  // Direct arXiv ID
  if (arxivPattern.test(trimmed)) return trimmed
  
  // arXiv URL
  const urlMatch = trimmed.match(/arxiv\.org\/(?:abs|pdf)\/([^/]+)/i)
  if (urlMatch) return urlMatch[1]
  
  return trimmed
}

async function startIdeate() {
  if (!isValidArxivId.value || loading.value) return
  
  const arxivId = extractArxivId(arxivInput.value)
  loading.value = true
  
  try {
    const response = await $fetch<IdeateJobStart>('/api/ideate', {
      method: 'POST',
      headers: { [headerName]: csrf },
      body: { arxiv_id: arxivId }
    })
    
    jobId.value = response.job_id
    emit('started', response.job_id, arxivId)
    
    // Start polling for status
    startPolling(response.job_id)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to start ideation'
    toast.add({
      title: 'Ideation failed',
      description: message,
      icon: 'i-lucide-alert-circle',
      color: 'error'
    })
    emit('error', message)
    loading.value = false
  }
}

async function pollJobStatus(id: string) {
  try {
    const status = await $fetch<IdeateJob>(`/api/ideate/${id}`)
    jobStatus.value = status
    
    if (status.status === 'completed' && status.result) {
      stopPolling()
      loading.value = false
      emit('completed', status.result)
    } else if (status.status === 'failed') {
      stopPolling()
      loading.value = false
      emit('error', status.error || 'Ideation failed')
    }
  } catch (err) {
    stopPolling()
    loading.value = false
    const message = err instanceof Error ? err.message : 'Failed to check status'
    emit('error', message)
  }
}

function startPolling(id: string) {
  pollInterval.value = setInterval(() => pollJobStatus(id), 2000)
}

function stopPolling() {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

function cancel() {
  stopPolling()
  jobId.value = null
  jobStatus.value = null
  loading.value = false
}

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <div class="rounded-[2rem] border border-base-300 bg-base-100/60 p-4 shadow-2xl shadow-neutral/5 backdrop-blur-xl">
    <div class="flex items-center gap-3 mb-3">
      <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <Icon name="lucide:lightbulb" class="h-5 w-5" />
      </div>
      <div>
        <p class="text-sm font-medium">Ideate Mode</p>
        <p class="text-xs text-base-content/55">Transform arXiv papers into product opportunities</p>
      </div>
    </div>

    <form @submit.prevent="startIdeate" class="space-y-3">
      <div class="relative">
        <input
          v-model="arxivInput"
          type="text"
          class="input input-bordered w-full pr-20"
          placeholder="arXiv ID (e.g., 2301.07035) or URL"
          :disabled="loading"
        />
        <button
          type="submit"
          class="btn btn-primary btn-sm absolute right-1 top-1"
          :disabled="!isValidArxivId || loading"
        >
          <span v-if="loading" class="loading loading-spinner loading-xs"></span>
          <span v-else>Start</span>
        </button>
      </div>

      <div v-if="jobStatus" class="rounded-xl border border-base-300/70 bg-base-200/50 p-3">
        <div class="flex items-center justify-between">
          <span class="text-xs text-base-content/60">Status:</span>
          <span class="badge badge-sm" :class="{
            'badge-warning': jobStatus.status === 'queued',
            'badge-primary': jobStatus.status === 'running',
            'badge-success': jobStatus.status === 'completed',
            'badge-error': jobStatus.status === 'failed'
          }">
            {{ jobStatus.status }}
          </span>
        </div>
        
        <div v-if="loading" class="mt-2 flex justify-end">
          <button type="button" class="btn btn-ghost btn-xs" @click="cancel">
            Cancel
          </button>
        </div>
      </div>
    </form>

    <div class="mt-4 flex flex-wrap gap-1.5">
      <span class="text-[10px] uppercase tracking-wide text-base-content/40">Examples:</span>
      <button
        v-for="example in ['2301.07035', '2401.15884', '2312.11805']"
        :key="example"
        type="button"
        class="rounded-full bg-base-200 px-2 py-0.5 text-xs text-base-content/60 hover:bg-base-300"
        @click="arxivInput = example"
      >
        {{ example }}
      </button>
    </div>
  </div>
</template>
