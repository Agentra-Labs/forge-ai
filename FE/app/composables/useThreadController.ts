import type { Ref } from 'vue'
import type { ChatMessage, ChatMode, MessagePart } from '#shared/types/research'
import { extractTextFromParts } from '#shared/utils/chat'

interface SubmitThreadInput {
  text: string
  files?: MessagePart[]
}

interface UseThreadControllerOptions {
  chatId: string
  initialMessages: ChatMessage[]
  mode: Ref<ChatMode>
  onError?: (message: string) => void
}

export function useThreadController(options: UseThreadControllerOptions) {
  const chat = useChat(options.chatId, options.initialMessages)
  const research = useResearch({
    onError: (message) => {
      options.onError?.(message)
    }
  })

  const messages = computed(() => chat.messages.value)
  const isStreaming = computed(() => chat.isStreaming.value)
  const isBusy = computed(() => chat.isStreaming.value || research.isRunning.value)
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value.at(-1))
  const lastUserMessage = computed(() => [...messages.value].reverse().find(message => message.role === 'user'))
  const error = computed(() => chat.error.value || research.error.value)

  function reportError(error: unknown, fallback: string) {
    if ((error as Error)?.name === 'AbortError') {
      return
    }

    const message = error instanceof Error ? error.message : fallback
    options.onError?.(message)
  }

  function runResearch(goal: string) {
    return research.run({
      goal,
      mode: options.mode.value
    })
  }

  async function submit(input: SubmitThreadInput) {
    const text = input.text.trim()
    if (!text || isBusy.value) {
      return false
    }

    try {
      void runResearch(text)
      await chat.sendMessage(text, input.files || [], {
        mode: options.mode.value
      })
      return true
    } catch (error) {
      reportError(error, 'Message failed')
      return false
    }
  }

  async function retry() {
    if (isBusy.value || !lastUserMessage.value) {
      return false
    }

    const text = extractTextFromParts(lastUserMessage.value.parts)
    try {
      void runResearch(text)
      await chat.regenerate({
        mode: options.mode.value
      })
      return true
    } catch (error) {
      reportError(error, 'Retry failed')
      return false
    }
  }

  function stop() {
    chat.stop()
    research.stop()
  }

  onBeforeUnmount(() => {
    stop()
  })

  return {
    messages,
    lastMessage,
    lastUserMessage,
    hasMessages,
    isBusy,
    isStreaming,
    error,
    chatError: readonly(chat.error),
    researchError: readonly(research.error),
    researchSteps: research.steps,
    researchCurrentStep: research.currentStep,
    researchContent: research.content,
    researchRunning: research.isRunning,
    submit,
    retry,
    stop
  }
}
