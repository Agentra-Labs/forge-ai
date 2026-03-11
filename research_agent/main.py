"""Forge Research Agent — AgentOS entry point.

Serves 3 core agents + 2 workflows via AgentOS on port 7777.
Custom FastAPI routes for CORS and the `/research/run` proxy endpoint.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

# Add the research_agent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.chat_agent import chat_agent
from agents.deep_researcher import deep_researcher
from agents.paper_reader import paper_reader
from agents.title_generator import title_generator
from agents.wide_researcher import wide_researcher
from agents.workflow_builder import workflow_builder
from services.arxiv_client import ArxivClient
from services.nova_bedrock import NovaLiteClient
from services.supermemory import SupermemoryService
from workflows.chained_research import chained_research_workflow
from workflows.literature_review import literature_review_workflow
from workflows.pasa_workflow import IngestRequest, PaSaWorkflow

load_dotenv()

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

db = SqliteDb(db_file="tmp/forge_research.db")

# Attach DB to agents for session persistence
wide_researcher.db = db
deep_researcher.db = db
paper_reader.db = db
workflow_builder.db = db
title_generator.db = db
chat_agent.db = db


# ---------------------------------------------------------------------------
# Custom FastAPI app with CORS
# ---------------------------------------------------------------------------

base_app = FastAPI(
    title="Forge Research Agent",
    description="Agno-powered research paper discovery and synthesis backend",
    version="0.1.0",
)

base_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Nuxt dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@base_app.get("/")
async def root():
    return {
        "name": "Forge Research Agent",
        "version": "0.1.0",
        "agents": [
            "wide-researcher",
            "deep-researcher",
            "paper-reader",
            "workflow-builder",
            "title-generator",
            "chat-agent",
        ],
        "workflows": ["chained-research", "literature-review"],
    }


@base_app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Ingest Processing Jobs
# ---------------------------------------------------------------------------

# In-memory storage for job statuses (in production, use Redis or database)
ingest_jobs = {}


# ---------------------------------------------------------------------------
# Ingest Endpoint
# ---------------------------------------------------------------------------


class IngestPayload(IngestRequest):
    pass


async def run_ingest_job(job_id: str, request: IngestRequest):
    """Background task to run the ingestion process."""
    try:
        # Update job status
        ingest_jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "result": None,
            "error": None,
        }

        # Initialize services
        nova_client = NovaLiteClient()
        arxiv_client = ArxivClient()
        supermemory_service = SupermemoryService()
        workflow = PaSaWorkflow(nova_client, arxiv_client, supermemory_service)

        # Run workflow
        result = workflow.run(request)

        # Update job status
        ingest_jobs[job_id] = {
            "status": "completed",
            "progress": 100,
            "result": result.model_dump(),
            "error": None,
        }
    except Exception as e:
        # Update job status with error
        ingest_jobs[job_id] = {
            "status": "failed",
            "progress": 0,
            "result": None,
            "error": str(e),
        }


@base_app.post("/ingest")
async def ingest(payload: IngestPayload, background_tasks: BackgroundTasks) -> dict:
    """Start ingestion process."""
    import uuid

    job_id = str(uuid.uuid4())

    # Initialize job
    ingest_jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "result": None,
        "error": None,
    }

    # Start background task
    background_tasks.add_task(run_ingest_job, job_id, payload)

    return {"job_id": job_id}


@base_app.get("/ingest/{job_id}")
async def get_job(job_id: str) -> dict:
    """Get job status."""
    if job_id not in ingest_jobs:
        return {"error": "Job not found"}
    return ingest_jobs[job_id]


# ---------------------------------------------------------------------------
# AgentOS
# ---------------------------------------------------------------------------

agent_os = AgentOS(
    description="Forge AI Research Agent — 3 core agents + workflow builder + workflows for paper discovery and synthesis",
    agents=[
        wide_researcher,
        deep_researcher,
        paper_reader,
        workflow_builder,
        title_generator,
        chat_agent,
    ],
    workflows=[chained_research_workflow, literature_review_workflow],
    on_route_conflict="preserve_base_app",
    config=os.path.join(os.path.dirname(__file__), "agentos.yaml"),
)

app = agent_os.get_app()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Ensure tmp directory exists for SQLite
    os.makedirs("tmp", exist_ok=True)

    agent_os.serve(
        app="main:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
