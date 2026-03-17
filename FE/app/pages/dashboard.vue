<script setup lang="ts">
import type { PipelinePhase, IdeateJob } from '#shared/types/research'

const toast = useToast()
const input = ref('')
const loading = ref(false)
const chatId = crypto.randomUUID()

const { mode, currentModeInfo, isIdeateMode, isResearchMode } = useResearchMode()
const { mode: chatMode } = useResearchMode()

const {
  dropzoneRef,
  isDragging,
  open,
  files,
  isUploading,
  uploadedFiles,
  removeFile,
  clearFiles
} = useFileUploadWithStatus(chatId)

const { csrf, headerName } = useCsrf()

// Ideate state
const ideateJobId = ref<string | null>(null)
const ideateArxivId = ref<string | null>(null)
const ideateResult = ref<string | null>(null)
const ideateLoading = ref(false)

// Pipeline visualization
const pipelinePhases = ref<PipelinePhase[]>([])
const pipelineStartTime = ref<number | null>(null)

const modeLabel = computed(() => currentModeInfo.value.label)
const modeIcon = computed(() => currentModeInfo.value.icon)

// Dynamic pipeline phases based on mode
const defaultPhases = computed<PipelinePhase[]>(() => {
  if (isIdeateMode.value) {
    return [
      { id: 'decompose', name: 'Decomposer', description: 'Extract technical primitives', status: 'pending' },
      { id: 'pain', name: 'Pain Scanner', description: 'Map market pain points', status: 'pending' },
      { id: 'infra', name: 'Infra Inversion', description: 'Second-order opportunities', status: 'pending' },
      { id: 'temporal', name: 'Temporal Arbitrage', description: 'Timing windows', status: 'pending' },
      { id: 'crosspoll', name: 'Cross-Pollinator', description: 'Cross-domain ideas', status: 'pending' },
      { id: 'destroyer', name: 'Destroyer', description: 'Red team critique', status: 'pending' },
      { id: 'synthesize', name: 'Synthesizer', description: 'Final ranked report', status: 'pending' }
    ]
  }
  
  if (mode.value === 'wide') {
    return [
      { id: 'search', name: 'Paper Search', description: 'Query OpenAlex', status: 'pending' },
      { id: 'citation', name: 'Citation Walk', description: 'Forward/backward citations', status: 'pending' },
      { id: 'cluster', name: 'Cluster', description: 'Technique clustering', status: 'pending' },
      { id: 'rank', name: 'Rank', description: 'Prioritize candidates', status: 'pending' }
    ]
  }
  
  if (mode.value === 'read') {
    return [
      { id: 'pass1', name: 'Pass 1: Skim', description: 'Title, abstract, figures', status: 'pending' },
      { id: 'pass2', name: 'Pass 2: Structure', description: 'Claims, baselines, results', status: 'pending' },
      { id: 'pass3', name: 'Pass 3: Critique', description: 'Deep methodology review', status: 'pending' }
    ]
  }
  
  // Deep mode default
  return [
    { id: 'extract', name: 'Extract Problem', description: 'Understand core question', status: 'pending' },
    { id: 'search', name: 'Search Papers', description: 'Find relevant literature', status: 'pending' },
    { id: 'analyze', name: 'Analyze Methods', description: 'Extract techniques & results', status: 'pending' },
    { id: 'synthesize', name: 'Synthesize', description: 'Tradeoffs & recommendations', status: 'pending' }
  ]
})

// Reset pipeline when mode changes
watch(mode, () => {
  pipelinePhases.value = defaultPhases.value.map(p => ({ ...p, status: 'pending' as const }))
})

// Initialize pipeline
pipelinePhases.value = defaultPhases.value

async function createChat(prompt: string) {
  input.value = prompt
  loading.value = true
  pipelineStartTime.value = Date.now()
  
  // Start first phase
  if (pipelinePhases.value.length > 0) {
    pipelinePhases.value[0].status = 'running'
  }

  try {
    const parts: Array<{ type: string, text?: string, mediaType?: string, url?: string }> = [{ type: 'text', text: prompt }]

    if (uploadedFiles.value.length > 0) {
      parts.push(...uploadedFiles.value)
    }

    const chat = await $fetch('/api/chats', {
      method: 'POST',
      headers: { [headerName]: csrf },
      body: {
        id: chatId,
        mode: isIdeateMode.value ? 'deep' : mode.value,
        message: {
          role: 'user',
          parts
        }
      }
    })
    
    // Mark first phase complete on success
    if (pipelinePhases.value.length > 0) {
      pipelinePhases.value[0].status = 'completed'
      pipelinePhases.value[0].duration = Date.now() - (pipelineStartTime.value || Date.now())
    }

    clearFiles()
    await refreshNuxtData('chats')
    await navigateTo(`/chat/${chat?.id}`)
  } catch (error) {
    // Mark first phase failed
    if (pipelinePhases.value.length > 0) {
      pipelinePhases.value[0].status = 'failed'
    }
    
    toast.add({
      title: 'Unable to start chat',
      description: error instanceof Error ? error.message : 'Please try again.',
      icon: 'i-lucide-alert-circle',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  if (isIdeateMode.value) {
    // Ideate mode is handled by IdeateForm component
    return
  }
  await createChat(input.value)
}

function handleIdeateStarted(jobId: string, arxivId: string) {
  ideateJobId.value = jobId
  ideateArxivId.value = arxivId
  ideateLoading.value = true
  pipelineStartTime.value = Date.now()
  
  // Start pipeline visualization
  if (pipelinePhases.value.length > 0) {
    pipelinePhases.value[0].status = 'running'
  }
}

function handleIdeateCompleted(result: string) {
  ideateResult.value = result
  ideateLoading.value = false
  
  // Mark all phases complete
  pipelinePhases.value.forEach(p => {
    p.status = 'completed'
    p.duration = Date.now() - (pipelineStartTime.value || Date.now())
  })
  
  toast.add({
    title: 'Ideation complete',
    description: 'Product opportunities have been generated.',
    icon: 'i-lucide-check-circle',
    color: 'success'
  })
  
  // Navigate to chat with result
  navigateTo(`/chat/${chatId}`)
}

function handleIdeateError(message: string) {
  ideateLoading.value = false
  
  // Mark running phase as failed
  const runningPhase = pipelinePhases.value.find(p => p.status === 'running')
  if (runningPhase) {
    runningPhase.status = 'failed'
  }
  
  toast.add({
    title: 'Ideation failed',
    description: message,
    icon: 'i-lucide-alert-circle',
    color: 'error'
  })
}

const quickChats = [
  {
    label: 'Find the strongest paper-backed approach for browser agents',
    icon: 'lucide:scan-search',
    mode: 'deep' as const
  },
  {
    label: 'Compare retrieval strategies across recent agent papers',
    icon: 'lucide:network',
    mode: 'wide' as const
  },
  {
    label: 'Map the leading solutions for hallucination reduction',
    icon: 'lucide:git-branch-plus',
    mode: 'wide' as const
  },
  {
    label: '3-pass review of transformer efficiency methods',
    icon: 'lucide:book-open',
    mode: 'read' as const
  },
  {
    label: 'Which benchmarks best measure deep research quality?',
    icon: 'lucide:line-chart',
    mode: 'deep' as const
  },
  {
    label: 'Wide scan of state-of-the-art research copilots',
    icon: 'lucide:telescope',
    mode: 'wide' as const
  }
]
</script>

<template>
  <div id="home" class="min-h-screen bg-base-100">
    <DashboardNavbar />

    <div class="flex min-h-[calc(100vh-4rem)] flex-1 overflow-hidden">
      <div ref="dropzoneRef" class="relative flex flex-1 justify-center">
        <DragDropOverlay :show="isDragging" />

        <div class="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6 lg:px-10">
          <div class="grid gap-8 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,0.9fr)] lg:items-start">
            
            <!-- Main Content -->
            <div class="flex flex-col justify-center gap-6">
              <!-- Header -->
              <div class="text-center lg:text-left">
                <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                  <Icon name="lucide:sparkles" class="h-3.5 w-3.5" />
                  <span>Agentica Powered</span>
                </div>
                <h1 class="font-display text-4xl font-bold tracking-tight text-base-content sm:text-5xl lg:justify-start">
                  {{ isIdeateMode ? 'Forge Ideate' : 'Forge Research' }}
                </h1>
                <p class="mt-4 max-w-xl text-base leading-relaxed text-base-content/70 mx-auto lg:mx-0">
                  {{ isIdeateMode 
                    ? 'Drop an arXiv paper. The agent will extract primitives, map market pain, and generate product opportunities.' 
                    : 'Drop a seed paper or type a research goal. The agent will read, synthesize, and evaluate literature to accelerate your decisions.' 
                  }}
                </p>
              </div>

              <!-- Ideate Form or Research Form -->
              <div class="mx-auto w-full max-w-3xl lg:mx-0">
                <!-- Ideate Mode -->
                <IdeateForm 
                  v-if="isIdeateMode"
                  :chat-id="chatId"
                  @started="handleIdeateStarted"
                  @completed="handleIdeateCompleted"
                  @error="handleIdeateError"
                />

                <!-- Research Mode -->
                <form v-else @submit.prevent="onSubmit" class="rounded-[2rem] border border-base-300 bg-base-100/60 p-3 shadow-2xl shadow-neutral/5 backdrop-blur-xl transition-all focus-within:border-primary/40 focus-within:bg-base-100/90 focus-within:ring-4 focus-within:ring-primary/10">
                  <div v-if="files.length > 0" class="mb-2 flex flex-wrap gap-2 rounded-2xl bg-base-200/60 p-2">
                    <FileAvatar
                      v-for="fileWithStatus in files"
                      :key="fileWithStatus.id"
                      :name="fileWithStatus.file.name"
                      :type="fileWithStatus.file.type"
                      :preview-url="fileWithStatus.previewUrl"
                      :status="fileWithStatus.status"
                      :error="fileWithStatus.error"
                      removable
                      @remove="removeFile(fileWithStatus.id)"
                    />
                  </div>

                  <textarea
                    v-model="input"
                    class="textarea textarea-ghost min-h-[5rem] w-full resize-none bg-transparent px-2 text-base leading-7 focus:outline-none placeholder:text-base-content/40 sm:text-[1.05rem]"
                    placeholder="How can I help you research today?"
                    :disabled="isUploading || loading"
                  />

                  <div class="mt-2 flex flex-wrap items-center justify-between gap-3 pt-1">
                    <div class="flex items-center gap-1 pl-1 text-base-content/70">
                      <FileUploadButton :open="open" />
                    </div>

                    <div class="flex items-center gap-1.5 pr-1">
                      <ModelSelect />
                      <ResearchModeMenu />
                      <button
                        type="submit"
                        class="btn btn-primary btn-circle btn-sm ml-1.5 p-0"
                        :disabled="isUploading || loading || !input.trim()"
                      >
                        <span v-if="loading || isUploading" class="loading loading-spinner loading-xs"></span>
                        <Icon v-else name="lucide:arrow-right" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </form>

                <!-- Quick Chat Prompts -->
                <div class="mx-auto mt-6 flex max-w-[42rem] flex-wrap justify-center gap-2.5 lg:justify-start">
                  <button
                    v-for="quickChat in quickChats"
                    :key="quickChat.label"
                    class="group flex items-center gap-2 rounded-full border border-base-300 bg-base-100 px-4 py-2 text-sm text-base-content/75 transition-all hover:border-primary/30 hover:bg-primary/5 hover:text-base-content"
                    @click="mode = quickChat.mode; createChat(quickChat.label)"
                  >
                    <Icon :name="quickChat.icon" class="h-4 w-4 text-base-content/40 group-hover:text-primary transition-colors" />
                    {{ quickChat.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Sidebar: Pipeline Progress -->
            <div class="hidden lg:block">
              <PipelineProgress 
                :phases="pipelinePhases"
                :compact="false"
              />
            </div>
          </div>

          <!-- Mobile Sidebar -->
          <div class="block lg:hidden">
            <PipelineProgress 
              :phases="pipelinePhases"
              :compact="true"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
