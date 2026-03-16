import { clerkClient } from '@clerk/nuxt/server'
import { db, schema } from 'hub:db'
import type { H3Event } from 'h3'
import { eq } from 'drizzle-orm'
import { createError, getCookie, setCookie } from 'h3'

const GUEST_COOKIE_NAME = 'forge_guest_id'
const GUEST_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

export interface ViewerIdentity {
  id: string
  isSignedIn: boolean
  name: string | null
  username: string | null
  storageKey: string
}

export async function getViewerIdentity(event: H3Event): Promise<ViewerIdentity> {
  const auth = event.context.auth?.()

  if (auth?.isAuthenticated && auth.userId) {
    await migrateGuestChats(event, auth.userId)

    const user = await clerkClient(event).users.getUser(auth.userId)
    const primaryEmail = user.emailAddresses.find(email => email.id === user.primaryEmailAddressId)?.emailAddress
      ?? user.emailAddresses[0]?.emailAddress
      ?? null
    const username = user.username
      ?? primaryEmail?.split('@')[0]
      ?? user.firstName
      ?? user.id
    const name = user.fullName
      ?? [user.firstName, user.lastName].filter(Boolean).join(' ')
      ?? username

    return {
      id: user.id,
      isSignedIn: true,
      name,
      username,
      storageKey: user.id
    }
  }

  const guestId = getOrCreateGuestId(event)

  return {
    id: guestId,
    isSignedIn: false,
    name: null,
    username: null,
    storageKey: guestId
  }
}

export async function requireAuthenticatedViewer(event: H3Event) {
  const auth = event.context.auth?.()

  if (!auth?.isAuthenticated || !auth.userId) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Sign in with Google to continue'
    })
  }

  await migrateGuestChats(event, auth.userId)

  return await clerkClient(event).users.getUser(auth.userId)
}

function getOrCreateGuestId(event: H3Event) {
  const existingGuestId = getCookie(event, GUEST_COOKIE_NAME)
  if (existingGuestId) {
    return existingGuestId
  }

  const guestId = crypto.randomUUID()

  setCookie(event, GUEST_COOKIE_NAME, guestId, {
    httpOnly: true,
    maxAge: GUEST_COOKIE_MAX_AGE,
    path: '/',
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production'
  })

  return guestId
}

async function migrateGuestChats(event: H3Event, userId: string) {
  const guestId = getCookie(event, GUEST_COOKIE_NAME)

  if (!guestId || guestId === userId) {
    return
  }

  await db.update(schema.chats)
    .set({ userId })
    .where(eq(schema.chats.userId, guestId))
}
