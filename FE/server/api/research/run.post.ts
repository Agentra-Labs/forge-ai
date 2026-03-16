/**
 * Nitro server route: POST /api/research/run
 *
 * Proxies research requests to the Agno backend (FastAPI/AgentOS) and
 * streams SSE events back to the Vue client.
 */
import { z } from 'zod'
import { RESEARCH_WORKFLOW_IDS } from '#shared/utils/chat'
import { getViewerIdentity } from '../../utils/auth'
import { buildResearchPrompt, ensureAgnoOk, fetchAgno } from '../../utils/agno'

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
        workflow: z.enum(RESEARCH_WORKFLOW_IDS).optional()
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
    } else {
        throw createError({
            statusCode: 400,
            statusMessage: 'Unsupported research mode'
        })
    }

    // Add user context
    if (viewer.isSignedIn) {
        payload.user_id = viewer.id
    }

    // Agno expects multipart/form-data for agents, but x-www-form-urlencoded for workflows
    const isWorkflow = body.workflow !== undefined
    const form = isWorkflow ? new URLSearchParams() : new FormData()

    for (const [key, value] of Object.entries(payload)) {
        if (value !== undefined && value !== null) {
            form.append(key, String(value))
        }
    }

    // Proxy SSE stream from agno backend to the Vue client
    const response = await fetchAgno(endpoint, {
        method: 'POST',
        headers: {
            'Accept': 'text/event-stream'
        },
        body: form
    })
    await ensureAgnoOk(response, 'Agno research backend error')

    // Forward the SSE stream directly
    setResponseHeader(event, 'Content-Type', 'text/event-stream')
    setResponseHeader(event, 'Cache-Control', 'no-cache')
    setResponseHeader(event, 'Connection', 'keep-alive')

    if (response.body) {
        return sendStream(event, response.body as any)
    }

    return ''
})
