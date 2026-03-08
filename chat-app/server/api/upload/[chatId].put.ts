import { blob } from 'hub:blob'
import { db, schema } from 'hub:db'
import { eq } from 'drizzle-orm'
import { z } from 'zod'
import { requireAuthenticatedViewer } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = await requireAuthenticatedViewer(event)

  const { chatId } = await getValidatedRouterParams(event, z.object({
    chatId: z.string()
  }).parse)

  const chat = await db.query.chats.findFirst({
    where: () => eq(schema.chats.id, chatId)
  })

  if (chat && chat.userId !== user.id) {
    throw createError({
      statusCode: 403,
      statusMessage: 'You do not have permission to upload files to this chat'
    })
  }

  return blob.handleUpload(event, {
    formKey: 'files',
    multiple: false,
    ensure: {
      maxSize: FILE_UPLOAD_CONFIG.maxSize,
      types: [...FILE_UPLOAD_CONFIG.types]
    },
    put: {
      addRandomSuffix: true,
      prefix: `${user.id}/${chatId}`
    }
  })
})
