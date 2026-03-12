import type { ChatMessage, MessagePart } from '#shared/types/research'

export function useChat(chatId: string, initialMessages: any[] = []) {
    const messages = ref<ChatMessage[]>(initialMessages)
    const isStreaming = ref(false)
    const error = ref<string | null>(null)
    const abortController = ref<AbortController | null>(null)

    async function sendMessage(text: string, files: any[] = []) {
        const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'user',
            content: text,
            parts: [{ type: 'text', text }],
            createdAt: new Date()
        }
        messages.value.push(userMessage)

        isStreaming.value = true
        error.value = null
        abortController.value = new AbortController()

        const assistantMessage: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: '',
            parts: [{ type: 'text', text: '' }],
            createdAt: new Date()
        }
        messages.value.push(assistantMessage)

        try {
            const { csrf, headerName } = useCsrf()
            const { model } = useModels()
            const { mode } = useResearchMode()

            const response = await fetch(`/api/chats/${chatId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    [headerName]: csrf,
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify({
                    messages: messages.value.slice(0, -1), // Send all but the empty assistant message
                    model: model.value,
                    mode: mode.value
                }),
                signal: abortController.value.signal
            })

            if (!response.ok) {
                const errText = await response.text()
                throw new Error(errText)
            }

            const reader = response.body?.getReader()
            if (!reader) throw new Error('No reader')
            console.log('Reader created, starting to read stream...')

            const decoder = new TextDecoder()
            let buffer = ''
            let chunksReceived = 0

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                chunksReceived++
                const decoded = decoder.decode(value, { stream: true })
                buffer += decoded
                console.log('Chunk', chunksReceived, ':', decoded.substring(0, 100))
                const lines = buffer.split('\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6))
                            console.log('Parsed data:', data)
                            if (data.content) {
                                assistantMessage.content += data.content
                                assistantMessage.parts[0].text = assistantMessage.content
                            }
                        } catch {
                            // Ignore partial JSON
                        }
                    }
                }
            }
            console.log('Stream complete. Chunks:', chunksReceived, 'Content length:', assistantMessage.content.length)
        } catch (err: any) {
            console.error('Chat error:', err)
            if (err.name !== 'AbortError') {
                error.value = err.message
                messages.value.pop() // Remove failed assistant message
            }
        } finally {
            isStreaming.value = false
        }
    }

    function stop() {
        abortController.value?.abort()
        isStreaming.value = false
    }

    function regenerate() {
        const lastUserMessage = [...messages.value].reverse().find(m => m.role === 'user')
        if (lastUserMessage) {
            // Remove messages after last user message
            const index = messages.value.lastIndexOf(lastUserMessage)
            messages.value = messages.value.slice(0, index + 1)
            sendMessage(lastUserMessage.content || lastUserMessage.parts?.[0]?.text || '')
        }
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
