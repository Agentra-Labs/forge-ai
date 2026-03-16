"""Title Generator Agent — short chat titles."""

from __future__ import annotations

from backend import call_agent_text, spawn_agent
from prompts import DEFAULT_MODEL, TITLE_SYSTEM_PROMPT


async def run_title_generator(message: str) -> str:
    """Generate a short title for a research chat message.

    Args:
        message: User message to generate a title from.

    Returns:
        Short plain-text title (< 30 chars).
    """
    agent = await spawn_agent(premise=TITLE_SYSTEM_PROMPT, model=DEFAULT_MODEL)
    return await call_agent_text(agent, message, phase="title")
