import { db, schema } from 'hub:db'
import { createChatRequestSchema } from '#shared/utils/chat'
import { getViewerIdentity } from '../utils/auth'

export default defineEventHandler(async (event) => {
  const viewer = await getViewerIdentity(event)
  const { id, mode, message } = await readValidatedBody(event, createChatRequestSchema.parse)
  if (message.role !== 'user') {
    throw createError({ statusCode: 400, statusMessage: 'Initial chat message must be from the user' })
  }

  const [chat] = await db.insert(schema.chats).values({
    id,
    title: '',
    mode,
    userId: viewer.id
  }).returning()

  if (!chat) {
    throw createError({ statusCode: 500, statusMessage: 'Failed to create chat' })
  }

  await db.insert(schema.messages).values({
    chatId: chat.id,
    role: 'user',
    parts: message.parts
  })

  return chat
})
