"""Workflow Builder Agent — meta-orchestrator that plans research pipelines.

Analyzes user intent and returns a structured plan with SPAWN directives.
The execute_builder_plan() function parses those directives and dispatches
to the real agent functions.
"""

from __future__ import annotations

import re
from typing import AsyncIterator

from backend import call_agent_text, spawn_agent, stream_agent_sse
from prompts import BUILDER_SYSTEM_PROMPT, DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Spawn stub tools — the builder uses these to signal intent.
# Each returns a SPAWN directive string; execute_builder_plan() executes them.
# ---------------------------------------------------------------------------

def spawn_wide_scan(goal: str, keywords: str = "") -> str:
    """Spawn a Wide Researcher run for broad landscape coverage.

    Args:
        goal: What to scan for broadly.
        keywords: Optional comma-separated keywords to seed the search.

    Returns:
        Directive string confirming the wide scan has been queued.
    """
    prompt = goal
    if keywords:
        prompt += f"\n\nKeywords to prioritize: {keywords}"
    return f"[SPAWN:wide] {prompt}"


def spawn_deep_analysis(goal: str, urls: str = "", arxiv_ids: str = "") -> str:
    """Spawn a Deep Researcher run on specific papers or URLs.

    Args:
        goal: What to extract from the papers.
        urls: Comma-separated URLs to deep-analyse.
        arxiv_ids: Comma-separated ArXiv IDs to deep-analyse.

    Returns:
        Directive string confirming the deep analysis has been queued.
    """
    prompt = goal
    if urls:
        prompt += f"\n\nURLs to analyse: {urls}"
    if arxiv_ids:
        prompt += f"\n\nArXiv papers: {arxiv_ids}"
    return f"[SPAWN:deep] {prompt}"


def spawn_paper_reading(content: str, goal: str) -> str:
    """Spawn a Paper Reader run using the 3-pass methodology.

    Args:
        content: Raw paper text or abstract to review.
        goal: What the review should focus on.

    Returns:
        Directive string confirming the paper reading has been queued.
    """
    return (
        "[SPAWN:read] Review the following paper content using the 3-pass methodology. "
        "Base every statement strictly on this content; do not invent missing details.\n\n"
        f"Goal: {goal}\n\n"
        "[PAPER CONTENT START]\n"
        f"{content[:4000]}\n"
        "[PAPER CONTENT END]"
    )


def spawn_literature_review(topic: str) -> str:
    """Spawn a full Literature Review workflow (wide scan → reading → synthesis).

    Args:
        topic: The research topic for the full review.

    Returns:
        Directive string confirming the literature review has been queued.
    """
    return f"[SPAWN:literature-review] {topic}"


def spawn_chained_research(goal: str, seed_paper: str = "") -> str:
    """Spawn the Chained Research workflow (wide → reader → deep pipeline).

    Args:
        goal: The research goal for the chained pipeline.
        seed_paper: Optional ArXiv ID or URL to seed the wide scan.

    Returns:
        Directive string confirming the chained research workflow has been queued.
    """
    prompt = goal
    if seed_paper:
        prompt += f"\n\nSeed paper: {seed_paper}"
    return f"[SPAWN:chained-research] {prompt}"


_TOOLS = {
    "spawn_wide_scan": spawn_wide_scan,
    "spawn_deep_analysis": spawn_deep_analysis,
    "spawn_paper_reading": spawn_paper_reading,
    "spawn_literature_review": spawn_literature_review,
    "spawn_chained_research": spawn_chained_research,
}


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

async def run_workflow_builder(
    prompt: str,
    *,
    stream: bool = False,
) -> str | AsyncIterator[str]:
    """Run the Workflow Builder to plan a research pipeline.

    Args:
        prompt: User's research request.
        stream: If True, return an SSE async iterator of the plan text.

    Returns:
        Builder plan text (with SPAWN directives) or async SSE iterator.
    """
    agent = await spawn_agent(
        premise=BUILDER_SYSTEM_PROMPT,
        model=DEFAULT_MODEL,
        scope=_TOOLS,
    )
    if stream:
        return stream_agent_sse(agent, prompt, phase="workflow builder")
    return await call_agent_text(agent, prompt, phase="workflow builder")


# ---------------------------------------------------------------------------
# Execution layer: parse SPAWN directives and delegate to real agents
# ---------------------------------------------------------------------------

async def execute_builder_plan(
    builder_response: str,
    original_goal: str,
) -> str:
    """Parse SPAWN directives from the builder's response and run the real agents.

    Runs each spawned agent in sequence and concatenates their outputs.

    Args:
        builder_response: Full builder plan text with [SPAWN:...] directives.
        original_goal: The original user goal (used for workflow fallback).

    Returns:
        Combined output from all spawned agents.
    """
    # Lazy imports to avoid circular deps
    from agents.wide_researcher import run_wide_researcher
    from agents.deep_researcher import run_deep_researcher
    from agents.paper_reader import run_paper_reader
    from workflows.chained_research import run_chained_research
    from workflows.literature_review import run_literature_review

    directives = re.findall(
        r"\[SPAWN:([^\]]+)\] (.+?)(?=\[SPAWN:|$)",
        builder_response,
        re.DOTALL,
    )

    if not directives:
        return builder_response

    parts: list[str] = []
    for action, payload in directives:
        action = action.strip()
        payload = payload.strip()

        header = f"\n\n---\n**Phase: {action.replace('-', ' ').title()}**\n\n"

        if action == "wide":
            result = await run_wide_researcher(payload)
        elif action == "deep":
            result = await run_deep_researcher(payload)
        elif action == "read":
            result = await run_paper_reader(payload)
        elif action == "chained-research":
            result = await run_chained_research(payload)
        elif action == "literature-review":
            result = await run_literature_review(payload)
        else:
            result = f"[Unknown action: {action}]"

        parts.append(header + result)

    return "\n".join(parts)
