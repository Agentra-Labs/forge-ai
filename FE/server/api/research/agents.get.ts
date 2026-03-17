/**
 * Nitro server route: GET /api/research/agents
 *
 * Lists available research features from the nova-forge backend.
 */
import { fetchBackend } from '../../utils/backend'

defineRouteMeta({
    openAPI: {
        description: 'List available research features and endpoints.',
        tags: ['research']
    }
})

export default defineEventHandler(async () => {
    const { backendUrl } = useRuntimeConfig()

    try {
        const response = await fetchBackend(`${backendUrl}/`)

        if (!response.ok) {
            throw new Error('Backend unavailable')
        }

        const data = await response.json()

        return {
            agents: data.features?.research || [],
            workflows: [],
            ideate: data.features?.ideate || [],
            status: 'connected'
        }
    } catch {
        return {
            agents: [
                'POST /research/chat',
                'POST /research/title',
                'POST /research/wide',
                'POST /research/deep',
                'POST /research/read',
                'POST /research/plan',
                'POST /research/run'
            ],
            workflows: ['chained', 'literature'],
            ideate: [
                'POST /ideate',
                'GET /ideate/{job_id}'
            ],
            status: 'disconnected'
        }
    }
})
