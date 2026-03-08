<script setup lang="ts">
const colorMode = useColorMode()

const color = computed(() => colorMode.value === 'dark' ? '#1b1718' : 'white')

const htmlAttrs = {
  lang: 'en',
  theme: 'dim',
  'data-theme': 'dim'
} as any

useHead({
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    { key: 'theme-color', name: 'theme-color', content: color }
  ],
  link: [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap' },
    { rel: 'icon', href: '/favicon.ico' }
  ],
  htmlAttrs
})

const title = 'Nuxt AI Chatbot template'
const description = 'A full-featured, hackable Nuxt AI chatbot template made with Nuxt UI.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogImage: 'https://ui.nuxt.com/assets/templates/nuxt/chat-light.png',
  twitterImage: 'https://ui.nuxt.com/assets/templates/nuxt/chat-light.png',
  twitterCard: 'summary_large_image'
})
</script>

<template>
  <div>
    <NuxtLoadingIndicator color="oklch(var(--p))" />

    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>
