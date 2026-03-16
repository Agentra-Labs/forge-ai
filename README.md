# Forge

Forge is a research-first AI workspace built to turn papers, benchmarks, and technical signals into decisions a product or engineering team can act on.

The current app lives in [`FE/`](./FE) and is structured around two research modes:

- `Deep Research`: follow a focused question through methods, evidence, tradeoffs, and the strongest available answer.
- `Wide Research`: scan the landscape quickly across papers, labs, and solution families before deciding where to go deeper.

## Product Shape

The public landing page frames Forge as a research agent for engineering and product teams.

The app workspace is built around:

- a dashboard for starting new research threads
- a threaded chat interface for continuing investigation
- file upload and model selection inside the composer
- deep/wide mode switching directly inside the input workflow

## Repository Layout

- [`FE/`](./FE): Nuxt application for the Forge landing page, chat interface, and proxy API
- [`BE/`](./BE): Python/Agno backend running the agentic workflow on Amazon Nova (AWS Bedrock)
- [`LICENSE`](./LICENSE): repository license

## Local Development

Forge runs as a two-part system: a Nuxt frontend and a Python/Agno backend.

### 1. Start the Agno Research Backend
The backend requires AWS credentials to access Amazon Nova models via Bedrock.

```bash
cd BE

# Install dependencies using uv
uv sync

# Configure your environment variables
cp .env.example .env
# Edit .env and add your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION

# Create the sqlite database directory
mkdir -p tmp

# Start the AgentOS server (runs on port 7777)
uv run python main.py
```

### 2. Start the Nuxt Frontend
In a new terminal window:

```bash
cd FE
bun install
bun run dev
```

The application will be available at `http://localhost:3000`.

### Tooling Commands (Frontend)

```bash
cd FE
bun run typecheck
bun run lint
bun run build
```

## Positioning

Forge is designed for questions like:

- Which planning architecture is holding up best for browser agents?
- What do recent papers say about hallucination reduction strategies?
- Which benchmark results actually matter for this implementation decision?
- What is the strongest recommendation once evidence and tradeoffs are compared?

The goal is not just to summarize research. The goal is to turn research into clear direction.
