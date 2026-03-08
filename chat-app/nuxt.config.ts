// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'
export default defineNuxtConfig({
    modules: [
        '@nuxt/eslint',
        '@nuxt/icon',
        '@nuxtjs/color-mode',
        '@nuxtjs/mdc',
        '@nuxthub/core',
        'nuxt-auth-utils',
        'nuxt-charts',
        'nuxt-csurf'
    ],

    devtools: {
        enabled: true
    },

    css: ['~/assets/css/main.css'],

    mdc: {
        headings: {
            anchorLinks: false
        },
        highlight: {
            // noApiRoute: true
            shikiEngine: 'javascript'
        }
    },

    experimental: {
        viewTransition: true
    },

    compatibilityDate: '2024-07-11',

    nitro: {
        experimental: {
            openAPI: true
        }
    },

    hub: {
        db: 'sqlite',
        blob: true
    },

    vite: {
        optimizeDeps: {
            include: ['striptags']
        },
        plugins: [tailwindcss() as any]
    },

    eslint: {
        config: {
            stylistic: {
                commaDangle: 'never',
                braceStyle: '1tbs'
            }
        }
    }
})
