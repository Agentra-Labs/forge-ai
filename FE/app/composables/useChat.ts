import type { ChatMessage, ChatMode, MessagePart } from '#shared/types/research'
import { consumeSseMessages, flushSseMessages, normalizeBackendMessage } from '#shared/utils/backend'
import { extractFileParts, extractTextFromParts } from '#shared/utils/chat'

function buildUserMessage(text: string, files: MessagePart[] = []): ChatMessage {
  const parts = [{ type: 'text', text } as const, ...files]

  return {
    id: crypto.randomUUID(),
    role: 'user',
    content: text,
    parts,
    createdAt: new Date()
  }
}

function buildAssistantMessage(): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: 'assistant',
    content: '',
    parts: [{ type: 'text', text: '' }],
    createdAt: new Date()
  }
}

interface SendMessageOptions {
  mode?: ChatMode
}

export function useChat(chatId: string, initialMessages: ChatMessage[] = []) {
  const messages = ref<ChatMessage[]>(initialMessages)
  const isStreaming = ref(false)
  const error = ref<string | null>(null)
  const abortController = ref<AbortController | null>(null)

  async function sendMessage(text: string, files: MessagePart[] = [], options: SendMessageOptions = {}) {
    if (isStreaming.value) {
      stop()
    }

    const userMessage = buildUserMessage(text, files)
    const assistantMessage = buildAssistantMessage()

    messages.value.push(userMessage)
    messages.value.push(assistantMessage)

    isStreaming.value = true
    error.value = null
    abortController.value = new AbortController()

    try {
      const { csrf, headerName } = useCsrf()
      const { model } = useModels()

      const response = await fetch(`/api/chats/${chatId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          [headerName]: csrf,
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          messages: messages.value.slice(0, -1),
          model: model.value,
          mode: options.mode || 'deep'
        }),
        signal: abortController.value.signal
      })

      if (!response.ok) {
        throw new Error(await response.text())
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response stream available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          break
        }

        const parsed = consumeSseMessages(buffer, decoder.decode(value, { stream: true }))
        buffer = parsed.buffer

        for (const message of parsed.messages) {
          const normalized = normalizeBackendMessage(message)
          if (normalized.error) {
            throw new Error(normalized.error)
          }

          if (normalized.content) {
            assistantMessage.content = `${assistantMessage.content || ''}${normalized.content}`
            const firstPart = assistantMessage.parts[0]
            if (firstPart?.type === 'text') {
              firstPart.text = assistantMessage.content
            }
          }
        }
      }

      for (const message of flushSseMessages(buffer)) {
        const normalized = normalizeBackendMessage(message)
        if (normalized.error) {
          throw new Error(normalized.error)
        }

        if (normalized.content) {
          assistantMessage.content = `${assistantMessage.content || ''}${normalized.content}`
          const firstPart = assistantMessage.parts[0]
          if (firstPart?.type === 'text') {
            firstPart.text = assistantMessage.content
          }
        }
      }

      await refreshNuxtData('chats')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Chat request failed'

      if ((err as Error)?.name !== 'AbortError') {
        error.value = errorMessage
      }

      if (!assistantMessage.content) {
        messages.value = messages.value.filter(message => message.id !== assistantMessage.id)
      }

      throw err
    } finally {
      isStreaming.value = false
      abortController.value = null
    }
  }

  function stop() {
    abortController.value?.abort()
    abortController.value = null
    isStreaming.value = false
  }

  async function regenerate(options: SendMessageOptions = {}) {
    const lastUserMessage = [...messages.value].reverse().find(message => message.role === 'user')
    if (!lastUserMessage) {
      return
    }

    const index = messages.value.lastIndexOf(lastUserMessage)
    messages.value = messages.value.slice(0, index)

    const text = extractTextFromParts(lastUserMessage.parts)
    const files = extractFileParts(lastUserMessage.parts)
    await sendMessage(text, files, options)
  }

  return {
    messages,
    isStreaming,
    error,
    sendMessage,
    stop,
    regenerate
  }
}
