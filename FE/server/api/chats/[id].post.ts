import { db, schema } from '../../utils/db'
import { and, eq } from 'drizzle-orm'
import { z } from 'zod'
import { MODELS } from '#shared/utils/models'
import { consumeSseMessages, flushSseMessages, normalizeBackendMessage } from '#shared/utils/backend'
import { extractTextFromParts, sendChatRequestSchema } from '#shared/utils/chat'
import { getViewerIdentity } from '../../utils/auth'
import { buildChatPrompt, ensureBackendOk, fetchBackend } from '../../utils/backend'

defineRouteMeta({
    openAPI: {
        description: 'Chat with Forge Research Agent.',
        tags: ['ai']
    }
})

export default defineEventHandler(async (event) => {
    const viewer = await getViewerIdentity(event)
    const { backendUrl } = useRuntimeConfig()

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

    // Title generation via backend
    if (!chat.title) {
        try {
            const firstUserMessage = messages.find(message => message.role === 'user')
            const titleSource = firstUserMessage
                ? extractTextFromParts(firstUserMessage.parts)
                : extractTextFromParts(messages[0]!.parts)

            const titleResponse = await fetchBackend(`${backendUrl}/research/title`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: titleSource || 'New Research' })
            })

            if (titleResponse.ok) {
                const result = await titleResponse.json()
                const title = result.title?.trim() || 'New Research'
                await db.update(schema.chats).set({ title }).where(eq(schema.chats.id, id as string))
            }
        } catch (error) {
            console.error('Failed to generate title:', error)
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

    // Proxy request to backend /research/chat (JSON body, SSE response)
    const response = await fetchBackend(`${backendUrl}/research/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
            message: buildChatPrompt(lastMessage.parts),
            stream: true
        })
    })
    await ensureBackendOk(response, 'Chat backend error')

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
                        const normalized = normalizeBackendMessage(message)
                        if (normalized.content) {
                            fullContent += normalized.content
                        }
                    }
                }

                for (const message of flushSseMessages(buffer)) {
                    const normalized = normalizeBackendMessage(message)
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
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: 'Chat stream interrupted' })}\n\n`))
            } finally {
                controller.close()
            }
        }
    }))
})
