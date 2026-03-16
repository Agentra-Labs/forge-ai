"""Chat Agent — general research assistant."""

from __future__ import annotations

from typing import AsyncIterator

from backend import call_agent_text, spawn_agent, stream_agent_sse
from prompts import CHAT_SYSTEM_PROMPT, DEFAULT_MODEL


async def run_chat_agent(
    message: str,
    *,
    stream: bool = False,
) -> str | AsyncIterator[str]:
    """Run the general research chat agent.

    Args:
        message: User message.
        stream: If True, return an SSE async iterator; otherwise return full text.

    Returns:
        Full text response or async SSE iterator.
    """
    agent = await spawn_agent(premise=CHAT_SYSTEM_PROMPT, model=DEFAULT_MODEL)
    if stream:
        return stream_agent_sse(agent, message, phase="chat")
    return await call_agent_text(agent, message, phase="chat")
