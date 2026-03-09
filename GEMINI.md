# Forge AI — Gemini Context

Forge is a research-first AI workspace built to turn technical signals (papers, benchmarks, evidence) into actionable decisions for engineering and product teams. It is currently being developed for the Amazon Nova Hackathon.

## Project Architecture

Forge is a mono-repo consisting of two primary services:

1.  **`chat-app/` (Frontend):** A Nuxt 4 workspace providing the landing page and research UI.
    - **Tech Stack:** Nuxt 4, Vue 3, Tailwind CSS 4, DaisyUI 5, Clerk (Auth), Drizzle ORM (SQLite/libSQL), NuxtHub.
    - **Key Directories:**
        - `app/`: Frontend application code (pages, components, composables).
        - `server/`: Backend Nitro server (API routes, auth, database).
        - `shared/`: Shared types and utilities between frontend and server.
2.  **`research_agent/` (Backend):** A Python/Agno service running agentic workflows.
    - **Tech Stack:** Python 3.11+, Agno (formerly Phidata), FastAPI, AWS Bedrock (Amazon Nova), SQLAlchemy (SQLite).
    - **Key Agents:** `wide_researcher`, `deep_researcher`, `paper_reader`, `workflow_builder`, `title_generator`, `chat_agent`.
    - **Workflows:** `chained_research`, `literature_review`.

## Getting Started

### Prerequisites
- **Frontend:** Bun or Node.js/pnpm.
- **Backend:** Python 3.11+, `uv` (recommended).
- **Environment:** AWS credentials for Amazon Nova (Bedrock) and Clerk API keys.

### 1. Start the Agno Research Backend
```bash
cd research_agent
uv sync
cp .env.example .env # Configure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
mkdir -p tmp
uv run python main.py
```
The backend runs on `http://localhost:7777`.

### 2. Start the Nuxt Frontend
```bash
cd chat-app
bun install
cp .env.example .env # Configure Clerk and DB secrets
bun run dev
```
The application runs on `http://localhost:3000`.

## Development Conventions

- **Module Organization:**
    - `chat-app/app/pages/`: File-based routing.
    - `chat-app/app/components/`: UI components (PascalCase).
    - `chat-app/app/composables/`: Reusable logic (camelCase).
    - `chat-app/server/api/`: Nitro API endpoints.
    - `chat-app/server/db/schema.ts`: Drizzle schema definition.
- **Coding Style:**
    - 2-space indentation (enforced via `.editorconfig`).
    - Prefer TypeScript and Vue SFCs.
    - ESLint rules are in `chat-app/eslint.config.mjs`.
- **Database:**
    - Drizzle ORM is used for both local SQLite and production libSQL (NuxtHub).
    - Run `bun run db:generate` followed by `bun run db:migrate` after schema changes.
- **AI Integration:**
    - **Strategy:** Completely eliminated reliance on the Vercel AI SDK (`ai`).
    - **Orchestration:** The Agno research backend (`research_agent/`) is the only intelligence and orchestration layer.
    - **Implementation:** Both research workflows and standard chat use the Agno backend via the `useResearch` and `useChat` composables.

## Key Files & Contracts

- `chat-app/shared/types/research.d.ts`: Defines the contract between the Nuxt frontend and the Agno backend (SSE events, query types, results).
- `chat-app/server/api/research/run.post.ts`: The primary proxy route between the UI and the Agno backend.
- `research_agent/main.py`: Entry point for the Agno service.

## Testing & Validation

- `bun run lint`: Runs ESLint checks.
- `bun run typecheck`: Runs Nuxt and TypeScript type checks.
- Currently, there is no unit test suite; use linting and type-checking as pre-PR validation.
