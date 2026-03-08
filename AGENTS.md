# Repository Guidelines

## Project Structure & Module Organization
This repository currently ships one active application in `chat-app/`, a Nuxt 4 workspace for the Forge landing page and research UI. Frontend code lives in `chat-app/app/`:
`pages/` for routes, `components/` for UI, `composables/` for reusable client logic, `layouts/` for shells, and `assets/css/` for styling. Server code lives in `chat-app/server/` with `api/` endpoints, `routes/` auth handlers, and `db/` schema plus migrations. Shared types and utilities live in `chat-app/shared/`. Generated output in `.nuxt/`, `.data/`, and `node_modules/` should not be edited by hand.

## Build, Test, and Development Commands
Run commands from `chat-app/`.

- `pnpm install`: install dependencies; this matches the lockfile and CI workflow.
- `pnpm dev`: start the Nuxt dev server on `http://localhost:3000`.
- `pnpm build`: create the production build.
- `pnpm preview`: serve the built app locally.
- `pnpm lint`: run ESLint across the workspace.
- `pnpm typecheck`: run Nuxt and TypeScript checks.
- `pnpm db:generate` / `pnpm db:migrate`: update Drizzle artifacts and apply database migrations.

## Coding Style & Naming Conventions
Use 2-space indentation, LF line endings, UTF-8, and a final newline; these are enforced by `chat-app/.editorconfig`. Prefer TypeScript and Vue SFCs. Use `PascalCase` for components such as `ResearchModeSwitch.vue`, `camelCase` for composables such as `useResearchMode.ts`, and route-driven names under `app/pages/`. ESLint is configured through `chat-app/eslint.config.mjs`; keep `vue/max-attributes-per-line` compliant and avoid introducing formatter-only churn.

## Testing Guidelines
There is no committed unit-test suite yet. Treat `pnpm lint` and `pnpm typecheck` as the required pre-PR validation, then manually smoke-test the affected flow in `pnpm dev`. When adding tests later, place them near the feature or under a dedicated `tests/` directory and mirror the source name.

## Commit & Pull Request Guidelines
Recent history mixes conventional commits (`feat(ui): ...`) with short imperative subjects (`Update root README...`). Prefer imperative, single-purpose commit messages and use an optional scope when it adds clarity. Pull requests should include a concise summary, linked issue or context, commands run locally, and screenshots or short recordings for UI changes.

## Security & Configuration Tips
Copy `chat-app/.env.example` when setting up local secrets. Do not commit API keys, OAuth secrets, or database credentials. For auth and AI features, validate `NUXT_SESSION_PASSWORD`, GitHub OAuth settings, `AI_GATEWAY_API_KEY`, and storage/database variables before testing integrations.
