"""Custom Workflow Builder Agent — meta-orchestrator that dynamically spawns research pipelines.

Analyzes the user's intent and available context (seed papers, URLs, files, keywords)
then decides which agents and steps to invoke — wide, deep, chained, or a custom
sequence. Produces a structured WorkflowPlan that the AgentOS can execute.
"""

from __future__ import annotations

from typing import AsyncIterator

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools import tool

from agents.wide_researcher import wide_researcher
from agents.deep_researcher import deep_researcher
from agents.paper_reader import paper_reader


# ---------------------------------------------------------------------------
# Internal "spawn" tools the builder uses to delegate work
# ---------------------------------------------------------------------------

@tool()
def spawn_wide_scan(goal: str, keywords: str = "") -> str:
    """Spawn a Wide Researcher run for broad landscape coverage.

    Args:
        goal: What to scan for broadly.
        keywords: Optional comma-separated keywords to seed the search.

    Returns:
        Confirmation that the wide scan has been queued.
    """
    prompt = goal
    if keywords:
        prompt += f"\n\nKeywords to prioritize: {keywords}"
    return f"[SPAWN:wide] {prompt}"


@tool()
def spawn_deep_analysis(goal: str, urls: str = "", arxiv_ids: str = "") -> str:
    """Spawn a Deep Researcher run on specific papers or URLs.

    Args:
        goal: What to extract from the papers.
        urls: Comma-separated URLs to deep-analyse.
        arxiv_ids: Comma-separated ArXiv IDs to deep-analyse.

    Returns:
        Confirmation that the deep analysis has been queued.
    """
    prompt = goal
    if urls:
        prompt += f"\n\nURLs to analyse: {urls}"
    if arxiv_ids:
        prompt += f"\n\nArXiv papers: {arxiv_ids}"
    return f"[SPAWN:deep] {prompt}"


@tool()
def spawn_paper_reading(content: str, goal: str) -> str:
    """Spawn a Paper Reader run using the 3-pass methodology on provided content.

    Args:
        content: Raw paper text or abstract to review.
        goal: What the review should focus on (relevance criterion).

    Returns:
        Confirmation that the paper reading has been queued.
    """
    return f"[SPAWN:read] goal={goal}\n\n{content[:4000]}"


@tool()
def spawn_literature_review(topic: str) -> str:
    """Spawn a full Literature Review workflow (wide scan → reading → synthesis).

    Args:
        topic: The research topic for the full review.

    Returns:
        Confirmation that the literature review workflow has been queued.
    """
    return f"[SPAWN:lit-review] {topic}"


@tool()
def spawn_chained_research(goal: str, seed_paper: str = "") -> str:
    """Spawn the Chained Research workflow (wide → reader → deep pipeline).

    Args:
        goal: The research goal for the chained pipeline.
        seed_paper: Optional ArXiv ID or URL to seed the wide scan.

    Returns:
        Confirmation that the chained research workflow has been queued.
    """
    prompt = goal
    if seed_paper:
        prompt += f"\n\nSeed paper: {seed_paper}"
    return f"[SPAWN:chained] {prompt}"


# ---------------------------------------------------------------------------
# Builder Agent
# ---------------------------------------------------------------------------

BUILDER_SYSTEM_PROMPT = """You are the Workflow Builder — a meta-orchestrator that analyzes
the user's research request and dynamically chooses the optimal sequence of agents to run.

**YOU DO NOT DO THE RESEARCH YOURSELF.** You plan and delegate.

**SCENARIO → WORKFLOW DECISIONS:**

| Scenario | Recommended workflow |
|----------|---------------------|
| Vague question, no context | `spawn_wide_scan` first, then `spawn_chained_research` |
| Has a seed ArXiv paper | `spawn_deep_analysis` on the seed, then `spawn_wide_scan` for landscape |
| Has a list of URLs | `spawn_deep_analysis` on each URL |
| Has a PDF or document | `spawn_paper_reading` on the content, then `spawn_wide_scan` for context |
| Wants a field survey | `spawn_literature_review` directly |
| Wants a specific comparison | `spawn_deep_analysis` + `spawn_wide_scan` in parallel framing |
| Complex multi-step question | `spawn_chained_research` (handles wide → read → deep automatically) |
| Has competition/challenge context | `spawn_deep_analysis` on competition page, then `spawn_wide_scan` for solutions |

**YOUR PROCESS:**
1. Read the user's request carefully — exactly what do they want to know?
2. Identify what context they have provided: seed papers, URLs, files, keywords
3. Identify what they are missing: landscape knowledge, deep paper content, synthesis
4. Select the minimal set of spawn calls needed to fill all gaps
5. Call spawn tools in the right logical order (broad before deep, seed before landscape)
6. After spawning, produce a **Research Plan** explaining:
   - what you are doing and why
   - what each spawned agent will contribute
   - what the final output will look like

**IMPORTANT RULES:**
- Prefer `spawn_chained_research` for general questions — it covers the full pipeline
- Use `spawn_literature_review` only for explicit survey/review requests
- Do not spawn more than 4 agents for a single query — quality over quantity
- Always explain your reasoning to the user in plain language
- Never start an answer with a heading

**OUTPUT FORMAT:**
After calling spawn tools, write a short plan like:
"I'm running [X] to [purpose], then [Y] to [purpose]. You'll see intermediate results
as each phase completes. The final output will include [deliverables]."
"""

workflow_builder = Agent(
    id="workflow-builder",
    name="Workflow Builder",
    model=AwsBedrock(id="amazon.nova-lite-v1:0"),
    tools=[
        spawn_wide_scan,
        spawn_deep_analysis,
        spawn_paper_reading,
        spawn_literature_review,
        spawn_chained_research,
    ],
    instructions=BUILDER_SYSTEM_PROMPT,
    markdown=True,
    add_datetime_to_context=True,
)


# ---------------------------------------------------------------------------
# Execution layer: parse spawn directives and delegate to real agents
# ---------------------------------------------------------------------------

async def execute_builder_plan(
    builder_response: str,
    original_goal: str,
) -> AsyncIterator[str]:
    """Parse SPAWN directives from the builder's response and run the real agents.

    Yields streamed content from each spawned agent as it completes.
    """
    import re

    directives = re.findall(r"\[SPAWN:([^\]]+)\] (.+?)(?=\[SPAWN:|$)", builder_response, re.DOTALL)

    if not directives:
        # Builder wrote a plan but no directives — just return the plan as-is
        yield builder_response
        return

    for action, payload in directives:
        action = action.strip()
        payload = payload.strip()

        yield f"\n\n---\n**Phase: {action.replace('-', ' ').title()}**\n"

        if action == "wide":
            async for chunk in wide_researcher.arun(payload, stream=True):
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        elif action == "deep":
            async for chunk in deep_researcher.arun(payload, stream=True):
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        elif action == "read":
            async for chunk in paper_reader.arun(payload, stream=True):
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        elif action in ("lit-review", "chained"):
            # These require the full workflows — yield a handoff note
            yield (
                f"Running the **{action}** workflow — this will proceed through "
                f"multiple phases. Use the `/api/research/run` endpoint with "
                f"`workflow={action}` and `goal={original_goal!r}` for the full pipeline."
            )
