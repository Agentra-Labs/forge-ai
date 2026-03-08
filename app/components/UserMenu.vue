<script setup lang="ts">
defineProps<{
  collapsed?: boolean
}>()

const colorMode = useColorMode()
const { user, clear } = useUserSession()

function logout() {
  clear()
  navigateTo('/')
}
</script>

<template>
  <div class="dropdown dropdown-end w-full">
    <div
      tabindex="0"
      role="button"
      class="flex w-full items-center gap-3 rounded-2xl border border-base-300/80 bg-base-100/72 px-3 py-3 text-left transition-colors hover:bg-base-100"
    >
      <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-base-300">
        <img v-if="user?.avatar" :src="user.avatar" :alt="user?.name || user?.username" class="h-full w-full rounded-2xl object-cover" />
        <span v-else class="text-sm font-medium">{{ (user?.name || user?.username || '?').charAt(0).toUpperCase() }}</span>
      </div>
      <div class="min-w-0 flex-1" v-if="!collapsed">
        <p class="truncate text-sm font-medium">{{ user?.name || user?.username }}</p>
        <p class="truncate text-xs text-base-content/55">@{{ user?.username }}</p>
      </div>
      <Icon v-if="!collapsed" name="lucide:chevrons-up-down" class="h-4 w-4 text-base-content/45" />
    </div>

    <ul tabindex="0" class="menu dropdown-content z-[1] mt-3 w-56 rounded-2xl border border-base-300/80 bg-base-100 p-2 shadow-xl">
      <li class="menu-title px-3 pb-1">
        <span>{{ user?.name || user?.username }}</span>
      </li>
      <li>
        <a @click.prevent="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'">
          <Icon :name="colorMode.value === 'dark' ? 'lucide:moon' : 'lucide:sun'" class="h-4 w-4" />
          Toggle Theme
        </a>
      </li>
      <li>
        <NuxtLink to="/dashboard">
          <Icon name="lucide:layout-dashboard" class="h-4 w-4" />
          Dashboard
        </NuxtLink>
      </li>
      <li>
        <a class="text-error" @click="logout">
          <Icon name="lucide:log-out" class="h-4 w-4" />
          Log out
        </a>
      </li>
    </ul>
  </div>
</template>
