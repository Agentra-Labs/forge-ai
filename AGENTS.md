# Repository Guidelines

This document provides guidance for AI agents working in this repository.

## Project Overview

This repository contains a Nuxt 4 application in `chat-app/` - a research-focused chat interface with authentication, file uploads, and AI-powered research capabilities.

## Project Structure

```
chat-app/
├── app/                    # Frontend source code
│   ├── components/         # Vue components (PascalCase)
│   ├── composables/        # Reusable client logic (use*.ts)
│   ├── layouts/            # Page layouts
│   ├── pages/              # Route pages (file-based routing)
│   └── assets/css/         # Global styles
├── server/                 # Server-side code
│   ├── api/                # API endpoints
│   ├── routes/             # Additional route handlers
│   ├── db/                 # Database schema and migrations
│   └── utils/              # Server utilities
├── shared/                 # Shared types and utilities
├── .nuxt/                  # Generated (do not edit)
├── .data/                  # Generated (do not edit)
└── node_modules/           # Dependencies (do not edit)
```

## Build, Development & Quality Commands

All commands run from `chat-app/` directory.

### Core Commands
```bash
pnpm install      # Install dependencies (use pnpm, matches lockfile/CI)
pnpm dev          # Start dev server at http://localhost:3000
pnpm build        # Create production build
pnpm preview      # Serve built app locally
pnpm lint         # Run ESLint across workspace
pnpm typecheck    # Run Nuxt and TypeScript checks
```

### Database Commands
```bash
pnpm db:generate  # Generate Drizzle ORM artifacts
pnpm db:migrate   # Apply database migrations
```

### Running Tests
No unit-test suite is committed yet. For pre-PR validation:
```bash
pnpm lint && pnpm typecheck
```

For manual testing, use `pnpm dev` and verify in the browser.

## Code Style Guidelines

### General Rules
- **2-space indentation** (enforced by `.editorconfig`)
- **LF line endings**, **UTF-8 charset**
- **Always include a final newline** at end of files
- Use **TypeScript** for all new code (`.ts` files, `<script setup lang="ts">` in Vue)
- Keep `vue/max-attributes-per-line` compliant (max 3 attributes per line)

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `ResearchModeSwitch.vue` |
| Composables | camelCase, prefix `use` | `useResearchMode.ts` |
| Types/Interfaces | PascalCase | `ResearchMode`, `ChatMessage` |
| Constants | UPPER_SNAKE_CASE | `RESEARCH_MODES` |
| Variables/Functions | camelCase | `getViewerIdentity` |

### Import Patterns
```typescript
// Server-side: use hub: alias
import { db, schema } from 'hub:db'
import { eq, desc } from 'drizzle-orm'

// Icons use lucide: prefix
<Icon name="lucide:menu" class="w-5 h-5" />
```

### Vue Single File Components
```vue
<script setup lang="ts">
withDefaults(defineProps<{
  compact?: boolean
}>(), {
  compact: false
})

const { mode } = useResearchMode()
</script>

<template>
  <div class="...">
    <button @click="handler">Label</button>
  </div>
</template>
```

### Error Handling
```typescript
export default defineEventHandler(async (event) => {
  try {
    const result = await doSomething()
    return result
  } catch (error) {
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to process request'
    })
  }
})
```

### TypeScript Guidelines
- Always define types for props, composable returns, and API responses
- Use `type` for unions, intersections, and primitives
- Use `interface` for object shapes that may be extended
- Avoid `any` - use `unknown` when type is truly uncertain

### CSS & Styling
- Use **Tailwind CSS** (v4) and **daisyUI** for all styling
- Prefer Tailwind utility classes over custom CSS
- Use semantic color tokens: `bg-base-100`, `text-primary`, `border-base-300`
- Use daisyUI components when available

## Security & Configuration

### Environment Variables
Copy `chat-app/.env.example` to `chat-app/.env` for local development:
- `NUXT_SESSION_PASSWORD` - Session encryption
- GitHub OAuth credentials for authentication
- `AI_GATEWAY_API_KEY` for AI features
- Database connection variables

### Security Rules
- **Never commit** API keys, OAuth secrets, or database credentials
- Use `.env` files (already in `.gitignore`) for local secrets
- Validate all user inputs on both client and server
- Use Zod for schema validation on API payloads

## Git & Workflow

### Commit Messages
- Use imperative mood: "Add feature" not "Added feature"
- Optional scope: `feat(ui):`, `fix(api):`, `refactor(db):`
- Keep commits single-purpose and focused

### Pre-PR Checklist
```bash
pnpm lint && pnpm typecheck
```

## Technology Stack

- **Framework**: Nuxt 4
- **UI**: Vue 3 (Composition API), Tailwind CSS 4, daisyUI
- **Database**: Drizzle ORM with PostgreSQL/Turso
- **Auth**: Clerk (`@clerk/nuxt`)
- **Icons**: Iconify (lucide, logos, simple-icons)
- **Package Manager**: pnpm (v10.30.3)
