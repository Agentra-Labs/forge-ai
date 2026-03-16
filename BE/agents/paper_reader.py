"""Paper Reader Agent — Karpathy/Keshav 3-pass paper reading methodology.

Pure reasoning agent (no heavy tools). Receives paper content and produces
structured review cards using the 3-pass reading model.
"""

from __future__ import annotations

from typing import AsyncIterator

from backend import call_agent_text, spawn_agent, stream_agent_sse
from prompts import DEFAULT_MODEL, PAPER_READER_SYSTEM_PROMPT
from tools.openalex import openalex_get_paper, openalex_search_papers

_TOOLS = {
    "openalex_search_papers": openalex_search_papers,
    "openalex_get_paper": openalex_get_paper,
}


async def run_paper_reader(
    prompt: str,
    *,
    stream: bool = False,
) -> str | AsyncIterator[str]:
    """Run the Paper Reader using 3-pass reading methodology.

    Args:
        prompt: Paper content, abstract, or list of papers from wide scan.
        stream: If True, return an SSE async iterator.

    Returns:
        Full text response or async SSE iterator.
    """
    agent = await spawn_agent(
        premise=PAPER_READER_SYSTEM_PROMPT,
        model=DEFAULT_MODEL,
        scope=_TOOLS,
    )
    if stream:
        return stream_agent_sse(agent, prompt, phase="paper reader")
    return await call_agent_text(agent, prompt, phase="paper reader")
