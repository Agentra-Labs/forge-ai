<script setup lang="ts">
const sidebarOpen = useState<boolean>('sidebar-open', () => false)
const { mode } = useResearchMode()
</script>

<template>
  <div class="sticky top-0 z-20 border-b border-base-300 bg-base-100/85 backdrop-blur">
    <div class="navbar mx-auto max-w-6xl min-h-14 px-3 sm:px-5">
      <div class="flex-none flex items-center gap-1">
        <button class="btn btn-ghost btn-square lg:hidden" @click="sidebarOpen = true">
        <Icon name="lucide:menu" class="w-5 h-5" />
        </button>
      </div>
      <div class="flex-1 px-2">
        <div class="hidden rounded-full border border-base-300 bg-base-200/60 px-3 py-1.5 text-xs text-base-content/60 sm:flex sm:max-w-md sm:items-center sm:gap-2">
          <Icon name="lucide:sparkles" class="h-4 w-4 text-primary" />
          Forge Research · {{ mode === 'deep' ? 'Deep mode' : 'Wide mode' }}
        </div>
      </div>
      <div class="flex-none gap-2">
        <NuxtLink to="/dashboard" class="btn btn-primary btn-sm h-9 min-h-9 rounded-full px-3.5">
          <Icon name="lucide:plus" class="h-3.5 w-3.5" />
          <span class="hidden sm:inline">New Thread</span>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
