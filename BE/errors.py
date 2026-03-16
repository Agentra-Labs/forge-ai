"""Error classes for the research agent."""

from __future__ import annotations


class AgentExecutionError(Exception):
    """Raised when an agent execution fails."""

    pass


class AgenticaConnectionError(Exception):
    """Raised when connection to Agentica backend fails."""

    pass
