# Nova Forge — System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   ingest.vue     │  │    graph.vue     │  │  Components  │  │
│  │                  │  │                  │  │              │  │
│  │ - Query Form     │  │ - Space Tabs     │  │ - Memory     │  │
│  │ - Presets        │  │ - Navigation     │  │   GraphWrap  │  │
│  │ - Job Polling    │  │ - Graph Display  │  │ - Error UI   │  │
│  │ - Results        │  │                  │  │              │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────────┘  │
│           │                     │                                │
│           └─────────────┬───────┘                                │
│                         │                                        │
│               Nuxt 4 + Vue 3 (TypeScript)                        │
│                         │                                        │
└─────────────────────────┼──────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
┌────────▼──────────┐     │     ┌──────────▼──────────┐
│  API LAYER        │     │     │  API LAYER          │
│ (Nuxt Server)     │     │     │ (FastAPI Backend)   │
├───────────────────┤     │     ├─────────────────────┤
│                   │     │     │                     │
│ POST /api/ingest  │     │     │ POST /ingest        │
│ GET /api/graph    │     │     │ GET /ingest/{id}    │
│                   │     │     │ GET /health         │
│                   │     │     │ GET /                │
│                   │     │     │                     │
└────────┬──────────┘     │     └──────────┬──────────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         PaSa Workflow (Orchestrator)                    │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ 1. Search Phase: ArxivClient                       │ │   │
│  │  │    - Query arXiv API                              │ │   │
│  │  │    - Retrieve papers with metadata                │ │   │
│  │  │    - Sort by relevance                            │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  │                           ↓                              │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ 2. Store Phase: SupermemoryService                │ │   │
│  │  │    - Store papers with metadata                   │ │   │
│  │  │    - Add tags and categories                      │ │   │
│  │  │    - Create searchable index                      │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  │                           ↓                              │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ 3. Analyze Phase: NovaLiteClient                  │ │   │
│  │  │    - Expand search queries                        │ │   │
│  │  │    - Generate synthesis                           │ │   │
│  │  │    - Score relevance                              │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  │                           ↓                              │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ 4. Return Results: IngestResult                   │ │   │
│  │  │    - Processed count                              │ │   │
│  │  │    - Stored papers list                           │ │   │
│  │  │    - Expansion queries                            │ │   │
│  │  │    - Synthesis summary                            │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
┌────────▼──────────┐     │     ┌──────────▼──────────┐
│   SERVICES LAYER  │     │     │  EXTERNAL APIs      │
├───────────────────┤     │     ├─────────────────────┤
│                   │     │     │                     │
│ NovaLiteClient    │────→│←────│ AWS Bedrock         │
│ - complete()      │     │     │ (Nova Lite Model)   │
│ - score_relevance │     │     │                     │
│                   │     │     │                     │
│ ArxivClient       │────→│←────│ arXiv API           │
│ - search()        │     │     │ - REST endpoints    │
│                   │     │     │ - Paper metadata    │
│                   │     │     │                     │
│ Supermemory       │────→│←────│ Supermemory API     │
│ Service           │     │     │ - Document storage  │
│ - add_paper()     │     │     │ - Graph operations  │
│ - get_documents() │     │     │                     │
│                   │     │     │                     │
└───────────────────┘     │     └─────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │  SQLite DB      │  │  Job Cache       │  │  Session Store │ │
│  │                 │  │                  │  │                │ │
│  │ - User data     │  │ - Job status     │  │ - User prefs   │ │
│  │ - Chat history  │  │ - Results        │  │ - Settings     │ │
│  │ - Documents     │  │ - Metadata       │  │                │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagrams

### 1. Paper Ingestion Flow

```
User Input
    ↓
┌─────────────────────────────────────┐
│ POST /api/ingest (Nuxt Server)      │
│ - query: string                     │
│ - container_tag: string             │
│ - max_candidates: number            │
│ - citation_expansion: boolean       │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ POST /ingest (Research Agent)       │
│ - Create job_id                     │
│ - Queue background task             │
│ - Return job_id immediately         │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Background Job Processing           │
│ Status: queued → processing         │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ PaSaWorkflow._run_async()           │
│ 1. Search papers (ArxivClient)      │
│ 2. Store results (SupermemoryServ)  │
│ 3. Build queries (NovaLiteClient)   │
│ 4. Synthesize summary (NovaLite)    │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Update Job Status                   │
│ Status: processing → completed      │
│ Progress: 0% → 100%                 │
│ Result: IngestResult object         │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Frontend Polling Loop               │
│ GET /ingest/{job_id}                │
│ Every 2 seconds                     │
│ Until status == completed           │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Display Results in Frontend         │
│ - Papers processed                  │
│ - Synthesis summary                 │
│ - Expansion queries                 │
│ - Link to graph view                │
└─────────────────────────────────────┘
```

### 2. Knowledge Graph Visualization Flow

```
User Navigates to /graph
            ↓
┌──────────────────────────────┐
│ graph.vue Component          │
│ - Select space (category)    │
│ - Mount MemoryGraphWrapper   │
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ MemoryGraphWrapper Component │
│ - Fetch documents on mount   │
│ - Setup pagination           │
│ - Watch space changes        │
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ GET /api/graph?space=X       │
│ &page=1&limit=20             │
│ (Nuxt Server)                │
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ GET Supermemory API          │
│ - Retrieve documents         │
│ - Filter by space/tags       │
│ - Return with metadata       │
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ Render MemoryGraph           │
│ - Display nodes              │
│ - Draw relationships         │
│ - Show labels                │
└──────────────────────────────┘
```

## 📦 Service Dependencies

```
PaSaWorkflow (Orchestrator)
    ├── NovaLiteClient
    │   ├── boto3
    │   └── AWS Bedrock API
    │
    ├── ArxivClient
    │   ├── arxiv library
    │   └── arXiv REST API
    │
    └── SupermemoryService
        ├── requests library
        └── Supermemory API

Frontend Components
    ├── Vue 3
    ├── Nuxt 4
    ├── TypeScript
    ├── Tailwind CSS
    └── @supermemory/memory-graph

Backend Infrastructure
    ├── FastAPI
    ├── Pydantic
    ├── SQLAlchemy
    ├── SQLite
    └── uvicorn
```

## 🔗 API Contract Specifications

### Request/Response: Paper Ingestion

```
REQUEST: POST /ingest
Content-Type: application/json

{
  "query": "machine learning algorithms",
  "container_tag": "ml-research",
  "max_candidates": 10,
  "citation_expansion": true
}

RESPONSE: 202 Accepted
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Request/Response: Job Status

```
REQUEST: GET /ingest/550e8400-e29b-41d4-a716-446655440000

RESPONSE (Processing): 200 OK
{
  "status": "processing",
  "progress": 45,
  "result": null,
  "error": null
}

RESPONSE (Completed): 200 OK
{
  "status": "completed",
  "progress": 100,
  "result": {
    "processed_count": 10,
    "stored_papers": ["2401.12345", "2401.67890", ...],
    "expansion_queries": ["query1", "query2", "query3"],
    "synthesis": "This research explores key themes..."
  },
  "error": null
}

RESPONSE (Failed): 200 OK
{
  "status": "failed",
  "progress": 0,
  "result": null,
  "error": "AWS Bedrock authentication failed"
}
```

### Request/Response: Graph Data

```
REQUEST: GET /api/graph?space=default&page=1&limit=20

RESPONSE: 200 OK
{
  "documents": [
    {
      "id": "2401.12345",
      "title": "Attention Is All You Need",
      "authors": ["Vaswani, A.", "Shazeer, N.", ...],
      "content": "...",
      "url": "https://arxiv.org/abs/2401.12345",
      "tags": ["attention", "transformer", "NLP"],
      "metadata": {...}
    },
    ...
  ],
  "page": 1,
  "limit": 20,
  "total": 250,
  "hasMore": true
}
```

## 🏛️ Component Hierarchy

### Frontend Component Tree

```
App (Nuxt Layout)
│
├── Dashboard Layout
│   └── Pages
│       ├── ingest.vue
│       │   ├── Form Elements
│       │   ├── Preset Buttons
│       │   ├── Log Display
│       │   └── Results Section
│       │
│       └── graph.vue
│           ├── Space Tabs Navigation
│           └── MemoryGraphWrapper.client.vue
│               ├── Loading State
│               ├── MemoryGraph Component
│               │   ├── Nodes
│               │   ├── Edges
│               │   └── Labels
│               ├── Error State
│               └── Load More Button
```

### Backend Module Structure

```
research_agent/
│
├── main.py (Application Root)
│   ├── FastAPI app initialization
│   ├── CORS configuration
│   ├── Database setup
│   └── Route registration
│
├── services/
│   ├── nova_bedrock.py
│   │   └── NovaLiteClient
│   ├── arxiv_client.py
│   │   ├── ArxivPaper (model)
│   │   └── ArxivClient
│   ├── supermemory.py
│   │   ├── Document (model)
│   │   └── SupermemoryService
│   └── __init__.py
│
├── workflows/
│   ├── pasa_workflow.py
│   │   ├── IngestRequest (model)
│   │   ├── IngestResult (model)
│   │   └── PaSaWorkflow
│   ├── chained_research.py
│   └── literature_review.py
│
├── agents/
│   ├── wide_researcher.py
│   ├── deep_researcher.py
│   ├── paper_reader.py
│   ├── workflow_builder.py
│   ├── title_generator.py
│   └── chat_agent.py
│
└── [Other existing modules]
```

## ⚡ Performance Architecture

### Bottlenecks & Optimizations

```
BOTTLENECK                    OPTIMIZATION
────────────────────────────  ──────────────────────────
arXiv API latency             Caching, batch queries
(2-5 seconds)                 Timeout handling

Nova Bedrock latency          Async/await
(3-10 seconds)                Queue for long tasks

Supermemory API calls         Batch operations
(100ms-1s per call)           Connection pooling

Database queries              Indexing
                              Connection pooling

Graph rendering               Pagination
(complex graphs)              Virtual scrolling

Paper metadata parsing        Pre-processing
                              Lazy loading
```

### Caching Strategy

```
Layer 1: Frontend Cache
    ├── Document cache (in-memory)
    └── Job results cache

Layer 2: Application Cache
    ├── Paper metadata
    ├── Expansion queries
    └── Synthesis results

Layer 3: Database Cache
    ├── SQLite full-text search
    └── Session storage

Layer 4: External Cache
    ├── arXiv paper metadata
    └── Supermemory graph
```

## 🔐 Security Architecture

```
INPUT VALIDATION
    ↓
Pydantic Models
    ├── IngestRequest validation
    ├── ArxivPaper validation
    └── Document validation
    ↓
AUTHENTICATION (Future)
    ↓
JWT Token Validation
    ├── User identification
    └── Permission check
    ↓
AUTHORIZATION (Future)
    ↓
Role-based Access Control
    ├── User permissions
    └── Resource access
    ↓
DATA PROTECTION
    ↓
Environment Variables
    ├── AWS credentials
    ├── API keys
    └── Database credentials
    ↓
HTTPS (Production)
    ↓
TLS Encryption
    ├── In-transit encryption
    └── Certificate validation
    ↓
ERROR HANDLING
    ↓
Sanitized Error Messages
    └── No sensitive data in errors
```

## 🚀 Deployment Architecture

### Development Environment
```
Local Machine
├── Python venv
├── Node.js + pnpm
├── SQLite database
├── .env file (local secrets)
└── Uvicorn server (reload enabled)
```

### Staging Environment
```
Staging Server
├── Python 3.11+
├── PostgreSQL database
├── Redis (job queue)
├── Gunicorn + Nginx
├── Environment variables (from secrets manager)
└── HTTPS + SSL certificate
```

### Production Environment
```
Production Cluster
├── Docker containers
├── Kubernetes orchestration
├── Load balancer
├── Multiple API instances
├── Managed PostgreSQL
├── AWS ElastiCache (Redis)
├── CloudFront CDN (frontend)
├── Route53 DNS
├── CloudWatch monitoring
├── Secrets Manager
└── VPC network isolation
```

## 📊 State Management

### Frontend State
```
ingest.vue
├── query (ref: string)
├── containerTag (ref: string)
├── mode (ref: "standard" | "expanded")
├── maxCandidates (ref: number)
├── jobId (ref: string | null)
├── logs (ref: string[])
├── result (ref: IngestResult | null)
└── polling (ref: boolean)

graph.vue
├── spaces (ref: Space[])
├── activeSpace (ref: string)
└── MemoryGraphWrapper
    ├── documents (ref: Document[])
    ├── isLoading (ref: boolean)
    ├── currentPage (ref: number)
    └── hasMore (ref: boolean)
```

### Backend State
```
main.py
└── ingest_jobs (dict)
    ├── job_id
    │   ├── status: "queued" | "processing" | "completed" | "failed"
    │   ├── progress: 0-100
    │   ├── result: IngestResult | null
    │   └── error: string | null
```

## 🔄 Event Flow

### User Actions → State Changes → Rendering

```
User clicks "Start Ingestion"
    ↓ (event)
startIngest() called
    ↓ (side effect)
POST /api/ingest
    ↓ (response)
jobId received
    ↓ (state update)
jobId.value = id
logs.value.push("Job started...")
polling = true
    ↓ (reactive)
Template re-renders
    ↓ (UI update)
Loading spinner shown
    ↓ (async loop)
pollJob() every 2s
GET /ingest/{jobId}
    ↓ (response)
status, progress, result
    ↓ (state update)
logs.value.push(status)
result.value = data
    ↓ (reactive)
Template re-renders
    ↓ (UI update)
Results displayed
```

## 📡 Message Passing & Communication

```
SYNCHRONOUS (Request/Response)
├── Frontend → Nuxt API: POST /api/ingest
├── Nuxt API → Research Agent: POST /ingest
└── Frontend → Nuxt API: GET /api/graph

ASYNCHRONOUS (Fire & Forget)
├── Frontend polling: GET /ingest/{id} every 2s
├── Backend job processing: Background task
└── Frontend event: Results ready

WEBHOOKS (Future)
├── Backend → Frontend: WebSocket connection
├── Job status updates: Real-time
└── Graph updates: Streaming data
```

## 🎯 Summary

The Nova Forge system is a well-architected, scalable solution that:

1. **Separates Concerns**: Services, workflows, APIs, and UI clearly separated
2. **Handles Concurrency**: Async/await throughout for non-blocking operations
3. **Validates Input**: Pydantic models enforce type safety
4. **Manages State**: Clear state flow from user input → processing → results
5. **Integrates Services**: Multiple external APIs orchestrated seamlessly
6. **Scales Horizontally**: Stateless API design ready for load balancing
7. **Provides Monitoring**: Logging and error tracking throughout

The architecture supports:
- ✅ Immediate development and testing
- ✅ Scaling to production
- ✅ Adding new services
- ✅ Integration with existing systems
- ✅ Performance optimization
- ✅ Security hardening