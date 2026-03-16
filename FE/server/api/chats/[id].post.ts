import { db, schema } from 'hub:db'
import { and, eq } from 'drizzle-orm'
import { z } from 'zod'
import { MODELS } from '#shared/utils/models'
import { extractAgnoContent, consumeSseMessages, flushSseMessages, normalizeAgnoMessage } from '#shared/utils/agno'
import { extractTextFromParts, sendChatRequestSchema } from '#shared/utils/chat'
import { getViewerIdentity } from '../../utils/auth'
import { buildChatPrompt, ensureAgnoOk, fetchAgno } from '../../utils/agno'

defineRouteMeta({
    openAPI: {
        description: 'Chat with Forge Research Agent.',
        tags: ['ai']
    }
})

export default defineEventHandler(async (event) => {
    const viewer = await getViewerIdentity(event)
    const { agnoBackendUrl } = useRuntimeConfig()

    const { id } = await getValidatedRouterParams(event, z.object({
        id: z.string()
    }).parse)

    const { messages, model } = await readValidatedBody(event, sendChatRequestSchema.superRefine((body, ctx) => {
        if (!MODELS.some(entry => entry.value === body.model)) {
            ctx.addIssue({
                code: 'custom',
                path: ['model'],
                message: 'Invalid model'
            })
        }
    }).parse)

    const chat = await db.query.chats.findFirst({
        where: () => and(
            eq(schema.chats.id, id as string),
            eq(schema.chats.userId, viewer.id)
        )
    })
    if (!chat) {
        throw createError({ statusCode: 404, statusMessage: 'Chat not found' })
    }

    // Title generation via Agno
    if (!chat.title) {
        try {
            const firstUserMessage = messages.find(message => message.role === 'user')
            const titleSource = firstUserMessage
                ? extractTextFromParts(firstUserMessage.parts)
                : extractTextFromParts(messages[0]!.parts)
            const titleForm = new FormData()
            titleForm.append('message', titleSource || 'New Research')
            titleForm.append('stream', 'false')

            const titleResponse = await fetchAgno(`${agnoBackendUrl}/agents/title-generator/runs`, {
                method: 'POST',
                body: titleForm
            })

            if (titleResponse.ok) {
                const result = await titleResponse.json()
                const title = extractAgnoContent(result)?.trim() || 'New Research'
                await db.update(schema.chats).set({ title }).where(eq(schema.chats.id, id as string))
            }
        } catch (error) {
            console.error('Failed to generate title via Agno:', error)
        }
    }

    const lastMessage = messages[messages.length - 1]
    if (!lastMessage || lastMessage.role !== 'user') {
        throw createError({ statusCode: 400, statusMessage: 'Last message must be from the user' })
    }

    if (lastMessage?.role === 'user') {
        await db.insert(schema.messages).values({
            chatId: id as string,
            role: 'user',
            parts: lastMessage.parts
        })
    }

    // Proxy request to Agno chat-agent (Agno expects multipart/form-data)
    const chatForm = new FormData()
    chatForm.append('message', buildChatPrompt(lastMessage.parts))
    chatForm.append('stream', 'true')
    chatForm.append('user_id', viewer.id)
    chatForm.append('session_id', id as string)
    chatForm.append('mode', chat.mode)
    chatForm.append('model', model)

    const response = await fetchAgno(`${agnoBackendUrl}/agents/chat-agent/runs`, {
        method: 'POST',
        headers: {
            'Accept': 'text/event-stream'
        },
        body: chatForm
    })
    await ensureAgnoOk(response, 'Agno chat backend error')

    // Forward the SSE stream
    setResponseHeader(event, 'Content-Type', 'text/event-stream')
    setResponseHeader(event, 'Cache-Control', 'no-cache')
    setResponseHeader(event, 'Connection', 'keep-alive')

    const reader = response.body?.getReader()
    if (!reader) {
        throw createError({ statusCode: 500, statusMessage: 'No response stream available' })
    }

    return sendStream(event, new ReadableStream({
        async start(controller) {
            const decoder = new TextDecoder()
            const encoder = new TextEncoder()
            let fullContent = ''
            let buffer = ''

            try {
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value, { stream: true })
                    controller.enqueue(value)
                    const parsed = consumeSseMessages(buffer, chunk)
                    buffer = parsed.buffer

                    for (const message of parsed.messages) {
                        const normalized = normalizeAgnoMessage(message)
                        if (normalized.content) {
                            fullContent += normalized.content
                        }
                    }
                }

                for (const message of flushSseMessages(buffer)) {
                    const normalized = normalizeAgnoMessage(message)
                    if (normalized.content) {
                        fullContent += normalized.content
                    }
                }

                // Save assistant message to DB
                if (fullContent) {
                    await db.insert(schema.messages).values({
                        chatId: id as string,
                        role: 'assistant',
                        parts: [{ type: 'text', text: fullContent }]
                    })
                }
            } catch (err) {
                console.error('Streaming error:', err)
                controller.enqueue(encoder.encode(`event: RunError\ndata: ${JSON.stringify({ message: 'Chat stream interrupted' })}\n\n`))
            } finally {
                controller.close()
            }
        }
    }))
})
