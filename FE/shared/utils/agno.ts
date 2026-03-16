export interface SseMessage {
  event?: string
  data: string
}

export interface AgnoNormalizedMessage {
  event?: string
  content?: string
  error?: string
  stepName?: string
  runId?: string
  workflowId?: string
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

export function extractAgnoContent(payload: unknown): string | undefined {
  if (!isRecord(payload)) {
    return getString(payload)
  }

  const nestedData = isRecord(payload.data) ? payload.data : undefined
  return getString(payload.content) ?? getString(nestedData?.content)
}

export function normalizeAgnoMessage(message: SseMessage): AgnoNormalizedMessage {
  const rawData = message.data.trim()
  if (!rawData) {
    return {
      event: message.event,
      done: false,
      raw: rawData
    }
  }

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
    return {
      event: message.event,
      content: rawData,
      done: false,
      raw: rawData
    }
  }

  const event = message.event || (isRecord(payload) ? getString(payload.event) : undefined)
  const nestedData = isRecord(payload) && isRecord(payload.data) ? payload.data : undefined
  const content = extractAgnoContent(payload)
  const error = getString(isRecord(payload) ? payload.message : undefined)
    ?? getString(nestedData?.message)
  const stepName = getString(isRecord(payload) ? payload.step_name : undefined)
    ?? getString(nestedData?.step_name)
  const runId = getString(isRecord(payload) ? payload.run_id : undefined)
    ?? getString(nestedData?.run_id)
  const workflowId = getString(isRecord(payload) ? payload.workflow_id : undefined)
    ?? getString(nestedData?.workflow_id)

  return {
    event,
    content,
    error,
    stepName,
    runId,
    workflowId,
    done: false,
    raw: payload
  }
}
