<script setup lang="ts">
import type { DefineComponent } from 'vue'
import { Chat } from '@ai-sdk/vue'
import { DefaultChatTransport } from 'ai'
import type { UIMessage } from 'ai'
import { useClipboard } from '@vueuse/core'
import { getTextFromMessage } from '@nuxt/ui/utils/ai'
import { useToast } from '~/composables/useToast'
import ProseStreamPre from '../../components/prose/PreStream.vue'

const components = {
  pre: ProseStreamPre as unknown as DefineComponent
}

const route = useRoute()
const toast = useToast()
const clipboard = useClipboard()
const { model } = useModels()
const { mode } = useResearchMode()

function getFileName(url: string): string {
  try {
    const urlObj = new URL(url)
    const pathname = urlObj.pathname
    const filename = pathname.split('/').pop() || 'file'
    return decodeURIComponent(filename)
  } catch {
    return 'file'
  }
}

const {
  dropzoneRef,
  isDragging,
  open,
  files,
  isUploading,
  uploadedFiles,
  removeFile,
  clearFiles
} = useFileUploadWithStatus(route.params.id as string)

const { data } = await useFetch(`/api/chats/${route.params.id}`, {
  cache: 'force-cache'
})
if (!data.value) {
  throw createError({ statusCode: 404, statusMessage: 'Chat not found' })
}

const chatTitle = computed(() => data.value?.title || 'Untitled chat')

const input = ref('')

const { csrf, headerName } = useCsrf()

const chat = new Chat({
  id: data.value.id,
  messages: data.value.messages,
  transport: new DefaultChatTransport({
    api: `/api/chats/${data.value.id}`,
    headers: { [headerName]: csrf },
    body: {
      model: model.value,
      mode: mode.value
    }
  }),
  onData: (dataPart) => {
    if (dataPart.type === 'data-chat-title') {
      refreshNuxtData('chats')
    }
  },
  onError(error) {
    const { message } = typeof error.message === 'string' && error.message[0] === '{' ? JSON.parse(error.message) : error
    toast.add({
      description: message,
      icon: 'i-lucide-alert-circle',
      color: 'error',
      duration: 0
    })
  }
})

const isStreaming = computed(() => (chat.status as string) === 'streaming')

async function handleSubmit(e: Event) {
  e.preventDefault()
  if (input.value.trim() && !isUploading.value) {
    chat.sendMessage({
      text: input.value,
      files: uploadedFiles.value.length > 0 ? uploadedFiles.value : undefined
    })
    input.value = ''
    clearFiles()
  }
}

const copied = ref(false)

function copy(e: MouseEvent, message: UIMessage) {
  clipboard.copy(getTextFromMessage(message))

  copied.value = true

  setTimeout(() => {
    copied.value = false
  }, 2000)
}

onMounted(() => {
  if (data.value?.messages.length === 1) {
    chat.regenerate()
  }
})
</script>

<template>
  <div
    id="chat"
    class="min-h-screen bg-base-100"
  >
    <DashboardNavbar />

    <div class="flex h-[calc(100vh-4rem)] min-h-0 overflow-hidden">
      <div ref="dropzoneRef" class="relative flex min-h-0 flex-1 justify-center">
        <DragDropOverlay :show="isDragging" />

        <div class="mx-auto flex h-full min-h-0 w-full max-w-6xl flex-1 flex-col px-4 sm:px-6 lg:px-10">
          <div class="border-b border-base-300/70 py-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.3em] text-primary/80">Conversation</p>
                <h1 class="mt-2 text-xl font-semibold tracking-tight">
                  {{ chatTitle }}
                </h1>
                <p class="mt-1 text-xs text-base-content/60 sm:text-sm">
                  {{ mode === 'deep'
                    ? 'Deep mode follows evidence chains through papers, methods, and tradeoffs.'
                    : 'Wide mode surveys the landscape quickly across papers, approaches, and competing signals.' }}
                </p>
              </div>
            </div>

          </div>

          <div class="min-h-0 flex-1 overflow-y-auto pt-5 scroll-smooth">
            <div class="mx-auto flex w-full max-w-4xl flex-col gap-5">
                <div
                  v-for="message in chat.messages"
                  :key="message.id"
                  class="flex"
                  :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
                >
                  <div
                    class="flex max-w-[92%] gap-3 sm:max-w-[82%]"
                    :class="message.role === 'user' ? 'flex-row-reverse' : ''"
                  >
                    <div class="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-base-300/70 bg-base-200/90">
                      <Icon
                        :name="message.role === 'user' ? 'lucide:user-round' : 'lucide:bot'"
                        class="h-4 w-4"
                        :class="message.role === 'user' ? 'text-base-content/70' : 'text-primary'"
                      />
                    </div>

                    <div class="min-w-0">
                      <div class="mb-2 flex items-center gap-2 px-1 text-xs uppercase tracking-[0.2em] text-base-content/45">
                        <span>{{ message.role === 'user' ? 'You' : 'Assistant' }}</span>
                        <span v-if="message.role === 'assistant'" class="rounded-full border border-base-300/70 px-2 py-0.5 text-[10px] tracking-[0.16em]">
                          {{ mode === 'deep' ? 'Deep synthesis' : 'Wide scan' }}
                        </span>
                      </div>
                      <div
                        class="rounded-[1.5rem] border px-3.5 py-2.5 shadow-sm"
                        :class="message.role === 'user'
                          ? 'border-primary/12 bg-primary text-primary-content'
                          : 'border-base-300/75 bg-base-100/72 text-base-content'"
                      >
                        <template v-for="(part, index) in message.parts" :key="`${message.id}-${part.type}-${index}${'state' in part ? `-${part.state}` : ''}`">
                          <Reasoning
                            v-if="part.type === 'reasoning'"
                            :text="part.text"
                            :is-streaming="part.state !== 'done'"
                          />
                          <MDCCached
                            v-else-if="part.type === 'text' && message.role === 'assistant'"
                            :value="part.text"
                            :cache-key="`${message.id}-${index}`"
                            :components="components"
                            :parser-options="{ highlight: false }"
                            class="prose prose-sm max-w-none *:first:mt-0 *:last:mb-0"
                          />
                          <p v-else-if="part.type === 'text' && message.role === 'user'" class="whitespace-pre-wrap">
                            {{ part.text }}
                          </p>
                          <ToolWeather
                            v-else-if="part.type === 'tool-weather'"
                            :invocation="(part as WeatherUIToolInvocation)"
                          />
                          <ToolChart
                            v-else-if="part.type === 'tool-chart'"
                            :invocation="(part as ChartUIToolInvocation)"
                          />
                          <FileAvatar
                            v-else-if="part.type === 'file'"
                            :name="getFileName(part.url)"
                            :type="part.mediaType"
                            :preview-url="part.url"
                            class="mt-2 inline-flex"
                          />
                        </template>
                      </div>

                      <div v-if="message.role === 'assistant' && !isStreaming" class="mt-2 flex gap-2 px-1">
                        <button class="btn btn-ghost btn-xs gap-1 rounded-full" @click="copy($event, message)">
                          <Icon :name="copied ? 'lucide:copy-check' : 'lucide:copy'" class="w-3 h-3" />
                          Copy
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="isStreaming && chat.messages[chat.messages.length - 1]?.role === 'user'" class="flex justify-start">
                  <div class="flex max-w-[88%] gap-3 sm:max-w-[80%]">
                    <div class="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-base-300 bg-base-200">
                      <Icon name="lucide:bot" class="w-5 h-5 text-primary" />
                    </div>
                    <div class="rounded-[1.5rem] border border-base-300 bg-base-100/72 px-3.5 py-2.5 text-base-content shadow-sm">
                      <span class="loading loading-dots loading-sm"></span>
                    </div>
                  </div>
                </div>
            </div>
          </div>

          <div class="sticky bottom-0 mt-auto bg-gradient-to-t from-base-100 via-base-100 to-transparent px-1 pb-[calc(env(safe-area-inset-bottom)+0.75rem)] pt-5 sm:px-2">
            <form @submit.prevent="handleSubmit" class="mx-auto max-w-5xl rounded-[1.75rem] border border-base-300/75 bg-base-200/82 p-3 shadow-xl shadow-neutral/10 backdrop-blur transition-all focus-within:border-primary/30 focus-within:ring-4 focus-within:ring-primary/10">
              <div v-if="files.length > 0" class="mb-2 flex flex-wrap gap-2 rounded-box bg-base-100/72 p-2">
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

              <!-- Error display -->
              <div v-if="chat.error" class="text-error text-sm mb-2 px-2">
                An error occurred. Please try again.
              </div>

              <input
                v-model="input"
                type="text"
                class="input input-ghost w-full bg-transparent px-1 text-base focus:outline-none focus:bg-transparent placeholder:text-base-content/40"
                :placeholder="mode === 'deep'
                  ? 'Ask for stronger evidence, edge cases, or direct paper comparisons...'
                  : 'Ask for broader coverage, more papers, or alternate solution families...'"
                :disabled="isUploading"
              />

              <div class="mt-3 flex items-center justify-between border-t border-base-300/60 pt-3">
                <div class="flex items-center gap-2">
                  <FileUploadButton :open="open" />
                  <ModelSelect />
                </div>

                <div class="flex gap-2">
                  <ResearchModeMenu />
                  <button 
                    v-if="isStreaming"
                    type="button" 
                    class="btn btn-neutral btn-sm h-9 min-h-9 rounded-full px-3.5"
                    @click="chat.stop()"
                  >
                    <Icon name="lucide:square" class="w-4 h-4 fill-current" />
                    <span>Stop</span>
                  </button>
                  <button 
                    v-else-if="chat.messages.length > 0 && !input"
                    type="button" 
                    class="btn btn-ghost btn-sm h-9 min-h-9 rounded-full px-3.5"
                    @click="chat.regenerate()"
                    title="Regenerate"
                  >
                    <Icon name="lucide:rotate-cw" class="w-4 h-4" />
                    <span>Retry</span>
                  </button>
                  <button 
                    v-else
                    type="submit" 
                    class="btn btn-primary btn-sm h-9 min-h-9 rounded-full px-4"
                    :disabled="isUploading || isStreaming || !input.trim()"
                  >
                    <span v-if="isUploading" class="loading loading-spinner loading-xs"></span>
                    <template v-else>
                      <span>Send</span>
                      <Icon name="lucide:arrow-up" class="w-4 h-4" />
                    </template>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
