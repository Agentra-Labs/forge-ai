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

        <div class="mx-auto flex w-full max-w-5xl flex-1 flex-col justify-center gap-6 px-4 py-8 sm:px-6 lg:px-10">
          <div class="space-y-4 text-center">
            <p class="text-sm font-medium uppercase tracking-[0.35em] text-primary/80">
              Forge Deep Research
            </p>
            <h1 class="mx-auto max-w-4xl text-3xl font-semibold tracking-tight sm:text-5xl">
              Research papers into concrete answers.
            </h1>
            <p class="mx-auto max-w-3xl text-sm text-base-content/62 sm:text-base">
              Switch between deep and wide research, gather evidence from papers, and turn synthesis into action.
            </p>
          </div>

          <div class="mx-auto w-full max-w-4xl space-y-3 rounded-[1.75rem] border border-base-300/70 bg-base-200/62 p-3 shadow-2xl shadow-neutral/10 backdrop-blur">
            <form @submit.prevent="onSubmit" class="rounded-[1.5rem] border border-base-300/80 bg-base-100/72 p-3 transition-all focus-within:border-primary/30 focus-within:ring-4 focus-within:ring-primary/10">
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
                class="textarea textarea-ghost min-h-28 w-full resize-none bg-transparent px-1 text-base leading-7 focus:outline-none placeholder:text-base-content/40 sm:text-[1.1rem]"
                :placeholder="mode === 'deep'
                  ? 'Ask a focused research question and I will dig through papers for a defensible answer...'
                  : 'Ask for a broad landscape scan and I will map the strongest directions across papers...'"
                :disabled="isUploading || loading"
              />

              <div class="mt-3 flex flex-wrap items-center justify-between gap-3 border-t border-base-300/60 pt-3">
                <div class="flex items-center gap-2">
                  <FileUploadButton :open="open" />
                  <ModelSelect />
                </div>

                <div class="flex items-center gap-2">
                  <ResearchModeMenu />
                  <button
                    type="submit"
                    class="btn btn-primary btn-sm h-9 min-h-9 rounded-full px-4"
                    :disabled="isUploading || loading || !input.trim()"
                  >
                    <span v-if="loading || isUploading" class="loading loading-spinner loading-xs"></span>
                    <template v-else>
                      <span>Research</span>
                      <Icon name="lucide:arrow-up" class="w-4 h-4" />
                    </template>
                  </button>
                </div>
              </div>
            </form>
          </div>

          <div class="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-3">
            <button
              v-for="quickChat in quickChats"
              :key="quickChat.label"
              class="flex items-center gap-3 rounded-[1.25rem] border border-base-300/70 bg-base-100/58 px-3.5 py-3 text-left transition-all hover:-translate-y-0.5 hover:border-primary/25 hover:bg-base-100/82"
              @click="createChat(quickChat.label)"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-base-200/90">
                <Icon :name="quickChat.icon.replace('i-', '').replace('-', ':')" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-[13px] font-medium text-base-content">{{ quickChat.label }}</p>
                <p class="text-xs text-base-content/55">Use as a starting point</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
