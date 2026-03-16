"""Deep Researcher Agent — depth-first paper analysis.

Takes a shortlist of papers and extracts full content: methods, results,
ablations, code links, failure modes. Returns goal-conditioned structured
extraction. Uses TinyFish and OpenAlex tools.
"""

from __future__ import annotations

from typing import AsyncIterator

from backend import call_agent_text, spawn_agent, stream_agent_sse
from prompts import DEEP_SYSTEM_PROMPT, DEFAULT_MODEL
from tools.openalex import openalex_get_paper, openalex_search_papers
from tools.tinyfish_tools import (
    tinyfish_deep_paper,
    tinyfish_extract,
    tinyfish_extract_competition,
)

_TOOLS = {
    "openalex_search_papers": openalex_search_papers,
    "openalex_get_paper": openalex_get_paper,
    "tinyfish_extract": tinyfish_extract,
    "tinyfish_deep_paper": tinyfish_deep_paper,
    "tinyfish_extract_competition": tinyfish_extract_competition,
}


async def run_deep_researcher(
    prompt: str,
    *,
    stream: bool = False,
) -> str | AsyncIterator[str]:
    """Run the Deep Researcher for depth-first paper analysis.

    Args:
        prompt: Research goal, paper URLs, or ArXiv IDs to analyze.
        stream: If True, return an SSE async iterator.

    Returns:
        Full text response or async SSE iterator.
    """
    agent = await spawn_agent(
        premise=DEEP_SYSTEM_PROMPT,
        model=DEFAULT_MODEL,
        scope=_TOOLS,
    )
    if stream:
        return stream_agent_sse(agent, prompt, phase="deep researcher")
    return await call_agent_text(agent, prompt, phase="deep researcher")
