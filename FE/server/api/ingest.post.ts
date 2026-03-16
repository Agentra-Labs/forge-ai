import { z } from 'zod'
import { ensureAgnoOk, fetchAgno } from '../utils/agno'

export default defineEventHandler(async (event) => {
  const { agnoBackendUrl } = useRuntimeConfig()
  const body = await readValidatedBody(event, z.object({
    query: z.string().min(1),
    container_tag: z.string().min(1),
    max_candidates: z.number().int().positive().max(25).optional(),
    citation_expansion: z.boolean().optional()
  }).parse)

  try {
    const response = await fetchAgno(`${agnoBackendUrl}/ingest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    await ensureAgnoOk(response, 'Agno ingest backend error')
    return await response.json()
  } catch (error) {
    console.error('Error starting ingestion:', error)
    if (typeof error === 'object' && error !== null && 'statusCode' in error) {
      throw error
    }

    throw createError({
      statusCode: 502,
      statusMessage: 'Failed to start ingestion process'
    })
  }
})
