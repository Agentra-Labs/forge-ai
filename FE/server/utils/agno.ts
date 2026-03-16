import type { MessagePart } from '#shared/types/research'
import { buildPromptFromParts } from '#shared/utils/chat'

const AGNO_TIMEOUT_MS = 180_000

export async function fetchAgno(endpoint: string, init: RequestInit = {}) {
  try {
    return await fetch(endpoint, {
      ...init,
      signal: AbortSignal.timeout(AGNO_TIMEOUT_MS)
    })
  } catch (error) {
    const name = (error as Error).name
    if (name === 'TimeoutError') {
      throw createError({
        statusCode: 504,
        statusMessage: 'Agno backend timed out'
      })
    }

    throw createError({
      statusCode: 502,
      statusMessage: 'Unable to reach Agno backend'
    })
  }
}

export async function ensureAgnoOk(response: Response, context: string) {
  if (response.ok) {
    return response
  }

  const errorText = await response.text()
  throw createError({
    statusCode: response.status,
    statusMessage: `${context}: ${errorText || 'Unknown Agno backend error'}`
  })
}

export function buildResearchPrompt(body: {
  goal: string
  primary_url?: string
  secondary_url?: string
  seed_arxiv_id?: string
  keywords?: string[]
}) {
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

export function buildChatPrompt(parts: MessagePart[]) {
  return buildPromptFromParts(parts)
}
