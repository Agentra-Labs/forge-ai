"""Semantic Scholar API tools for paper discovery and citation graph traversal."""

from __future__ import annotations

import httpx
from agno.tools import tool

from config import settings

SS_BASE = "https://api.semanticscholar.org/graph/v1"
SS_FIELDS = "paperId,title,authors,abstract,url,year,citationCount,venue,externalIds"


def _ss_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key
    return headers


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool()
def ss_search_papers(query: str, limit: int = 20) -> str:
    """Search Semantic Scholar for papers matching a query string.

    Args:
        query: Natural language search query (e.g. 'reinforcement learning for math olympiad').
        limit: Maximum number of results to return (default 20, max 100).

    Returns:
        JSON string with a list of paper objects containing title, authors, abstract, year, citation count.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{SS_BASE}/paper/search",
            params={"query": query, "limit": min(limit, 100), "fields": SS_FIELDS},
            headers=_ss_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        papers = data.get("data", [])
        return _format_papers(papers)


@tool()
def ss_get_paper(paper_id: str) -> str:
    """Get detailed information about a specific paper from Semantic Scholar.

    Args:
        paper_id: Semantic Scholar paper ID, DOI, ArXiv ID (prefixed with 'ARXIV:'), or ACL ID.

    Returns:
        JSON string with full paper details including title, authors, abstract, citations.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{SS_BASE}/paper/{paper_id}",
            params={"fields": SS_FIELDS},
            headers=_ss_headers(),
        )
        resp.raise_for_status()
        paper = resp.json()
        return _format_paper(paper)


@tool()
def ss_recommendations(paper_id: str, limit: int = 10) -> str:
    """Get recommended papers similar to a given paper using Semantic Scholar's embedding-based recommendations.

    Args:
        paper_id: Semantic Scholar paper ID or ArXiv ID (prefixed with 'ARXIV:').
        limit: Maximum number of recommendations (default 10).

    Returns:
        JSON string with recommended papers ranked by similarity.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{SS_BASE}/paper/{paper_id}/recommendations",
            params={"limit": limit, "fields": SS_FIELDS},
            headers=_ss_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        return _format_papers(data.get("recommendedPapers", []))


@tool()
def ss_citations(paper_id: str, limit: int = 20) -> str:
    """Get papers that cite a given paper (forward citation walk).

    Args:
        paper_id: Semantic Scholar paper ID or ArXiv ID (prefixed with 'ARXIV:').
        limit: Maximum number of citing papers (default 20).

    Returns:
        JSON string with papers that cite the given paper.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{SS_BASE}/paper/{paper_id}/citations",
            params={"limit": limit, "fields": SS_FIELDS},
            headers=_ss_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        papers = [c.get("citingPaper", {}) for c in data.get("data", []) if c.get("citingPaper")]
        return _format_papers(papers)


@tool()
def ss_references(paper_id: str, limit: int = 20) -> str:
    """Get papers referenced by a given paper (backward citation walk).

    Args:
        paper_id: Semantic Scholar paper ID or ArXiv ID (prefixed with 'ARXIV:').
        limit: Maximum number of referenced papers (default 20).

    Returns:
        JSON string with papers referenced by the given paper.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{SS_BASE}/paper/{paper_id}/references",
            params={"limit": limit, "fields": SS_FIELDS},
            headers=_ss_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        papers = [r.get("citedPaper", {}) for r in data.get("data", []) if r.get("citedPaper")]
        return _format_papers(papers)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_paper(p: dict) -> str:
    arxiv_id = ""
    if p.get("externalIds"):
        arxiv_id = p["externalIds"].get("ArXiv", "")
    authors = ", ".join(a.get("name", "") for a in p.get("authors", [])[:5])
    if len(p.get("authors", [])) > 5:
        authors += f" (+{len(p['authors']) - 5} more)"
    return (
        f"Title: {p.get('title', 'N/A')}\n"
        f"ArXiv ID: {arxiv_id}\n"
        f"SS ID: {p.get('paperId', 'N/A')}\n"
        f"Authors: {authors}\n"
        f"Year: {p.get('year', 'N/A')}\n"
        f"Venue: {p.get('venue', 'N/A')}\n"
        f"Citations: {p.get('citationCount', 0)}\n"
        f"URL: {p.get('url', 'N/A')}\n"
        f"Abstract: {(p.get('abstract') or 'N/A')[:500]}\n"
    )


def _format_papers(papers: list[dict]) -> str:
    if not papers:
        return "No papers found."
    parts = []
    for i, p in enumerate(papers, 1):
        parts.append(f"--- Paper {i} ---\n{_format_paper(p)}")
    return "\n".join(parts)
