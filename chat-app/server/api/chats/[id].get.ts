import { db, schema } from 'hub:db'
import { and, asc, eq } from 'drizzle-orm'
import { z } from 'zod'
import { getViewerIdentity } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const viewer = await getViewerIdentity(event)

  const { id } = await getValidatedRouterParams(event, z.object({
    id: z.string()
  }).parse)

  const chat = await db.query.chats.findFirst({
    where: () => and(
      eq(schema.chats.id, id as string),
      eq(schema.chats.userId, viewer.id)
    ),
    with: {
      messages: {
        orderBy: () => asc(schema.messages.createdAt)
      }
    }
  })

  if (!chat) {
    throw createError({ statusCode: 404, statusMessage: 'Chat not found' })
  }

  return chat
})
