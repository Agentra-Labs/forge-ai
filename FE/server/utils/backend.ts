import type { MessagePart } from '#shared/types/research'
import { buildPromptFromParts } from '#shared/utils/chat'

const BACKEND_TIMEOUT_MS = 300_000 // 5 minutes for long research workflows

export async function fetchBackend(endpoint: string, init: RequestInit = {}) {
  try {
    return await fetch(endpoint, {
      ...init,
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS)
    })
  } catch (error) {
    const name = (error as Error).name
    if (name === 'TimeoutError') {
      throw createError({
        statusCode: 504,
        statusMessage: 'Backend timed out'
      })
    }

    throw createError({
      statusCode: 502,
      statusMessage: 'Unable to reach backend'
    })
  }
}

export async function ensureBackendOk(response: Response, context: string) {
  if (response.ok) {
    return response
  }

  const errorText = await response.text()
  throw createError({
    statusCode: response.status,
    statusMessage: `${context}: ${errorText || 'Unknown backend error'}`
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
