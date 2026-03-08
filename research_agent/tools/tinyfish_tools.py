"""TinyFish API tools for deep research extraction.

TinyFish treats any website as a programmable surface:
send {url, goal} → get clean structured JSON back.

Falls back to basic httpx extraction if TINYFISH_API_KEY is not set.
"""

from __future__ import annotations

import json

import httpx
from agno.tools import tool

from config import settings

TINYFISH_BASE = "https://api.tinyfish.ai/v1"


@tool()
def tinyfish_extract(url: str, goal: str) -> str:
    """Extract structured information from any URL using TinyFish AI web agent.

    TinyFish renders the page, understands it semantically, and extracts
    exactly what you ask for as clean JSON. Handles JS-heavy pages and auth walls.

    Args:
        url: The URL to extract from.
        goal: What to extract (e.g. 'Extract paper methods, results, ablation studies, and benchmark numbers').

    Returns:
        Structured extraction results as formatted text.
    """
    if not settings.tinyfish_api_key:
        return _fallback_extract(url, goal)

    try:
        with httpx.Client(timeout=90) as client:
            resp = client.post(
                f"{TINYFISH_BASE}/extract",
                json={"url": url, "goal": goal},
                headers={
                    "Authorization": f"Bearer {settings.tinyfish_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
    except Exception as e:
        return f"TinyFish extraction failed ({e}), using fallback.\n{_fallback_extract(url, goal)}"


@tool()
def tinyfish_deep_paper(arxiv_url: str) -> str:
    """Deeply extract full paper content from an arXiv paper URL using TinyFish.

    Extracts: title, authors, abstract, methods, experimental setup,
    results, ablation studies, limitations, code links, and figures.

    Args:
        arxiv_url: ArXiv paper URL (e.g. 'https://arxiv.org/abs/2603.03202').

    Returns:
        Comprehensive structured extraction of the paper content.
    """
    goal = (
        "Extract comprehensive paper information: "
        "1) Title and authors, "
        "2) Full abstract, "
        "3) Key methods and techniques used, "
        "4) Experimental setup (datasets, metrics, baselines), "
        "5) Main results and benchmark numbers, "
        "6) Ablation studies if any, "
        "7) Limitations acknowledged by authors, "
        "8) Code repository URL if mentioned, "
        "9) Key figures and their descriptions"
    )
    return tinyfish_extract.entrypoint(url=arxiv_url, goal=goal)


@tool()
def tinyfish_extract_competition(url: str) -> str:
    """Extract competition/challenge details from a competition page using TinyFish.

    Extracts rules, constraints, evaluation criteria, compute limits,
    scoring rubric, and allowed approaches.

    Args:
        url: Competition or challenge page URL (e.g. Kaggle competition URL).

    Returns:
        Structured competition details as formatted text.
    """
    goal = (
        "Extract all competition information: "
        "1) Competition name and description, "
        "2) Evaluation criteria and scoring rubric, "
        "3) Compute constraints (GPU type, time limits), "
        "4) Input/output format requirements, "
        "5) Allowed approaches and restrictions, "
        "6) Timeline and deadlines, "
        "7) Prize information"
    )
    return tinyfish_extract.entrypoint(url=url, goal=goal)


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _fallback_extract(url: str, goal: str) -> str:
    """Basic HTTP extraction fallback when TinyFish is unavailable."""
    try:
        import re
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "ForgeResearchAgent/1.0"})
            resp.raise_for_status()
            text = resp.text

            # Strip HTML
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

            return f"[Fallback extraction — TinyFish API key not configured]\nGoal: {goal}\nURL: {url}\nContent (first 5000 chars):\n{text[:5000]}"
    except Exception as e:
        return f"Failed to extract from {url}: {e}"
