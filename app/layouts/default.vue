<script setup lang="ts">
import { LazyModalConfirm } from '#components'
import { defineShortcuts } from '~/composables/defineShortcuts'
import { useOverlay } from '~/composables/useOverlay'
import { useToast } from '~/composables/useToast'

const route = useRoute()
const toast = useToast()
const overlay = useOverlay()
const { loggedIn, openInPopup } = useUserSession()
const { csrf, headerName } = useCsrf()

const open = useState<boolean>('sidebar-open', () => false)
const collapsed = useState<boolean>('sidebar-collapsed', () => false)

const deleteModal = overlay.create(LazyModalConfirm, {
  props: {
    title: 'Delete chat',
    description: 'Are you sure you want to delete this chat? This cannot be undone.'
  }
})

const { data: chats, refresh: refreshChats } = await useFetch('/api/chats', {
  key: 'chats',
  transform: data => data.map(chat => ({
    id: chat.id,
    label: chat.title || 'Untitled',
    to: `/chat/${chat.id}`,
    icon: 'lucide:message-circle',
    createdAt: chat.createdAt
  }))
})

onNuxtReady(async () => {
  const first10 = (chats.value || []).slice(0, 10)
  for (const chat of first10) {
    // prefetch the chat and let the browser cache it
    await $fetch(`/api/chats/${chat.id}`)
  }
})

watch(loggedIn, () => {
  refreshChats()

  open.value = false
})

watch(() => route.fullPath, () => {
  open.value = false
})

const { groups } = useChats(chats)

async function deleteChat(id: string) {
  const instance = deleteModal.open()
  const result = await instance.result
  if (!result) {
    return
  }

  await $fetch(`/api/chats/${id}`, {
    method: 'DELETE',
    headers: { [headerName]: csrf }
  })

  toast.add({
    title: 'Chat deleted',
    description: 'Your chat has been deleted',
    icon: 'i-lucide-trash'
  })

  refreshChats()

  if (route.params.id === id) {
    navigateTo('/dashboard')
  }
}

defineShortcuts({
  c: () => {
    navigateTo('/dashboard')
  }
})
</script>

<template>
  <div class="flex min-h-screen bg-transparent">
    <div
      v-if="open"
      class="fixed inset-0 z-40 bg-neutral/45 backdrop-blur-sm lg:hidden"
      @click="open = false"
    />

    <aside
      class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-base-300/70 bg-base-200/72 backdrop-blur-xl transition-[transform,width] duration-200 lg:sticky lg:top-0 lg:z-10 lg:h-screen lg:translate-x-0"
      :class="[collapsed ? 'w-72 lg:w-[5.25rem]' : 'w-72', open ? 'translate-x-0' : '-translate-x-full']"
    >
      <div class="flex items-center justify-between border-b border-base-300/80 px-5 py-4">
        <NuxtLink to="/dashboard" class="flex items-center gap-3 min-w-0" @click="open = false">
          <div class="flex h-9 w-9 items-center justify-center rounded-2xl border border-primary/20 bg-primary/12 text-primary shadow-sm">
            <Logo class="h-5 w-auto shrink-0" />
          </div>
          <div v-if="!collapsed" class="min-w-0">
            <p class="text-[11px] uppercase tracking-[0.3em] text-base-content/45">Workspace</p>
            <p class="text-base font-semibold">Forge Research</p>
          </div>
        </NuxtLink>

        <div class="flex items-center gap-1">
          <button class="btn btn-ghost btn-sm btn-square hidden lg:inline-flex" @click="collapsed = !collapsed">
            <Icon :name="collapsed ? 'lucide:panel-left-open' : 'lucide:panel-left-close'" class="h-4 w-4" />
          </button>
          <button class="btn btn-ghost btn-square lg:hidden" @click="open = false">
          <Icon name="lucide:x" class="h-5 w-5" />
          </button>
        </div>
      </div>

      <div class="flex flex-1 flex-col overflow-hidden px-3 py-4">
        <NuxtLink to="/dashboard" class="btn btn-primary h-10 min-h-10 w-full gap-2 rounded-2xl px-3 shadow-sm" :class="collapsed ? 'justify-center px-0' : 'justify-start'" @click="open = false">
          <Icon name="lucide:plus" class="h-3.5 w-3.5" />
          <span v-if="!collapsed">New thread</span>
        </NuxtLink>

        <div class="mt-5 overflow-y-auto pr-1">
          <div
            v-for="group in groups"
            :key="group.id"
            class="mb-5"
          >
            <p v-if="!collapsed" class="mb-2 px-2 text-[11px] font-semibold uppercase tracking-[0.25em] text-base-content/40">
              {{ group.label }}
            </p>

            <ul class="space-y-1">
              <li v-for="item in group.items" :key="item.id">
                <template v-if="item.id">
                <div
                  class="group flex items-center gap-2 rounded-2xl border transition-colors"
                  :class="[
                    collapsed ? 'justify-center px-0 py-2' : 'px-2 py-1.5',
                    route.path === `/chat/${item.id}`
                    ? 'border-primary/20 bg-base-100/95 shadow-sm'
                    : 'border-transparent hover:border-base-300/70 hover:bg-base-100/65'
                  ]"
                >
                  <NuxtLink
                    :to="`/chat/${item.id}`"
                    class="flex min-w-0 items-center gap-3"
                    :class="collapsed ? 'justify-center' : 'flex-1'"
                    @click="open = false"
                  >
                    <div
                      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl"
                      :class="route.path === `/chat/${item.id}` ? 'bg-primary/12 text-primary' : 'bg-base-300/70 text-base-content/70'"
                    >
                      <Icon name="lucide:message-circle" class="h-3.5 w-3.5" />
                    </div>
                    <span v-if="!collapsed" class="truncate text-[13px]" :class="item.label === 'Untitled' ? 'text-base-content/55' : 'text-base-content'">
                      {{ item.label }}
                    </span>
                  </NuxtLink>

                  <button
                    v-if="!collapsed"
                    class="btn btn-ghost btn-xs btn-square opacity-0 transition-opacity group-hover:opacity-100"
                    @click.stop.prevent="deleteChat((item as any).id)"
                  >
                    <Icon name="lucide:x" class="h-4 w-4 text-error" />
                  </button>
                </div>
                </template>
              </li>
            </ul>
          </div>
        </div>

        <div class="mt-4 border-t border-base-300/80 pt-4">
          <UserMenu v-if="loggedIn" :collapsed="collapsed" />
          <button
            v-else
            class="btn btn-outline w-full gap-2 rounded-2xl"
            :class="collapsed ? 'justify-center px-0' : 'justify-start'"
            @click="openInPopup('/auth/github')"
          >
            <Icon name="simple-icons:github" class="h-5 w-5" />
            <span v-if="!collapsed">Login with GitHub</span>
          </button>
        </div>
      </div>
    </aside>

    <div class="relative min-w-0 flex-1 lg:h-screen lg:min-h-0 lg:overflow-hidden">
      <slot />
    </div>
  </div>
</template>
