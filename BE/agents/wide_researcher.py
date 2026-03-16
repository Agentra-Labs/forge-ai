"""Wide Researcher Agent — breadth-first paper discovery.

Surveys the research landscape broadly using OpenAlex and kernel.sh.
"""

from __future__ import annotations

from typing import AsyncIterator

from backend import call_agent_text, spawn_agent, stream_agent_sse
from prompts import DEFAULT_MODEL, WIDE_SYSTEM_PROMPT
from tools.kernel_tools import kernel_parallel_scrape, kernel_scrape_url
from tools.openalex import (
    openalex_citations,
    openalex_get_paper,
    openalex_recommendations,
    openalex_references,
    openalex_search_papers,
)

_TOOLS = {
    "openalex_search_papers": openalex_search_papers,
    "openalex_get_paper": openalex_get_paper,
    "openalex_recommendations": openalex_recommendations,
    "openalex_citations": openalex_citations,
    "openalex_references": openalex_references,
    "kernel_scrape_url": kernel_scrape_url,
    "kernel_parallel_scrape": kernel_parallel_scrape,
}


async def run_wide_researcher(
    prompt: str,
    *,
    stream: bool = False,
) -> str | AsyncIterator[str]:
    """Run the Wide Researcher for broad paper landscape discovery.

    Args:
        prompt: Research goal or seed query.
        stream: If True, return an SSE async iterator.

    Returns:
        Full text response or async SSE iterator.
    """
    agent = await spawn_agent(
        premise=WIDE_SYSTEM_PROMPT,
        model=DEFAULT_MODEL,
        scope=_TOOLS,
    )
    if stream:
        return stream_agent_sse(agent, prompt, phase="wide researcher")
    return await call_agent_text(agent, prompt, phase="wide researcher")
