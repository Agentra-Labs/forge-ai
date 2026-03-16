"""Backend abstraction for Agentica execution."""

from __future__ import annotations

import asyncio
import json
import os
from typing import AsyncIterator

import httpx
from agentica import spawn
from agentica.logging import set_default_agent_listener

from errors import AgentExecutionError, AgenticaConnectionError

SPAWN_TIMEOUT_SECONDS = 30.0


def _agent_logs_enabled() -> bool:
    return os.getenv("ENABLE_AGENT_LOGS", "0").strip().lower() in {"1", "true", "yes"}


def _get_phase_timeout_seconds() -> float:
    default = 360.0
    raw_value = os.getenv("AGENT_PHASE_TIMEOUT_SECONDS", str(default))
    try:
        value = float(raw_value)
    except ValueError:
        return default
    return max(30.0, value)


def _agentica_connection_help() -> str:
    base_url = os.getenv("AGENTICA_BASE_URL", "https://api.platform.symbolica.ai")
    session_manager_url = os.getenv("S_M_BASE_URL")
    target = session_manager_url or base_url
    return (
        "Timed out while connecting to the Agentica backend. "
        f"Current target: {target}. "
        "Check outbound network access, verify the backend URL, or set "
        "S_M_BASE_URL to a reachable local session manager."
    )


async def spawn_agent(**kwargs):
    """Spawn an agent with timeout handling."""
    if not _agent_logs_enabled():
        set_default_agent_listener(None)
    
    try:
        return await asyncio.wait_for(
            spawn(**kwargs),
            timeout=SPAWN_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        raise AgenticaConnectionError(
            f"Timed out after {SPAWN_TIMEOUT_SECONDS}s waiting for Agentica "
            f"to create an agent. {_agentica_connection_help()}"
        ) from exc
    except httpx.TimeoutException as exc:
        raise AgenticaConnectionError(_agentica_connection_help()) from exc
    except httpx.HTTPError as exc:
        raise AgenticaConnectionError(
            f"Agentica request failed while creating an agent: {exc}"
        ) from exc


def _format_agent_error(phase: str, exc: BaseException) -> str:
    if isinstance(exc, asyncio.TimeoutError):
        return (
            f"{phase} timed out inside Agentica while finalizing the response. "
            "This is usually a transient Agentica invocation timeout."
        )
    return f"{phase} failed with {exc.__class__.__name__}: {exc}"


async def call_agent_text(
    agent,
    prompt: str,
    *,
    phase: str = "agent",
) -> str:
    """Call an agent and return the full text response."""
    try:
        return await asyncio.wait_for(
            agent.call(str, prompt),
            timeout=_get_phase_timeout_seconds(),
        )
    except BaseException as exc:
        raise AgentExecutionError(_format_agent_error(phase, exc)) from exc
    finally:
        close = getattr(agent, "close", None)
        if close is not None:
            try:
                await asyncio.wait_for(asyncio.shield(close()), timeout=5.0)
            except Exception:
                pass


async def stream_agent_sse(
    agent,
    prompt: str,
    *,
    phase: str = "agent",
) -> AsyncIterator[str]:
    """Call an agent and yield SSE-formatted chunks."""
    try:
        async for chunk in agent.call(str, prompt, stream=True):
            if chunk:
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    except BaseException as exc:
        error_msg = _format_agent_error(phase, exc)
        yield f"data: {json.dumps({'error': error_msg})}\n\n"
    finally:
        close = getattr(agent, "close", None)
        if close is not None:
            try:
                await asyncio.wait_for(asyncio.shield(close()), timeout=5.0)
            except Exception:
                pass


async def gather_agent_calls(calls: dict[str, asyncio.coroutine]) -> dict[str, str]:
    """Run multiple agent calls in parallel and collect results."""
    names = list(calls)
    results = await asyncio.gather(*(calls[name] for name in names), return_exceptions=True)

    failures: list[str] = []
    outputs: dict[str, str] = {}
    for name, result in zip(names, results):
        if isinstance(result, BaseException):
            failures.append(_format_agent_error(name, result))
            continue
        outputs[name] = result

    if failures:
        raise AgentExecutionError(" | ".join(failures))

    return outputs
