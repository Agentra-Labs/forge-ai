/**
 * Nitro server route: GET /api/research/agents
 *
 * Lists available research agents and workflows from the agno backend.
 */

defineRouteMeta({
    openAPI: {
        description: 'List available research agents and workflows.',
        tags: ['research']
    }
})

export default defineEventHandler(async () => {
    const { agnoBackendUrl } = useRuntimeConfig()

    try {
        const [agentsRes, workflowsRes] = await Promise.all([
            fetch(`${agnoBackendUrl}/agents`).then(r => r.json()).catch(() => []),
            fetch(`${agnoBackendUrl}/workflows`).then(r => r.json()).catch(() => [])
        ])

        return {
            agents: agentsRes,
            workflows: workflowsRes,
            status: 'connected'
        }
    } catch {
        return {
            agents: [],
            workflows: [],
            status: 'disconnected'
        }
    }
})
