import { blob } from '../../utils/blob'
import { z } from 'zod'
import { requireAuthenticatedViewer } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = await requireAuthenticatedViewer(event)

  const { pathname } = await getValidatedRouterParams(event, z.object({
    pathname: z.string().min(1)
  }).parse)

  if (!pathname.startsWith(`${user.id}/`)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'You do not have permission to delete this file'
    })
  }

  await blob.del(pathname)

  return sendNoContent(event)
})
