/**
 * SSE utilities for the nova-forge backend.
 *
 * The backend streams SSE with simple data-only format:
 *   data: {"content": "chunk text"}
 *   data: [DONE]
 */

export interface SseMessage {
  event?: string
  data: string
}

export interface BackendNormalizedMessage {
  event?: string
  content?: string
  error?: string
  done: boolean
  raw: unknown
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function getString(value: unknown): string | undefined {
  return typeof value === 'string' && value.length > 0 ? value : undefined
}

function parseSseBlock(block: string): SseMessage | null {
  const lines = block.split('\n')
  let event: string | undefined
  const dataLines: string[] = []

  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim()
      continue
    }

    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }

  if (!event && dataLines.length === 0) {
    return null
  }

  return {
    event,
    data: dataLines.join('\n')
  }
}

export function consumeSseMessages(buffer: string, chunk: string) {
  const normalized = `${buffer}${chunk}`.replace(/\r\n/g, '\n')
  const blocks = normalized.split('\n\n')
  const nextBuffer = blocks.pop() ?? ''
  const messages = blocks
    .map(parseSseBlock)
    .filter((message): message is SseMessage => message !== null)

  return {
    messages,
    buffer: nextBuffer
  }
}

export function flushSseMessages(buffer: string): SseMessage[] {
  const trimmed = buffer.trim()
  if (!trimmed) {
    return []
  }

  const message = parseSseBlock(trimmed)
  return message ? [message] : []
}

export function normalizeBackendMessage(message: SseMessage): BackendNormalizedMessage {
  const rawData = message.data.trim()
  if (!rawData) {
    return {
      event: message.event,
      done: false,
      raw: rawData
    }
  }

  // [DONE] marker signals end of stream
  if (rawData === '[DONE]') {
    return {
      event: message.event,
      done: true,
      raw: rawData
    }
  }

  let payload: unknown = rawData
  try {
    payload = JSON.parse(rawData)
  } catch {
    // Plain text response
    return {
      event: message.event,
      content: rawData,
      done: false,
      raw: rawData
    }
  }

  // Extract content/error from JSON payload
  const content = isRecord(payload) ? getString(payload.content) : undefined
  const error = isRecord(payload) ? getString(payload.error) : undefined

  return {
    event: message.event,
    content,
    error,
    done: false,
    raw: payload
  }
}

// Legacy aliases for backward compatibility
export const extractAgnoContent = (payload: unknown): string | undefined => {
  if (!isRecord(payload)) {
    return getString(payload)
  }
  return getString(payload.content)
}

export const normalizeAgnoMessage = normalizeBackendMessage
