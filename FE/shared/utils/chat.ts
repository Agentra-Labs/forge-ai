import { z } from 'zod'

export const CHAT_MODE_VALUES = ['deep', 'wide'] as const
export const RESEARCH_RUN_MODE_VALUES = ['deep', 'wide', 'builder'] as const
export const RESEARCH_WORKFLOW_IDS = ['chained-research', 'literature-review'] as const

export const textMessagePartSchema = z.object({
  type: z.literal('text'),
  text: z.string().min(1)
})

export const reasoningMessagePartSchema = z.object({
  type: z.literal('reasoning'),
  text: z.string(),
  state: z.enum(['running', 'done'])
})

export const fileMessagePartSchema = z.object({
  type: z.literal('file'),
  url: z.string().url(),
  mediaType: z.string().min(1)
})

export const weatherToolMessagePartSchema = z.object({
  type: z.literal('tool-weather'),
  invocation: z.unknown()
})

export const chartToolMessagePartSchema = z.object({
  type: z.literal('tool-chart'),
  invocation: z.unknown()
})

export const messagePartSchema = z.union([
  textMessagePartSchema,
  reasoningMessagePartSchema,
  fileMessagePartSchema,
  weatherToolMessagePartSchema,
  chartToolMessagePartSchema
])

export const chatMessageSchema = z.object({
  id: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string().optional(),
  parts: z.array(messagePartSchema).min(1)
})

export const createChatRequestSchema = z.object({
  id: z.string(),
  mode: z.enum(CHAT_MODE_VALUES),
  message: chatMessageSchema
})

export const sendChatRequestSchema = z.object({
  model: z.string().min(1),
  mode: z.enum(CHAT_MODE_VALUES).optional(),
  messages: z.array(chatMessageSchema).min(1)
})

export function extractTextFromParts(parts: Array<z.infer<typeof messagePartSchema>>): string {
  return parts
    .filter((part): part is z.infer<typeof textMessagePartSchema> => part.type === 'text')
    .map(part => part.text.trim())
    .filter(Boolean)
    .join('\n\n')
}

export function extractFileParts(parts: Array<z.infer<typeof messagePartSchema>>) {
  return parts.filter((part): part is z.infer<typeof fileMessagePartSchema> => part.type === 'file')
}

export function buildPromptFromParts(parts: Array<z.infer<typeof messagePartSchema>>): string {
  const text = extractTextFromParts(parts)
  const files = extractFileParts(parts)

  if (!files.length) {
    return text
  }

  const attachmentContext = files
    .map((part, index) => `Attachment ${index + 1}: ${part.url} (${part.mediaType})`)
    .join('\n')

  return [text, attachmentContext].filter(Boolean).join('\n\n')
}
