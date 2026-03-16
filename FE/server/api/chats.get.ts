import { db, schema } from 'hub:db'
import { eq, desc } from 'drizzle-orm'
import { getViewerIdentity } from '../utils/auth'

export default defineEventHandler(async (event) => {
    const viewer = await getViewerIdentity(event)

    return await db.query.chats.findMany({
        where: () => eq(schema.chats.userId, viewer.id),
        orderBy: () => desc(schema.chats.createdAt)
    })
})
