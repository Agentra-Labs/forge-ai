import { blob } from 'hub:blob'
import { db, schema } from 'hub:db'
import { and, eq } from 'drizzle-orm'
import { z } from 'zod'
import { getViewerIdentity } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const viewer = await getViewerIdentity(event)
  const { id } = await getValidatedRouterParams(event, z.object({
    id: z.string()
  }).parse)

  const chat = await db.query.chats.findFirst({
    where: () => and(eq(schema.chats.id, id as string), eq(schema.chats.userId, viewer.id))
  })

  if (!chat) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Chat not found'
    })
  }

  const chatFolder = `${viewer.storageKey}/${id}`

  try {
    const { blobs } = await blob.list({
      prefix: chatFolder
    })

    if (blobs.length > 0) {
      await Promise.all(
        blobs.map(b =>
          blob.del(b.pathname).catch(error =>
            console.error('[delete-chat] Failed to delete file:', b.pathname, error)
          )
        )
      )
    }
  } catch (error) {
    console.error('Failed to list/delete chat files:', error)
  }

  return await db.delete(schema.chats)
    .where(and(eq(schema.chats.id, id as string), eq(schema.chats.userId, viewer.id)))
    .returning()
})
