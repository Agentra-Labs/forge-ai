<script setup lang="ts">
const input = ref('')
const loading = ref(false)
const chatId = crypto.randomUUID()

const { mode } = useResearchMode()

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

const modeLabel = computed(() => {
  if (mode.value === 'wide') {
    return 'Wide Research'
  }

  if (mode.value === 'deep') {
    return 'Deep Research'
  }

  return 'Research'
})

async function createChat(prompt: string) {
  input.value = prompt
  loading.value = true

  const parts: Array<{ type: string, text?: string, mediaType?: string, url?: string }> = [{ type: 'text', text: prompt }]

  if (uploadedFiles.value.length > 0) {
    parts.push(...uploadedFiles.value)
  }

  const chat = await $fetch('/api/chats', {
    method: 'POST',
    headers: { [headerName]: csrf },
    body: {
      id: chatId,
      mode: mode.value,
      message: {
        role: 'user',
        parts
      }
    }
  })

  refreshNuxtData('chats')
  navigateTo(`/chat/${chat?.id}`)
}

async function onSubmit() {
  await createChat(input.value)
  clearFiles()
}

const quickChats = [
  {
    label: 'Find the strongest paper-backed approach for browser agents',
    icon: 'lucide:scan-search'
  },
  {
    label: 'Compare retrieval strategies across recent agent papers',
    icon: 'lucide:network'
  },
  {
    label: 'Map the leading solutions for hallucination reduction',
    icon: 'lucide:git-branch-plus'
  },
  {
    label: 'Summarize evidence for tool-use planning architectures',
    icon: 'lucide:book-open'
  },
  {
    label: 'Which benchmarks best measure deep research quality?',
    icon: 'lucide:line-chart'
  },
  {
    label: 'Wide scan of state-of-the-art research copilots',
    icon: 'lucide:telescope'
  }
]
</script>

<template>
  <div
    id="home"
    class="min-h-screen bg-base-100"
  >
    <DashboardNavbar />

    <div class="flex min-h-[calc(100vh-4rem)] flex-1 overflow-hidden">
      <div ref="dropzoneRef" class="relative flex flex-1 justify-center">
        <DragDropOverlay :show="isDragging" />

        <div class="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6 lg:px-10">
          <div class="grid gap-8 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,0.9fr)] lg:items-start">
            <div class="flex flex-col justify-center gap-6">
              <div class="text-center lg:text-left">
                <h1 class="font-display flex items-center justify-center gap-3 text-3xl font-medium tracking-tight text-base-content sm:text-4xl lg:justify-start">
                  <Icon name="lucide:sparkles" class="h-7 w-7 text-primary" />
                  Time to Forge ahead?
                </h1>
              </div>

              <div class="mx-auto w-full max-w-3xl lg:mx-0">
                <form @submit.prevent="onSubmit" class="rounded-[1.75rem] border border-base-300/70 bg-base-200/50 p-3 pb-2 shadow-xl backdrop-blur-md transition-all hover:bg-base-200/70 hover:border-base-300/90 focus-within:bg-base-200/80 focus-within:border-primary/30 focus-within:ring-4 focus-within:ring-primary/10">
                  <div v-if="files.length > 0" class="mb-2 flex flex-wrap gap-2 rounded-box bg-base-200/80 p-2">
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

                <div class="mx-auto mt-4 flex max-w-[42rem] flex-wrap justify-center gap-2 lg:justify-start">
                  <button
                    v-for="quickChat in quickChats"
                    :key="quickChat.label"
                    class="btn btn-outline btn-sm h-9 rounded-full border-base-300/60 text-xs font-normal text-base-content/75 hover:border-base-300 hover:bg-base-200"
                    @click="createChat(quickChat.label)"
                  >
                    <Icon :name="quickChat.icon" class="h-3.5 w-3.5" />
                    {{ quickChat.label }}
                  </button>
                </div>
              </div>
            </div>

            <div class="hidden lg:block">
              <DashboardSidebar :mode-label="modeLabel" />
            </div>
          </div>

          <div class="block lg:hidden">
            <DashboardSidebar :mode-label="modeLabel" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
