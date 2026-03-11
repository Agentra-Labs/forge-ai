# Nova Forge — Academic Intelligence Engine
### Amazon Nova AI Hackathon Submission · Agentic AI Category

> *"Two rivers, one ocean."* Deep and Wide research modes unified by a living knowledge graph — powered by Amazon Nova 2 Lite, Supermemory, and agno.

---

## 0. The Pitch (60 seconds)

Researchers drown in papers. Nova Forge is a **self-expanding academic intelligence engine** that:

1. Accepts a natural-language research intent ("long-term memory in LLMs")
2. Deploys a **PaSa-style dual agent** (Crawler + Selector) powered by **Amazon Nova 2 Lite** to autonomously search arXiv, score relevance, and follow citation trails
3. Stores every accepted paper in **Supermemory** with semantic clustering by topic (`containerTag`)
4. Renders a **live, navigable knowledge galaxy** via `@supermemory/memory-graph` — dandelion subgraphs per research thread
5. Exposes **Deep / Wide** research chat (your forge-ai DNA) sitting *on top of* the graph — so every answer is grounded in a curated, growing paper corpus

**Hackathon alignment**: Uses Nova 2 Lite (Bedrock) for agent reasoning + Nova multimodal embeddings for figure-level semantic clustering. Category: Agentic AI. Also touches Multimodal Understanding (PDF figures).

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NOVA FORGE                               │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────────────────────────┐   │
│  │  Nuxt/Vue   │    │          Python / FastAPI             │   │
│  │  Frontend   │    │                                       │   │
│  │             │    │  ┌─────────────────────────────────┐  │   │
│  │  /graph     │◄───┼──│  agno Workflow: PaSa Agent      │  │   │
│  │  (MemGraph) │    │  │                                  │  │   │
│  │             │    │  │  ┌──────────┐  ┌─────────────┐  │  │   │
│  │  /research  │    │  │  │ Crawler  │  │  Selector   │  │  │   │
│  │  (Deep/Wide)│    │  │  │ Agent    │  │  Agent      │  │  │   │
│  │             │    │  │  │          │  │             │  │  │   │
│  │  /ingest    │    │  │  │ arXiv    │  │ Nova 2 Lite │  │  │   │
│  │  (trigger)  │    │  │  │ API      │  │ via Bedrock │  │  │   │
│  └──────┬──────┘    │  │  └────┬─────┘  └──────┬──────┘  │  │   │
│         │           │  │       │                │          │  │   │
│         │ /api/graph│  │       └────────────────┘          │  │   │
│         │ /api/ingest│  │              │                    │  │   │
│         │           │  │              ▼                    │  │   │
│         │           │  │  ┌─────────────────────────────┐  │  │   │
│         │           │  │  │      Supermemory SDK         │  │  │   │
│         │           │  │  │  documents.add(pdf_url,      │  │  │   │
│         │           │  │  │    containerTag=topic)       │  │  │   │
│         │           │  │  └─────────────────────────────┘  │  │   │
│         │           │  └─────────────────────────────────┘  │   │
│         │           │                                       │   │
│         │           │  ┌─────────────────────────────────┐  │   │
│         └───────────┼──│  /api/graph  (proxy to SM API)  │  │   │
│                     │  │  /api/ingest (trigger agent)     │  │   │
│                     │  │  /api/search (SM search + Nova)  │  │   │
│                     │  └─────────────────────────────────┘  │   │
│                     └──────────────────────────────────────┘   │
│                                                                 │
│  External: Supermemory API  │  Amazon Bedrock  │  arXiv API    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User query: "memory-augmented transformers"
     │
     ▼
Crawler Agent: arxiv.search(query, max_results=50)
     │  returns: [Paper(title, abstract, id, authors, categories)]
     ▼
Selector Agent (Nova 2 Lite):
  For each paper → "Is this directly relevant? Score 1-10. Reason."
  Accept if score >= 7
     │  returns: [AcceptedPaper, ...]
     ▼
Expander (optional, Deep mode):
  For each accepted paper → extract key cited works → re-run Selector
     │
     ▼
For each final paper:
  supermemory.documents.add(
    content = "https://arxiv.org/pdf/{id}.pdf",
    containerTag = "arxiv-{topic-slug}",
    metadata = { title, arxiv_id, authors, published, categories }
  )
     │
     ▼
Frontend: GET /api/graph?space=arxiv-{topic-slug}
  → MemoryGraph renders dandelion visualization
```

---

## 2. Repository Layout

```
nova-forge/
├── chat-app/                    # Nuxt/Vue frontend (forge-ai DNA)
│   ├── pages/
│   │   ├── index.vue            # Landing / dashboard
│   │   ├── graph.vue            # MemoryGraph visualization
│   │   ├── research.vue         # Deep/Wide chat interface
│   │   └── ingest.vue           # Trigger ingestion UI
│   ├── server/api/
│   │   ├── graph.get.ts         # Proxy to Supermemory, filter by space
│   │   ├── ingest.post.ts       # Trigger Python agent via HTTP
│   │   └── search.post.ts       # SM semantic search + Nova synthesis
│   ├── components/
│   │   ├── MemoryGraphWrapper.client.vue
│   │   ├── ResearchChat.vue
│   │   ├── SpaceSelector.vue
│   │   └── IngestPanel.vue
│   └── nuxt.config.ts
│
├── agent/                       # Python agent service
│   ├── main.py                  # FastAPI app
│   ├── agents/
│   │   ├── crawler.py           # arXiv search agent (agno)
│   │   ├── selector.py          # Nova 2 Lite relevance scorer
│   │   └── pasa_workflow.py     # agno Workflow orchestrating both
│   ├── services/
│   │   ├── supermemory.py       # SM client wrapper
│   │   ├── nova_bedrock.py      # Bedrock client (Nova 2 Lite)
│   │   └── arxiv_client.py      # arXiv search wrapper
│   └── requirements.txt
│
└── scripts/
    └── ingest-batch.py          # One-shot CLI ingestion script
```

---

## 3. Setup

### 3.1 Prerequisites

```bash
# Accounts / keys needed:
# - AWS account with Bedrock access (Nova 2 Lite enabled in us-east-1)
# - Supermemory account → https://console.supermemory.ai
# - arXiv API: no key needed

# AWS CLI configured
aws configure
# Or set:
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

### 3.2 Environment Variables

```env
# agent/.env
SUPERMEMORY_API_KEY=sm_...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
NOVA_MODEL_ID=us.amazon.nova-lite-v1:0

# chat-app/.env
SUPERMEMORY_API_KEY=sm_...
AGENT_SERVICE_URL=http://localhost:8000
```

### 3.3 Agent Service Setup

```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

`requirements.txt`:
```
fastapi
uvicorn
agno>=0.1.0
arxiv
supermemory
boto3
pydantic
python-dotenv
```

### 3.4 Frontend Setup

```bash
cd chat-app
bun install
bun run dev
```

---

## 4. Core Code

### 4.1 Nova 2 Lite Client (`agent/services/nova_bedrock.py`)

```python
import json
import boto3
from typing import Any

class NovaLiteClient:
    """Amazon Nova 2 Lite via Bedrock Converse API."""

    def __init__(self, model_id: str = "us.amazon.nova-lite-v1:0", region: str = "us-east-1"):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        response = self.client.converse(
            modelId=self.model_id,
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": user}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": 0.1},
        )
        return response["output"]["message"]["content"][0]["text"]

    def score_relevance(self, query: str, title: str, abstract: str) -> dict[str, Any]:
        """Returns {score: int, reason: str, accept: bool}"""
        system = """You are a rigorous academic paper selector. 
Given a research query and a paper's title + abstract, score relevance 1-10.
Respond ONLY with valid JSON: {"score": <int>, "reason": "<one sentence>", "accept": <bool>}
Accept (true) if score >= 7."""

        user = f"""Research query: {query}

Paper title: {title}

Abstract: {abstract[:800]}"""

        raw = self.complete(system, user, max_tokens=200)
        try:
            # Strip markdown fences if present
            raw = raw.strip().strip("```json").strip("```").strip()
            return json.loads(raw)
        except Exception:
            return {"score": 0, "reason": "parse error", "accept": False}
```

### 4.2 arXiv Client (`agent/services/arxiv_client.py`)

```python
import arxiv
from dataclasses import dataclass
from typing import Optional

@dataclass
class ArxivPaper:
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    published: str
    categories: list[str]
    pdf_url: str

class ArxivClient:
    def search(self, query: str, max_results: int = 50) -> list[ArxivPaper]:
        client = arxiv.Client(num_retries=3, delay_seconds=3)
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = []
        for r in client.results(search):
            results.append(ArxivPaper(
                arxiv_id=r.entry_id.split("/")[-1],
                title=r.title.strip(),
                abstract=r.summary.strip(),
                authors=[a.name for a in r.authors[:5]],
                published=r.published.strftime("%Y-%m-%d"),
                categories=r.categories,
                pdf_url=r.pdf_url,
            ))
        return results
```

### 4.3 Supermemory Service (`agent/services/supermemory.py`)

```python
import os
from supermemory import Supermemory

class SupermemoryService:
    def __init__(self):
        self.client = Supermemory(api_key=os.environ["SUPERMEMORY_API_KEY"])

    def add_paper(self, paper, container_tag: str) -> dict:
        """Ingest an arXiv paper into Supermemory."""
        doc = self.client.documents.add(
            content=paper.pdf_url,
            container_tags=[container_tag],
            metadata={
                "title": paper.title,
                "arxiv_id": paper.arxiv_id,
                "authors": ", ".join(paper.authors),
                "published": paper.published,
                "categories": ", ".join(paper.categories),
                "source": "arxiv",
            }
        )
        return doc

    def get_documents(self, container_tag: str | None = None, page: int = 1, limit: int = 100) -> dict:
        import requests, os
        headers = {
            "Authorization": f"Bearer {os.environ['SUPERMEMORY_API_KEY']}",
            "Content-Type": "application/json",
        }
        body = {"page": page, "limit": limit, "sort": "createdAt", "order": "desc"}
        if container_tag:
            body["containerTag"] = container_tag
        resp = requests.post(
            "https://api.supermemory.ai/v3/documents/documents",
            headers=headers, json=body
        )
        return resp.json()
```

### 4.4 PaSa-Style agno Workflow (`agent/agents/pasa_workflow.py`)

```python
import asyncio
from dataclasses import dataclass, field
from typing import AsyncGenerator
from agno.workflow import Workflow, RunResponse, RunEvent
from agno.agent import Agent
from agno.models.aws import Claude  # or use custom Nova provider

from services.nova_bedrock import NovaLiteClient
from services.arxiv_client import ArxivClient, ArxivPaper
from services.supermemory import SupermemoryService

@dataclass
class IngestRequest:
    query: str
    container_tag: str
    max_candidates: int = 50
    citation_expansion: bool = False  # Deep mode toggle
    min_score: int = 7

@dataclass  
class IngestResult:
    accepted: list[str] = field(default_factory=list)
    rejected: int = 0
    ingested: int = 0
    container_tag: str = ""
    summary: str = ""

class PaSaWorkflow(Workflow):
    """
    PaSa-inspired: Crawler → Selector (Nova 2 Lite) → [Expander] → Supermemory
    
    Wide mode: Crawler only, shallow pass, fast
    Deep mode: Crawler + Expander (citation-trail following via additional searches)
    """

    description: str = "Academic paper discovery and ingestion workflow"

    def run(self, request: IngestRequest) -> AsyncGenerator[RunResponse, None]:
        return self._run_async(request)

    async def _run_async(self, req: IngestRequest) -> AsyncGenerator[RunResponse, None]:
        nova = NovaLiteClient()
        arxiv = ArxivClient()
        sm = SupermemoryService()

        yield RunResponse(
            event=RunEvent.workflow_started,
            content=f"🔍 Crawling arXiv for: '{req.query}'"
        )

        # ── PHASE 1: CRAWL ──────────────────────────────────────────
        candidates = arxiv.search(req.query, max_results=req.max_candidates)
        
        yield RunResponse(
            event=RunEvent.run_response,
            content=f"📄 Found {len(candidates)} candidates. Scoring with Nova 2 Lite..."
        )

        # ── PHASE 2: SELECT (Nova 2 Lite relevance scoring) ─────────
        accepted: list[ArxivPaper] = []
        rejected = 0

        for paper in candidates:
            result = nova.score_relevance(req.query, paper.title, paper.abstract)
            if result.get("accept"):
                accepted.append(paper)
                yield RunResponse(
                    event=RunEvent.run_response,
                    content=f"✅ [{result['score']}/10] {paper.title[:70]}..."
                )
            else:
                rejected += 1

        # ── PHASE 3: EXPAND (Deep mode — citation trail) ────────────
        if req.citation_expansion and accepted:
            yield RunResponse(
                event=RunEvent.run_response,
                content=f"🕸️ Deep mode: expanding via citation trails..."
            )
            # Extract key terms from accepted paper titles for related searches
            expansion_queries = self._build_expansion_queries(accepted[:5], nova, req.query)
            for eq in expansion_queries[:3]:  # Cap at 3 expansion searches
                extra = arxiv.search(eq, max_results=20)
                for paper in extra:
                    if paper.arxiv_id not in {p.arxiv_id for p in accepted}:
                        result = nova.score_relevance(req.query, paper.title, paper.abstract)
                        if result.get("accept"):
                            accepted.append(paper)

        # ── PHASE 4: INGEST → SUPERMEMORY ───────────────────────────
        yield RunResponse(
            event=RunEvent.run_response,
            content=f"💾 Ingesting {len(accepted)} papers into Supermemory ({req.container_tag})..."
        )

        ingested = 0
        for paper in accepted:
            try:
                sm.add_paper(paper, req.container_tag)
                ingested += 1
            except Exception as e:
                yield RunResponse(
                    event=RunEvent.run_response,
                    content=f"⚠️ Failed to ingest {paper.arxiv_id}: {e}"
                )

        # ── PHASE 5: SUMMARIZE (Nova 2 Lite) ────────────────────────
        summary = self._synthesize_summary(nova, req.query, accepted[:10])

        yield RunResponse(
            event=RunEvent.workflow_completed,
            content=IngestResult(
                accepted=[p.title for p in accepted],
                rejected=rejected,
                ingested=ingested,
                container_tag=req.container_tag,
                summary=summary,
            )
        )

    def _build_expansion_queries(
        self, papers: list[ArxivPaper], nova: NovaLiteClient, original_query: str
    ) -> list[str]:
        """Ask Nova 2 Lite to generate related search queries from accepted papers."""
        titles = "\n".join(f"- {p.title}" for p in papers)
        prompt = f"""Original query: {original_query}

Accepted papers:
{titles}

Generate 3 arXiv search queries to find closely related work not yet covered.
Respond with JSON array of strings: ["query1", "query2", "query3"]"""

        raw = nova.complete(
            system="You are a research assistant. Respond ONLY with a JSON array of 3 search queries.",
            user=prompt,
            max_tokens=200
        )
        try:
            raw = raw.strip().strip("```json").strip("```").strip()
            import json
            return json.loads(raw)
        except Exception:
            return []

    def _synthesize_summary(
        self, nova: NovaLiteClient, query: str, papers: list[ArxivPaper]
    ) -> str:
        titles = "\n".join(f"- {p.title} ({p.published})" for p in papers)
        return nova.complete(
            system="You are a research synthesis assistant. Be concise and insightful.",
            user=f"""Query: {query}

Top papers ingested:
{titles}

Write a 3-sentence synthesis: main themes, key contributions, and notable clusters.""",
            max_tokens=300
        )
```

### 4.5 FastAPI Service (`agent/main.py`)

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio, uuid

load_dotenv()

from agents.pasa_workflow import PaSaWorkflow, IngestRequest

app = FastAPI(title="Nova Forge Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (use Redis/DB in production)
jobs: dict[str, dict] = {}

class IngestPayload(BaseModel):
    query: str
    container_tag: str
    max_candidates: int = 50
    citation_expansion: bool = False

@app.post("/ingest")
async def ingest(payload: IngestPayload, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "logs": [], "result": None}

    async def run():
        workflow = PaSaWorkflow()
        request = IngestRequest(
            query=payload.query,
            container_tag=payload.container_tag,
            max_candidates=payload.max_candidates,
            citation_expansion=payload.citation_expansion,
        )
        async for event in workflow.run(request):
            if isinstance(event.content, str):
                jobs[job_id]["logs"].append(event.content)
            else:
                jobs[job_id]["result"] = event.content.__dict__
                jobs[job_id]["status"] = "done"

    background_tasks.add_task(run)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/health")
def health():
    return {"status": "ok", "model": "us.amazon.nova-lite-v1:0"}
```

---

### 4.6 Nuxt API: Graph Route (`chat-app/server/api/graph.get.ts`)

```typescript
import { defineEventHandler, getQuery, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const { space, page = '1', limit = '150' } = getQuery(event)

  const body: Record<string, unknown> = {
    page: parseInt(page as string),
    limit: parseInt(limit as string),
    sort: 'createdAt',
    order: 'desc',
  }

  if (space && space !== 'all') {
    body.containerTag = space as string
  }

  const response = await fetch('https://api.supermemory.ai/v3/documents/documents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.SUPERMEMORY_API_KEY}`,
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw createError({
      statusCode: response.status,
      message: 'Supermemory API error',
    })
  }

  return response.json()
})
```

### 4.7 Nuxt API: Ingest Route (`chat-app/server/api/ingest.post.ts`)

```typescript
import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  const agentUrl = process.env.AGENT_SERVICE_URL ?? 'http://localhost:8000'
  const response = await fetch(`${agentUrl}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  return response.json()
})
```

### 4.8 MemoryGraph Vue Wrapper (`chat-app/components/MemoryGraphWrapper.client.vue`)

```vue
<script setup lang="ts">
// .client.vue = Nuxt auto-skips SSR for this component (canvas needs browser)
import { ref, onMounted, watch } from 'vue'
// @ts-ignore — no types yet for this pkg
import { MemoryGraph } from '@supermemory/memory-graph'
import '@supermemory/memory-graph/dist/style.css'

const props = defineProps<{
  space: string
}>()

const documents = ref([])
const isLoading = ref(true)
const isLoadingMore = ref(false)
const hasMore = ref(false)
const error = ref(null)
const currentPage = ref(1)
const LIMIT = 150

async function fetchDocs(page: number, append = false) {
  try {
    page === 1 ? (isLoading.value = true) : (isLoadingMore.value = true)
    const params = new URLSearchParams({
      page: String(page),
      limit: String(LIMIT),
      space: props.space,
    })
    const data = await $fetch(`/api/graph?${params}`)
    if (append) {
      documents.value = [...documents.value, ...data.documents]
    } else {
      documents.value = data.documents ?? []
    }
    hasMore.value = data.pagination
      ? data.pagination.currentPage < data.pagination.totalPages
      : false
  } catch (e: any) {
    error.value = e
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

async function loadMore() {
  if (!isLoadingMore.value && hasMore.value) {
    currentPage.value++
    await fetchDocs(currentPage.value, true)
  }
}

onMounted(() => fetchDocs(1))
watch(() => props.space, () => {
  currentPage.value = 1
  fetchDocs(1)
})
</script>

<template>
  <div style="height: 100%; width: 100%">
    <MemoryGraph
      :documents="documents"
      :is-loading="isLoading"
      :is-loading-more="isLoadingMore"
      :has-more="hasMore"
      :total-loaded="documents.length"
      :load-more-documents="loadMore"
      :error="error"
      variant="console"
      :show-spaces-selector="true"
    />
  </div>
</template>
```

### 4.9 Graph Page (`chat-app/pages/graph.vue`)

```vue
<script setup lang="ts">
import { ref } from 'vue'

// Predefined topic spaces — grows as user ingests
const spaces = ref([
  { id: 'all', label: 'All Papers' },
  { id: 'arxiv-llm-memory', label: 'LLM Memory' },
  { id: 'arxiv-multimodal', label: 'Multimodal' },
  { id: 'arxiv-agents', label: 'Agents' },
  { id: 'arxiv-quantum-gnn', label: 'Quantum GNN' },
])

const activeSpace = ref('all')
</script>

<template>
  <div class="graph-page">
    <!-- Topic tabs -->
    <nav class="space-tabs">
      <button
        v-for="space in spaces"
        :key="space.id"
        :class="['tab', { active: activeSpace === space.id }]"
        @click="activeSpace = space.id"
      >
        {{ space.label }}
      </button>
    </nav>

    <!-- Full-screen graph canvas — .client.vue skips SSR automatically -->
    <div class="graph-canvas">
      <MemoryGraphWrapper :space="activeSpace" />
    </div>
  </div>
</template>

<style scoped>
.graph-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0a0a0f;
  color: #e8e8e8;
}

.space-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  background: #0f0f1a;
  border-bottom: 1px solid #1e1e2e;
  overflow-x: auto;
}

.tab {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid #2a2a3e;
  background: transparent;
  color: #888;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab.active {
  background: #f59e0b22;
  border-color: #f59e0b;
  color: #f59e0b;
}

.graph-canvas {
  flex: 1;
  overflow: hidden;
}
</style>
```

### 4.10 Ingest Page (`chat-app/pages/ingest.vue`)

```vue
<script setup lang="ts">
import { ref } from 'vue'

const query = ref('')
const containerTag = ref('arxiv-llm-memory')
const mode = ref<'wide' | 'deep'>('wide')
const maxCandidates = ref(50)
const jobId = ref<string | null>(null)
const logs = ref<string[]>([])
const result = ref<any>(null)
const polling = ref(false)

const presets = [
  { label: 'LLM Memory', tag: 'arxiv-llm-memory', query: 'large language model long-term memory continual learning' },
  { label: 'Multimodal', tag: 'arxiv-multimodal', query: 'multimodal vision language model' },
  { label: 'Agents', tag: 'arxiv-agents', query: 'LLM agent autonomous planning tool use' },
]

async function startIngest() {
  logs.value = ['🚀 Starting Nova Forge ingestion...']
  result.value = null

  const res = await $fetch('/api/ingest', {
    method: 'POST',
    body: {
      query: query.value,
      container_tag: containerTag.value,
      max_candidates: maxCandidates.value,
      citation_expansion: mode.value === 'deep',
    }
  })

  jobId.value = res.job_id
  polling.value = true
  pollJob()
}

async function pollJob() {
  if (!jobId.value || !polling.value) return
  const job = await $fetch(`${useRuntimeConfig().public.agentUrl}/jobs/${jobId.value}`)

  logs.value = job.logs ?? []
  if (job.status === 'done') {
    result.value = job.result
    polling.value = false
  } else {
    setTimeout(pollJob, 1500)
  }
}

function applyPreset(p: typeof presets[0]) {
  query.value = p.query
  containerTag.value = p.tag
}
</script>

<template>
  <div class="ingest-page">
    <h1 class="title">Nova Forge — Ingest Papers</h1>

    <div class="presets">
      <button v-for="p in presets" :key="p.tag" class="preset-btn" @click="applyPreset(p)">
        {{ p.label }}
      </button>
    </div>

    <div class="form">
      <label>Research Query</label>
      <input v-model="query" placeholder="e.g. memory-augmented transformers" />

      <label>Topic Tag (containerTag)</label>
      <input v-model="containerTag" placeholder="arxiv-topic-name" />

      <label>Mode</label>
      <div class="mode-toggle">
        <button :class="{ active: mode === 'wide' }" @click="mode = 'wide'">⚡ Wide</button>
        <button :class="{ active: mode === 'deep' }" @click="mode = 'deep'">🔬 Deep</button>
      </div>

      <label>Max Candidates: {{ maxCandidates }}</label>
      <input v-model.number="maxCandidates" type="range" min="10" max="100" step="10" />

      <button class="ingest-btn" :disabled="!query" @click="startIngest">
        🔍 Run PaSa Agent
      </button>
    </div>

    <!-- Live log stream -->
    <div v-if="logs.length" class="log-panel">
      <div v-for="(log, i) in logs" :key="i" class="log-line">{{ log }}</div>
    </div>

    <!-- Result card -->
    <div v-if="result" class="result-card">
      <h3>✅ Ingestion Complete</h3>
      <p><strong>Ingested:</strong> {{ result.ingested }} papers → <code>{{ result.container_tag }}</code></p>
      <p><strong>Rejected:</strong> {{ result.rejected }}</p>
      <blockquote>{{ result.summary }}</blockquote>
      <NuxtLink :to="`/graph?space=${result.container_tag}`" class="view-graph-btn">
        View Knowledge Graph →
      </NuxtLink>
    </div>
  </div>
</template>
```

---

## 5. nuxt.config.ts Additions

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    supermemoryApiKey: process.env.SUPERMEMORY_API_KEY,
    public: {
      agentUrl: process.env.AGENT_SERVICE_URL ?? 'http://localhost:8000',
    },
  },
  // @supermemory/memory-graph uses canvas — needs browser-only
  build: {
    transpile: ['@supermemory/memory-graph'],
  },
})
```

`package.json` addition:
```json
{
  "dependencies": {
    "@supermemory/memory-graph": "latest"
  }
}
```

---

## 6. One-Shot CLI Ingestion (`scripts/ingest-batch.py`)

```python
#!/usr/bin/env python3
"""
Quick CLI for seeding initial paper graphs before demo.
Usage: python scripts/ingest-batch.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'agent', '.env'))

from agents.pasa_workflow import PaSaWorkflow, IngestRequest

SEED_TOPICS = [
    {
        "query": "large language model long-term memory episodic memory continual learning",
        "container_tag": "arxiv-llm-memory",
        "max_candidates": 40,
        "citation_expansion": False,
    },
    {
        "query": "multimodal vision language model image understanding",
        "container_tag": "arxiv-multimodal",
        "max_candidates": 30,
        "citation_expansion": False,
    },
    {
        "query": "LLM agent autonomous tool use planning ReAct",
        "container_tag": "arxiv-agents",
        "max_candidates": 30,
        "citation_expansion": False,
    },
]

async def main():
    workflow = PaSaWorkflow()
    for topic in SEED_TOPICS:
        print(f"\n{'='*60}")
        print(f"Topic: {topic['container_tag']}")
        print(f"{'='*60}")
        req = IngestRequest(**topic)
        async for event in workflow.run(req):
            if isinstance(event.content, str):
                print(event.content)
            else:
                r = event.content
                print(f"\n📊 Result: {r.ingested} ingested, {r.rejected} rejected")
                print(f"🧠 Summary: {r.summary}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 7. Hackathon Differentiators

| Dimension | What Nova Forge does |
|-----------|---------------------|
| **Nova 2 Lite** | Every relevance score, expansion query, and synthesis runs through Nova 2 Lite on Bedrock — not a peripheral integration, it's the cognitive core |
| **Agentic AI** | True dual-agent PaSa architecture: Crawler (arXiv) + Selector (Nova) + optional Expander — async, streaming, background jobs |
| **Multimodal** | Nova multimodal embeddings can embed paper figures/tables (future: PDF → image chunks → Nova embed → richer SM graph edges) |
| **Real-world impact** | Researchers save 10+ hours per literature review; teams share living knowledge graphs instead of static Notion pages |
| **forge-ai DNA** | Deep mode (full citation expansion) / Wide mode (fast scan) maps exactly to your existing product positioning |

---

## 8. Next Steps / Extensions

### 8.1 Multi-Agent Delegation (agno sub-agents)
```python
# In pasa_workflow.py — spawn specialized sub-agents per domain
crawler_agent = Agent(name="CrawlerAgent", ...)
selector_agent = Agent(name="SelectorAgent", model=nova_lite, ...)
# agno's team/delegation API wires them together
```

### 8.2 Nova Multimodal Embeddings for Figure Clustering
```python
# Extract PDF page images → embed with Nova multimodal
import boto3
bedrock = boto3.client("bedrock-runtime")
response = bedrock.invoke_model(
    modelId="amazon.titan-embed-image-v1",  # or nova embed when GA
    body=json.dumps({"inputImage": base64_page})
)
# Store embedding in SM metadata → richer graph edges
```

### 8.3 Search + Highlight Flow
```typescript
// In research.vue — after user asks a question:
const { ids } = await $fetch('/api/search', { method: 'POST', body: { query } })
// Pass to graph:
highlightDocumentIds.value = ids
// MemoryGraph lights up the relevant paper nodes
```

### 8.4 Nova Act for UI Automation (bonus prize angle)
```
Nova Act agent automates: open arxiv.org → run search → scrape results 
→ feed to Selector → ingest without any API
```

---

## 9. Demo Script (3-min video)

1. **0:00** — Show the empty graph page (beautiful dark canvas)
2. **0:20** — Go to Ingest, type "memory-augmented transformers", select Wide mode, hit Run
3. **0:35** — Watch live log stream: "Found 47 candidates... ✅ [8/10] Memorizing Transformers..."
4. **1:10** — Jump to Graph page, watch papers materialize as dandelion clusters
5. **1:40** — Switch topic tab: LLM Memory → Agents → see different subgraphs
6. **2:00** — Research chat: ask "What's the best architecture for episodic memory in LLMs?" → Nova-grounded answer
7. **2:30** — Deep mode demo: re-ingest with citation expansion, watch graph grow
8. **2:50** — Narrate: "Nova 2 Lite is the cognitive core — every decision, every synthesis"

---

*Nova Forge — turning the infinite arxiv into a navigable knowledge galaxy.*