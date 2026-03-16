"""nova-forge backend — research + ideate features.

Research: wide/deep/read/chat/plan/run (Agentica-powered research agents)
Ideate:   5-phase arXiv paper → product opportunity pipeline (async job)
"""

from __future__ import annotations

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.chat_agent import run_chat_agent
from agents.deep_researcher import run_deep_researcher
from agents.paper_reader import run_paper_reader
from agents.title_generator import run_title_generator
from agents.wide_researcher import run_wide_researcher
from agents.workflow_builder import execute_builder_plan, run_workflow_builder
from errors import AgentExecutionError, AgenticaConnectionError
from ideate.pipeline import run_pipeline
from prompts import DEFAULT_MODEL
from workflows.chained_research import run_chained_research
from workflows.literature_review import run_literature_review

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="nova-forge",
    description="Research + Ideate backend powered by Agentica",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    stream: bool = True


class ResearchRequest(BaseModel):
    prompt: str
    stream: bool = True


class TitleRequest(BaseModel):
    message: str


class WorkflowRequest(BaseModel):
    goal: str
    workflow: str = "chained"  # "chained" or "literature"
    stream: bool = False


class BuilderRequest(BaseModel):
    prompt: str
    stream: bool = True
    execute: bool = False  # if True, run execute_builder_plan after getting the plan


class IdeateRequest(BaseModel):
    arxiv_id: str
    model: str = DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sse(gen) -> StreamingResponse:
    return StreamingResponse(gen, media_type="text/event-stream")


def _error_response(exc: Exception) -> dict:
    return {"error": str(exc), "type": type(exc).__name__}


# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "name": "nova-forge",
        "version": "0.2.0",
        "features": {
            "research": [
                "POST /research/chat",
                "POST /research/title",
                "POST /research/wide",
                "POST /research/deep",
                "POST /research/read",
                "POST /research/plan",
                "POST /research/run",
            ],
            "ideate": [
                "POST /ideate",
                "GET  /ideate/{job_id}",
            ],
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Research: single-agent endpoints
# ---------------------------------------------------------------------------

@app.post("/research/chat")
async def research_chat(req: ChatRequest):
    """General research chat agent."""
    try:
        result = await run_chat_agent(req.message, stream=req.stream)
        if req.stream:
            return _sse(result)
        return {"response": result}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/research/title")
async def research_title(req: TitleRequest):
    """Generate a short title for a research chat."""
    try:
        title = await run_title_generator(req.message)
        return {"title": title.strip()}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/research/wide")
async def research_wide(req: ResearchRequest):
    """Wide Researcher — breadth-first paper landscape scan."""
    try:
        result = await run_wide_researcher(req.prompt, stream=req.stream)
        if req.stream:
            return _sse(result)
        return {"response": result}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/research/deep")
async def research_deep(req: ResearchRequest):
    """Deep Researcher — depth-first paper analysis with TinyFish."""
    try:
        result = await run_deep_researcher(req.prompt, stream=req.stream)
        if req.stream:
            return _sse(result)
        return {"response": result}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/research/read")
async def research_read(req: ResearchRequest):
    """Paper Reader — 3-pass reading methodology."""
    try:
        result = await run_paper_reader(req.prompt, stream=req.stream)
        if req.stream:
            return _sse(result)
        return {"response": result}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/research/plan")
async def research_plan(req: BuilderRequest):
    """Workflow Builder — returns a research plan (with optional execution)."""
    try:
        plan = await run_workflow_builder(req.prompt, stream=req.stream)
        if req.stream and not req.execute:
            return _sse(plan)
        if req.stream:
            # Collect the plan text first (can't execute while streaming)
            plan_text = plan
        else:
            plan_text = plan

        if req.execute and isinstance(plan_text, str):
            result = await execute_builder_plan(plan_text, req.prompt)
            return {"plan": plan_text, "result": result}

        return {"plan": plan_text}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/research/run")
async def research_run(req: WorkflowRequest):
    """Run a multi-phase research workflow (chained or literature review).

    Runs synchronously — expect 3-8 minutes for full pipeline.
    Use background polling pattern for long-running UI.
    """
    try:
        if req.workflow == "literature":
            result = await run_literature_review(req.goal)
        else:
            result = await run_chained_research(req.goal)
        return {"result": result, "workflow": req.workflow}
    except (AgentExecutionError, AgenticaConnectionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


# ---------------------------------------------------------------------------
# Ideate: async job endpoints
# ---------------------------------------------------------------------------

# In-memory job store. Replace with Redis/DB for multi-process deployments.
_ideate_jobs: dict[str, dict] = {}


async def _run_ideate_job(job_id: str, req: IdeateRequest) -> None:
    _ideate_jobs[job_id]["status"] = "running"
    try:
        report = await run_pipeline(req.arxiv_id, model=req.model)
        _ideate_jobs[job_id] = {
            "status": "completed",
            "result": report,
            "error": None,
        }
    except Exception as exc:
        _ideate_jobs[job_id] = {
            "status": "failed",
            "result": None,
            "error": str(exc),
        }


@app.post("/ideate")
async def ideate(req: IdeateRequest, background_tasks: BackgroundTasks):
    """Start an ideation pipeline job for an arXiv paper.

    Returns a job_id to poll via GET /ideate/{job_id}.
    The pipeline takes 3-8 minutes.
    """
    job_id = str(uuid.uuid4())
    _ideate_jobs[job_id] = {"status": "queued", "result": None, "error": None}
    background_tasks.add_task(_run_ideate_job, job_id, req)
    return {"job_id": job_id}


@app.get("/ideate/{job_id}")
async def get_ideate_job(job_id: str):
    """Poll the status of an ideation pipeline job."""
    job = _ideate_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
