import { db, schema } from 'hub:db'
import { and, eq } from 'drizzle-orm'
import { z } from 'zod'
import { MODELS } from '#shared/utils/models'
import { getViewerIdentity } from '../../utils/auth'

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

    const { messages } = await readValidatedBody(event, z.object({
        model: z.string().refine(value => MODELS.some(m => m.value === value), {
            message: 'Invalid model'
        }),
        mode: z.enum(['deep', 'wide']).default('deep'),
        messages: z.array(z.any())
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
            const titleResponse = await fetch(`${agnoBackendUrl}/agents/title-generator/runs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: JSON.stringify(messages[0]),
                    stream: false
                })
            })

            if (titleResponse.ok) {
                const result = await titleResponse.json()
                const title = result.content?.trim() || 'New Research'
                await db.update(schema.chats).set({ title }).where(eq(schema.chats.id, id as string))
            }
        } catch (error) {
            console.error('Failed to generate title via Agno:', error)
        }
    }

    const lastMessage = messages[messages.length - 1]
    if (lastMessage?.role === 'user') {
        await db.insert(schema.messages).values({
            chatId: id as string,
            role: 'user',
            parts: lastMessage.parts || [{ type: 'text', text: lastMessage.content || lastMessage.text }]
        })
    }

    // Proxy request to Agno chat-agent
    const response = await fetch(`${agnoBackendUrl}/agents/chat-agent/runs`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
            message: lastMessage.content || lastMessage.text || JSON.stringify(lastMessage.parts),
            stream: true,
            user_id: viewer.id,
            session_id: id // Use chat ID as session ID for persistence in Agno
        })
    })

    if (!response.ok) {
        const errorText = await response.text()
        throw createError({
            statusCode: response.status,
            statusMessage: `Agno backend error: ${errorText}`
        })
    }

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
            let fullContent = ''

            try {
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value, { stream: true })
                    controller.enqueue(value)

                    // Collect content to save to DB at the end
                    const lines = chunk.split('\n')
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6))
                                if (data.content) fullContent += data.content
                            } catch {
                                // Ignore non-JSON or partial chunks
                            }
                        }
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
            } finally {
                controller.close()
            }
        }
    }))
})
