<script setup lang="ts">
import type { NuxtError } from '#app'

defineProps<{
  error: NuxtError
}>()

useSeoMeta({
  title: 'Page not found',
  description: 'We are sorry but this page could not be found.'
})

const htmlAttrs = {
  lang: 'en',
  theme: 'dim',
  'data-theme': 'dim'
} as any

useHead({
  htmlAttrs
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-base-100 flex-col gap-4">
    <h1 class="text-4xl font-bold">{{ error.statusCode }}</h1>
    <p class="text-xl">{{ error.message || 'An error occurred' }}</p>
    <NuxtLink to="/" class="btn btn-primary">Go Home</NuxtLink>
  </div>
</template>
