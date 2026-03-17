import { z } from 'zod'
import { ensureBackendOk, fetchBackend } from '../../utils/backend'

export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig()
  const jobId = getRouterParam(event, 'id')
  
  if (!jobId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Job ID is required'
    })
  }

  try {
    const response = await fetchBackend(`${backendUrl}/ideate/${jobId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
    await ensureBackendOk(response, 'Ideate backend error')
    return await response.json()
  } catch (error) {
    console.error('Error checking ideation status:', error)
    if (typeof error === 'object' && error !== null && 'statusCode' in error) {
      throw error
    }

    throw createError({
      statusCode: 502,
      statusMessage: 'Failed to check ideation status'
    })
  }
})
