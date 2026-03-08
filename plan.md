# Forge x Amazon Nova Hackathon Plan

## Why this plan changed
This revision is based on a broader scan of the actual codebase, not just the landing page and README. The repo already contains:

- a polished Nuxt chat workspace in `chat-app/app/pages/dashboard.vue` and `chat-app/app/pages/chat/[id].vue`
- a separate research SSE path in `chat-app/server/api/research/run.post.ts` and `chat-app/app/composables/useResearch.ts`
- existing multimodal-style file upload support for images, PDFs, and CSVs in `chat-app/shared/utils/file.ts`
- latent research UI pieces such as `chat-app/app/components/ResearchStream.vue` and `chat-app/app/components/PaperCard.vue`

The important finding is that Forge is already halfway to a hackathon-worthy research agent, but the implementation is split across two parallel systems that are not yet unified.

## Hackathon fit
Based on the Amazon Nova Devpost overview and resources pages:

- core requirement: use **Amazon Nova foundation models and/or Nova Act**
- strongest category fit: **Agentic AI**
- strongest secondary differentiators: **Multimodal Understanding** and a narrow **UI Automation** workflow
- judging emphasis: **Technical Implementation 60%**, **Impact 20%**, **Creativity and Innovation 20%**
- the page explicitly calls out innovative multi-agent systems under creativity
- deadline listed: **March 16, 2026 at 5:00pm PDT**

Sources:
- https://amazon-nova.devpost.com/
- https://amazon-nova.devpost.com/resources

## Current codebase assessment
### What is already strong
- The user experience is already focused on research, not generic chat.
- `deep` vs `wide` modes are already first-class in the UI and prompt handling.
- File upload is already built and supports exactly the kinds of inputs a multimodal research demo needs.
- The chat page already shows reasoning and can host richer research artifacts.
- A dedicated research stream UI already exists and displays step-by-step progress.

### What is currently weak
- The app currently runs **two independent backends** per query:
  - the normal AI SDK chat pipeline in `chat-app/server/api/chats/[id].post.ts`
  - the Agno research pipeline in `chat-app/server/api/research/run.post.ts`
- Those outputs are shown side by side but are not truly merged into one agent workflow.
- The DB only persists `users`, `chats`, and `messages` in `chat-app/server/db/schema.ts`; research runs, citations, evidence, and artifacts are not stored.
- Model selection in `chat-app/shared/utils/models.ts` does not include Amazon Nova.
- The title generator is still hardcoded to `openai/gpt-4o-mini`.
- `chat-app/package.json` has no Bedrock or AWS-specific integration yet, so Nova support is not a small config tweak.
- Existing tools are demo-oriented (`weather`, `chart`) rather than hackathon-relevant research tools.
- `PaperCard.vue` and the richer research typing in `shared/types/research.d.ts` are present but not fully connected to the user flow.
- Uploads are blob-first and not tracked in the DB, so there is no ingestion pipeline, retrieval index, or cleanup story for abandoned pre-chat uploads.
- `shared/types/research.d.ts` and `server/api/research/run.post.ts` already support a `chained` workflow mode, but the UI only exposes `deep` and `wide`.

## Best submission angle
### Submit as: Agentic AI
Do not reposition Forge as a voice app or as pure browser automation. The strongest entry is:

**Forge Nova**: an agentic research workspace that ingests multimodal evidence, runs a visible multi-agent analysis flow, produces a defendable recommendation, and optionally prepares execution via Nova Act.

This keeps the main idea intact and uses the codebase’s real strengths instead of forcing a different product.

## Core product upgrade
Replace the current “chat response + separate research stream” pattern with one unified Nova-centered workflow:

1. user asks a research question and optionally uploads files
2. Forge runs named internal agents
3. intermediate steps stream into the existing research UI
4. the final answer is stored as part of the conversation
5. citations, extracted evidence, and artifacts are visible and reusable
6. an optional Nova Act step turns the recommendation into a real follow-up action

The winning version of Forge is not “more models in a dropdown.” It is “one coherent research-to-decision system.”

## Recommended implementation roadmap
### Phase 1: Make Nova the real backend, not a badge
Primary goal: remove eligibility risk and anchor the demo in Amazon Nova.

Changes:
- Add Nova model entries to `chat-app/shared/utils/models.ts`.
- Make Nova the default in `chat-app/app/composables/useModels.ts`.
- Update `chat-app/app/components/ModelSelect.vue` to visually prioritize Nova.
- Replace provider-specific assumptions in `chat-app/server/api/chats/[id].post.ts`.
- Remove the hardcoded `openai/gpt-4o-mini` title generation path and switch title generation onto the same Nova stack.
- Add AWS/Nova runtime config and env documentation alongside `.env.example`.
- Add the Bedrock/AWS dependencies and wiring that are currently missing from `chat-app/package.json`.

Why:
- This directly serves the 60% technical score.
- It prevents the project from feeling like “a generic AI SDK app with Nova added at the last minute.”

### Phase 2: Unify the two intelligence paths
Primary goal: stop running chat and research as disconnected systems.

Current issue:
- `chat-app/app/pages/chat/[id].vue` sends one request into the chat transport and a second request into `useResearch()` in parallel.

Recommended fix:
- Turn the research path into the primary orchestration layer.
- Use a single backend route for research-grade responses.
- Stream structured events for:
  - planning
  - evidence gathering
  - verification
  - synthesis
  - final recommendation
- Persist the final output into chat history so the conversation remains the system of record.

Implementation options:
- either upgrade `server/api/research/run.post.ts` into the canonical path and make chat consume it
- or fold the research orchestration into `server/api/chats/[id].post.ts` and keep one route surface

Recommendation:
- keep `/api/research/run` as the orchestration layer and make the chat page treat it as the primary engine
- reduce the standard chat pipeline to a thin persistence/presentation layer

Why:
- This is the single biggest product improvement available in the repo.
- It will also make the demo easier to explain.

### Phase 2.5: Expose the existing chained workflow as a fast win
Primary goal: unlock a more agentic story quickly while the deeper unification work is underway.

Changes:
- Extend `chat-app/app/composables/useResearchMode.ts` to expose `chained`.
- Update `chat-app/app/components/ResearchModeMenu.vue` and `chat-app/app/components/ResearchModeSwitch.vue` to surface that mode.
- Map `chained` in the chat page and research UI to the existing workflow support already present in `server/api/research/run.post.ts`.

Why:
- This gives the demo a more explicit multi-step agent narrative with relatively low UI effort.
- It uses capability that already exists in the backend contract instead of inventing a new mode from scratch.

### Phase 3: Make the agent system visible
Primary goal: score on creativity without inventing unnecessary features.

Reuse the existing `ResearchStream.vue` surface and make the pipeline explicit:

- **Scout agent**: expands the question, identifies sources, extracts file contents
- **Reviewer agent**: checks claims, limitations, contradictions, and confidence
- **Synthesizer agent**: writes the recommendation with tradeoffs
- **Operator agent**: turns the recommendation into follow-up actions

UI work:
- keep `ResearchStream.vue` for step progress
- reuse and connect `PaperCard.vue` for reviewed evidence
- add a compact evidence rail or section in `chat-app/app/pages/chat/[id].vue`
- show:
  - top sources
  - extracted claims
  - limitations
  - confidence
  - recommended next step

Why:
- The repo already contains the start of this UX.
- Judges need to see the agent architecture, not infer it.

### Phase 4: Turn upload support into judged multimodal capability
Primary goal: convert an existing feature into a differentiator.

The app already accepts:
- `image/*`
- `application/pdf`
- `.csv`

Use that to support a strong research workflow:
- PDFs: paper ingestion, summary extraction, claim extraction, limitation extraction
- images/screenshots: diagrams, benchmark screenshots, requirements screenshots
- CSVs: benchmark tables, experiment logs, cost/performance comparisons
- move from “blob URL attached to prompt” to “ingest, parse, store metadata, and retrieve”
- add cleanup or expiration handling for pre-chat uploads that never become real conversations

Output should not be generic prose. It should produce:
- recommendation
- evidence matrix
- tradeoffs
- risks
- unanswered questions
- next experiment or implementation step

This is stronger than adding new input types because it builds on functionality already in the app.

### Phase 5: Replace demo tools with hackathon-relevant tools
Primary goal: avoid shipping a research product that still exposes placeholder weather tooling.

Current tool layer:
- `shared/utils/tools/weather.ts`
- `shared/utils/tools/chart.ts`

Recommended replacements:
- keep `chartTool`, but reposition it for benchmark visualization and comparison tables
- remove or deprioritize `weatherTool`
- add research-native tools such as:
  - evidence table generator
  - benchmark comparison/chart builder
  - citation pack generator
  - task brief generator

Why:
- Tooling should reinforce the research-use case and the hackathon narrative.

### Phase 6: Persist research artifacts in the database
Primary goal: make the app feel like a real workspace instead of a streaming demo.

Extend `chat-app/server/db/schema.ts` with new entities such as:
- `research_runs`
- `research_steps`
- `evidence_items`
- `artifacts`

What to store:
- source type and source URL
- extracted claim
- limitation or uncertainty note
- agent that produced it
- confidence score
- run status
- final synthesis

Why:
- It enables replay, auditability, and better UI.
- It supports the “defendable recommendation” story better than raw markdown alone.
- It also fixes the current weakness where uploads, research steps, and evidence exist outside durable application state.

### Phase 7: Add one narrow Nova Act workflow
Primary goal: gain extra upside without destabilizing the product.

Do not build a general web automation platform. Add one constrained bridge from research to action:

- after a final recommendation, user clicks `Prepare execution`
- Nova Act performs one limited flow:
  - draft a GitHub issue from the recommendation
  - draft a Jira ticket
  - fill a project brief form
  - populate a comparison sheet

This should remain a second-step feature, not the heart of the app.

Why:
- It gives the project a stronger end-to-end story
- It creates UI Automation upside while keeping Agentic AI as the main category

## Concrete file-level priorities
### Highest leverage files
- `chat-app/app/pages/chat/[id].vue`
- `chat-app/server/api/research/run.post.ts`
- `chat-app/server/api/chats/[id].post.ts`
- `chat-app/server/db/schema.ts`
- `chat-app/shared/utils/models.ts`
- `chat-app/app/composables/useResearch.ts`
- `chat-app/app/components/ResearchStream.vue`
- `chat-app/app/components/PaperCard.vue`

### Likely new files
- `chat-app/server/api/research/artifacts/*.ts`
- `chat-app/server/api/research/runs/*.ts`
- `chat-app/server/utils/research/*`
- `chat-app/app/components/research/*`

## Best demo scenario
Use one concrete engineering decision:

“A team needs to decide which browser-agent reliability approach to adopt. They upload a benchmark CSV, two paper PDFs, and a screenshot of internal requirements. Forge Nova runs scout/reviewer/synthesizer agents, produces a recommendation with evidence and limitations, generates a comparison chart, and then prepares a GitHub issue or Jira ticket through Nova Act.”

This demo uses what the codebase already supports:
- uploads
- chat workspace
- progress streaming
- chart rendering

## Scope control
### Must-have
- Nova integration
- unified research orchestration
- visible multi-agent steps
- multimodal evidence handling
- evidence/citation UI
- polished end-to-end demo

### Nice-to-have
- persisted artifacts and run history
- benchmark charts from uploaded CSV
- expose `chained` mode end to end if it is not completed in the must-have pass
- one execution handoff via Nova Act

### Stretch
- voice briefing mode
- multi-run comparison dashboard
- multiple automation targets

## What will improve win probability most
If time is tight, prioritize in this order:

1. remove the split architecture and make Forge feel like one coherent system
2. make Nova central and obvious in both code and demo
3. show visible agent steps with evidence, not just a final paragraph
4. use the existing upload pipeline for a compelling multimodal scenario
5. add one narrow execution workflow instead of several shallow features

## Bottom line
The best hackathon version of this repo is not a rebrand. It is a consolidation:

- unify the chat and research paths
- put Amazon Nova at the center
- turn existing uploads and research UI into a real multi-agent evidence workflow
- add one action-taking step at the end

That approach keeps Forge’s main idea unchanged and materially increases the odds of scoring well on technical implementation, impact, and creativity.
