import { z } from 'zod'
import { ensureBackendOk, fetchBackend } from '../../utils/backend'

export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig()
  const body = await readValidatedBody(event, z.object({
    arxiv_id: z.string().min(1),
    model: z.string().optional()
  }).parse)

  try {
    const response = await fetchBackend(`${backendUrl}/ideate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        arxiv_id: body.arxiv_id,
        model: body.model
      })
    })
    await ensureBackendOk(response, 'Ideate backend error')
    return await response.json()
  } catch (error) {
    console.error('Error starting ideation:', error)
    if (typeof error === 'object' && error !== null && 'statusCode' in error) {
      throw error
    }

    throw createError({
      statusCode: 502,
      statusMessage: 'Failed to start ideation process'
    })
  }
})
