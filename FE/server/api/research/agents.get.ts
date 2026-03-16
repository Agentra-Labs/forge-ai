/**
 * Nitro server route: GET /api/research/agents
 *
 * Lists available research agents and workflows from the agno backend.
 */
import { fetchAgno } from '../../utils/agno'

defineRouteMeta({
    openAPI: {
        description: 'List available research agents and workflows.',
        tags: ['research']
    }
})

export default defineEventHandler(async () => {
    const { agnoBackendUrl } = useRuntimeConfig()

    try {
        const [agentsResponse, workflowsResponse] = await Promise.all([
            fetchAgno(`${agnoBackendUrl}/agents`),
            fetchAgno(`${agnoBackendUrl}/workflows`)
        ])

        if (!agentsResponse.ok || !workflowsResponse.ok) {
            throw new Error('Agno listing endpoint unavailable')
        }

        const [agents, workflows] = await Promise.all([
            agentsResponse.json(),
            workflowsResponse.json()
        ])

        return {
            agents,
            workflows,
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
