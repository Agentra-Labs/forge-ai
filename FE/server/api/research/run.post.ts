/**
 * Nitro server route: POST /api/research/run
 *
 * Proxies research requests to the nova-forge backend and
 * streams SSE events back to the Vue client.
 *
 * Backend endpoints:
 *   POST /research/wide   — Wide Researcher (breadth-first scan)
 *   POST /research/deep   — Deep Researcher (depth-first analysis)
 *   POST /research/read   — Paper Reader (3-pass methodology)
 *   POST /research/plan   — Workflow Builder (returns plan, optionally executes)
 *   POST /research/run    — Run a full workflow (chained or literature review)
 */
import { z } from 'zod'
import { RESEARCH_WORKFLOW_IDS } from '#shared/utils/chat'
import { getViewerIdentity } from '../../utils/auth'
import { buildResearchPrompt, ensureBackendOk, fetchBackend } from '../../utils/backend'

defineRouteMeta({
    openAPI: {
        description: 'Run a research agent or workflow via the nova-forge backend.',
        tags: ['research']
    }
})

export default defineEventHandler(async (event) => {
    const viewer = await getViewerIdentity(event)
    const { backendUrl } = useRuntimeConfig()

    const body = await readValidatedBody(event, z.object({
        goal: z.string().min(1),
        mode: z.enum(['deep', 'wide', 'builder', 'read']).default('deep'),
        primary_url: z.string().optional(),
        secondary_url: z.string().optional(),
        seed_arxiv_id: z.string().optional(),
        keywords: z.array(z.string()).optional(),
        workflow: z.enum(RESEARCH_WORKFLOW_IDS).optional(),
        execute: z.boolean().optional() // for builder mode
    }).parse)

    // Determine which backend endpoint to hit
    let endpoint: string
    const payload: Record<string, unknown> = { stream: true }

    if (body.workflow) {
        // Full workflow run: chained or literature review
        endpoint = `${backendUrl}/research/run`
        payload.goal = body.goal
        payload.workflow = body.workflow
    } else if (body.mode === 'builder') {
        // Workflow Builder — plans and optionally executes
        endpoint = `${backendUrl}/research/plan`
        payload.prompt = buildResearchPrompt(body)
        payload.execute = body.execute ?? false
    } else if (body.mode === 'wide') {
        endpoint = `${backendUrl}/research/wide`
        payload.prompt = buildResearchPrompt(body)
    } else if (body.mode === 'deep') {
        endpoint = `${backendUrl}/research/deep`
        payload.prompt = buildResearchPrompt(body)
    } else if (body.mode === 'read') {
        endpoint = `${backendUrl}/research/read`
        payload.prompt = buildResearchPrompt(body)
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

    // Proxy SSE stream from backend to the Vue client
    const response = await fetchBackend(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify(payload)
    })
    await ensureBackendOk(response, 'Research backend error')

    // Forward the SSE stream directly
    setResponseHeader(event, 'Content-Type', 'text/event-stream')
    setResponseHeader(event, 'Cache-Control', 'no-cache')
    setResponseHeader(event, 'Connection', 'keep-alive')

    if (response.body) {
        return sendStream(event, response.body as any)
    }

    return ''
})
