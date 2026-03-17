// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
export default defineNuxtConfig({
  modules: [
    "@clerk/nuxt",
    "@nuxt/eslint",
    "@nuxt/icon",
    "@nuxtjs/color-mode",
    "@nuxtjs/mdc",
    "@nuxthub/core",
    "nuxt-charts",
    "nuxt-csurf",
  ],

  devtools: {
    enabled: true,
  },

  css: ["~/assets/css/main.css"],

  mdc: {
    headings: {
      anchorLinks: false,
    },
    highlight: {
      // noApiRoute: true
      shikiEngine: "javascript",
    },
  },

  experimental: {
    viewTransition: true,
  },

  runtimeConfig: {
    backendUrl: process.env.BACKEND_URL || "http://localhost:7777",
    supermemoryApiKey: process.env.SUPERMEMORY_API_KEY || "",
    public: {
      backendUrl: process.env.BACKEND_URL || "http://localhost:7777",
    },
  },

  clerk: {
    signInForceRedirectUrl: "/dashboard",
    signInFallbackRedirectUrl: "/dashboard",
    signUpForceRedirectUrl: "/dashboard",
    signUpFallbackRedirectUrl: "/dashboard",
  },

  compatibilityDate: "2024-07-11",

  nitro: {
    experimental: {
      openAPI: true,
    },
  },

  hub: {
    db: "sqlite",
    blob: true,
  },

  vite: {
    optimizeDeps: {
      include: ["striptags"],
    },
    plugins: [tailwindcss() as any],
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: "never",
        braceStyle: "1tbs",
      },
    },
  },

  build: {
    transpile: ["@supermemory/memory-graph"],
  },
});
