/**
 * Nitro server route: POST /api/research/run
 *
 * Proxies research requests to the Agno backend (FastAPI/AgentOS) and
 * streams SSE events back to the Vue client.
 */
import { z } from 'zod'
import { getViewerIdentity } from '../../utils/auth'

defineRouteMeta({
    openAPI: {
        description: 'Run a research agent or workflow via the agno backend.',
        tags: ['research']
    }
})

export default defineEventHandler(async (event) => {
    const viewer = await getViewerIdentity(event)

    const { agnoBackendUrl } = useRuntimeConfig()

    const body = await readValidatedBody(event, z.object({
        goal: z.string().min(1),
        mode: z.enum(['deep', 'wide', 'builder']).default('deep'),
        primary_url: z.string().optional(),
        secondary_url: z.string().optional(),
        seed_arxiv_id: z.string().optional(),
        keywords: z.array(z.string()).optional(),
        workflow: z.string().optional()
    }).parse)

    // Determine which agno endpoint to hit
    let endpoint: string
    const payload: Record<string, unknown> = { stream: true }

    if (body.workflow) {
        endpoint = `${agnoBackendUrl}/workflows/${body.workflow}/runs`
        payload.message = body.goal
    } else if (body.mode === 'builder') {
        // Workflow Builder — dynamically analyses scenario and spawns the right pipeline
        endpoint = `${agnoBackendUrl}/agents/workflow-builder/runs`
        payload.message = buildResearchPrompt(body)
    } else if (body.mode === 'wide') {
        endpoint = `${agnoBackendUrl}/agents/wide-researcher/runs`
        payload.message = buildResearchPrompt(body)
    } else if (body.mode === 'deep') {
        endpoint = `${agnoBackendUrl}/agents/deep-researcher/runs`
        payload.message = buildResearchPrompt(body)
    }

    // Add user context
    if (viewer.isSignedIn) {
        payload.user_id = viewer.id
    }

    // Proxy SSE stream from agno backend to the Vue client
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify(payload)
    })

    if (!response.ok) {
        const errorText = await response.text()
        throw createError({
            statusCode: response.status,
            statusMessage: `Agno backend error: ${errorText}`
        })
    }

    // Forward the SSE stream directly
    setResponseHeader(event, 'Content-Type', 'text/event-stream')
    setResponseHeader(event, 'Cache-Control', 'no-cache')
    setResponseHeader(event, 'Connection', 'keep-alive')

    if (response.body) {
        return sendStream(event, response.body as any)
    }

    return ''
})

/**
 * Build a rich research prompt from the request body.
 */
function buildResearchPrompt(body: {
    goal: string
    primary_url?: string
    secondary_url?: string
    seed_arxiv_id?: string
    keywords?: string[]
}): string {
    const parts = [`Research Goal: ${body.goal}`]

    if (body.primary_url) {
        parts.push(`Primary Source URL: ${body.primary_url}`)
    }
    if (body.secondary_url) {
        parts.push(`Secondary Source URL: ${body.secondary_url}`)
    }
    if (body.seed_arxiv_id) {
        parts.push(`Seed ArXiv Paper: ${body.seed_arxiv_id}`)
    }
    if (body.keywords?.length) {
        parts.push(`Keywords: ${body.keywords.join(', ')}`)
    }

    return parts.join('\n')
}
