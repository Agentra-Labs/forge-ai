"""OpenAlex API tools for paper discovery and citation graph traversal."""

from __future__ import annotations

import httpx
from config import settings

OPENALEX_BASE = "https://api.openalex.org"

_WORK_SELECT = "id,title,authorships,abstract_inverted_index,doi,ids,publication_year,cited_by_count,primary_location"


def _normalize_arxiv_id(value: str) -> str:
    v = value.strip().lower()
    v = v.removeprefix("arxiv:").strip()
    # If OpenAlex returns an arXiv URL, strip it down to the canonical ID.
    if v.startswith("https://arxiv.org/abs/"):
        v = v.split("https://arxiv.org/abs/", 1)[1]
    return v


def _extract_arxiv_id_from_ids(ids: dict | None) -> str:
    if not ids:
        return ""
    arxiv = ids.get("arxiv")
    if not arxiv:
        return ""
    return _normalize_arxiv_id(str(arxiv))


def _openalex_params(params: dict) -> dict:
    """Add mailto (polite pool) and/or api_key when configured."""
    if settings.openalex_email:
        params["mailto"] = settings.openalex_email
    if settings.openalex_api_key:
        params["api_key"] = settings.openalex_api_key
    return params


def _get(url: str, params: dict) -> httpx.Response:
    """Perform GET with OpenAlex params and clear error messages on failure."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, params=_openalex_params(dict(params)))
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            body = ""
            try:
                body = resp.json()
            except Exception:
                body = resp.text or ""
            msg = body.get("message", body) if isinstance(body, dict) else body
            hint = ""
            if resp.status_code == 429:
                hint = " (rate limit; set OPENALEX_EMAIL and/or OPENALEX_API_KEY for higher limits)"
            raise RuntimeError(
                f"OpenAlex API error {resp.status_code}: {msg or e.response.status_phrase}{hint}"
            ) from e
        return resp


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

def openalex_search_papers(query: str, limit: int = 20) -> str:
    """Search OpenAlex for papers matching a query string.

    Args:
        query: Natural language search query (e.g. 'reinforcement learning for math olympiad').
        limit: Maximum number of results to return (default 20, max 100).

    Returns:
        JSON string with a list of paper objects containing title, authors, abstract, year, citation count.
    """
    params = {
        "search": query,
        "per_page": min(limit, 100),
        "select": _WORK_SELECT
    }
    resp = _get(f"{OPENALEX_BASE}/works", params)
    data = resp.json()
    results = data.get("results", [])
    return _format_papers(results)


def openalex_get_paper(paper_id: str) -> str:
    """Get detailed information about a specific paper from OpenAlex.

    Args:
        paper_id: OpenAlex work ID (e.g. 'W2741809807'), DOI, or ArXiv ID.
                  For ArXiv IDs, provide it directly (e.g. '2103.00020').

    Returns:
        JSON string with full paper details including title, authors, abstract, citations.
    """
    # Handle ArXiv IDs if passed directly
    if paper_id.replace(".", "").isdigit() or "arxiv" in paper_id.lower():
        # OpenAlex does NOT support filtering on ids.arxiv. We search and then
        # pick the exact match from returned `ids.arxiv` where possible.
        clean_id = _normalize_arxiv_id(paper_id)

        # Best-effort: arXiv papers usually have a canonical DOI mapping:
        # 10.48550/arXiv.<id>
        doi = f"10.48550/arXiv.{clean_id}"
        try:
            resp = _get(f"{OPENALEX_BASE}/works/https://doi.org/{doi}", {"select": _WORK_SELECT})
            return _format_paper(resp.json())
        except RuntimeError as e:
            # If the DOI mapping doesn't exist, fall back to OpenAlex search.
            if " 404:" not in str(e):
                raise

        params = {"search": clean_id, "per_page": 10, "select": _WORK_SELECT}
        resp = _get(f"{OPENALEX_BASE}/works", params)
        data = resp.json()
        results = data.get("results", [])
        # OpenAlex often does not include an arXiv id in `ids`, so we can't always do
        # an exact id match. If we got anything back, present the closest hit.
        if results:
            return (
                f"No direct OpenAlex DOI mapping for ArXiv ID: {clean_id}\n"
                f"Closest OpenAlex search result:\n{_format_paper(results[0])}"
            )
        return f"No paper found with ArXiv ID: {clean_id}"

    # Handle DOI or OpenAlex ID
    target = paper_id
    if not target.startswith("https://api.openalex.org/"):
        if target.startswith("W"):
            target = f"{OPENALEX_BASE}/works/{target}"
        elif "/" in target:  # Assume DOI
            target = f"{OPENALEX_BASE}/works/https://doi.org/{target}"

    try:
        resp = _get(target, {})
    except RuntimeError as e:
        # If the work/DOI truly does not exist in OpenAlex, return a clear
        # message instead of surfacing a low-level HTML 404 error.
        if " 404:" in str(e):
            return (
                "No paper found for the given identifier.\n"
                f"Original input: {paper_id}\n"
                "Make sure this is a valid OpenAlex work ID (e.g. 'W2741809807') "
                "or a resolvable DOI."
            )
        raise

    paper = resp.json()
    return _format_paper(paper)


def openalex_recommendations(paper_id: str, limit: int = 10) -> str:
    """Get recommended papers similar to a given paper using OpenAlex's related_to filter.

    Args:
        paper_id: OpenAlex work ID (e.g. 'W2741809807').
        limit: Maximum number of recommendations (default 10).

    Returns:
        JSON string with recommended papers ranked by similarity.
    """
    # If it's an ArXiv ID, we first need to get the OpenAlex ID
    if "." in paper_id and paper_id.replace(".", "").isdigit():
        paper_info = openalex_get_paper(paper_id)
        if "OpenAlex ID: " in paper_info:
            paper_id = paper_info.split("OpenAlex ID: ")[1].split("\n")[0].split("/")[-1]

    params = {
        "filter": f"related_to:{paper_id}",
        "per_page": limit,
        "select": _WORK_SELECT
    }
    resp = _get(f"{OPENALEX_BASE}/works", params)
    data = resp.json()
    return _format_papers(data.get("results", []))


def openalex_citations(paper_id: str, limit: int = 20) -> str:
    """Get papers that cite a given paper (forward citation walk).

    Args:
        paper_id: OpenAlex work ID (e.g. 'W2741809807').
        limit: Maximum number of citing papers (default 20).

    Returns:
        JSON string with papers that cite the given paper.
    """
    params = {
        "filter": f"cites:{paper_id}",
        "per_page": limit,
        "select": _WORK_SELECT
    }
    resp = _get(f"{OPENALEX_BASE}/works", params)
    data = resp.json()
    return _format_papers(data.get("results", []))


def openalex_references(paper_id: str, limit: int = 20) -> str:
    """Get papers referenced by a given paper (backward citation walk).

    Args:
        paper_id: OpenAlex work ID (e.g. 'W2741809807').
        limit: Maximum number of referenced papers (default 20).

    Returns:
        JSON string with papers referenced by the given paper.
    """
    # References in OpenAlex are available as a list of IDs on the work itself.
    # To get full metadata, we use a filter for those IDs.
    resp = _get(f"{OPENALEX_BASE}/works/{paper_id}", {})
    data = resp.json()
    refs = data.get("referenced_works", [])[:limit]
    if not refs:
        return "No references found."

    # OpenAlex filter for multiple IDs: openalex:W1|W2|...
    ref_ids = "|".join(r.split("/")[-1] for r in refs)
    params = {
        "filter": f"openalex:{ref_ids}",
        "per_page": limit,
        "select": _WORK_SELECT
    }
    resp = _get(f"{OPENALEX_BASE}/works", params)
    data = resp.json()
    return _format_papers(data.get("results", []))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reconstruct_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return "N/A"
    
    # Inverted index is { word: [positions] }
    # We want to reconstruct the string at those positions.
    word_map = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            word_map[pos] = word
            
    if not word_map:
        return "N/A"
        
    max_pos = max(word_map.keys())
    parts = []
    for i in range(max_pos + 1):
        parts.append(word_map.get(i, ""))
    
    return " ".join(parts)


def _format_paper(p: dict) -> str:
    arxiv_id = p.get("ids", {}).get("arxiv", "N/A")
    authors = ", ".join(a.get("author", {}).get("display_name", "") for a in p.get("authorships", [])[:5])
    if len(p.get("authorships", [])) > 5:
        authors += f" (+{len(p['authorships']) - 5} more)"
    
    venue = "N/A"
    if p.get("primary_location") and p["primary_location"].get("source"):
        venue = p["primary_location"]["source"].get("display_name", "N/A")

    abstract = _reconstruct_abstract(p.get("abstract_inverted_index"))
    
    return (
        f"Title: {p.get('title', 'N/A')}\n"
        f"ArXiv ID: {arxiv_id}\n"
        f"OpenAlex ID: {p.get('id', 'N/A')}\n"
        f"Authors: {authors}\n"
        f"Year: {p.get('publication_year', 'N/A')}\n"
        f"Venue: {venue}\n"
        f"Citations: {p.get('cited_by_count', 0)}\n"
        f"URL: {p.get('doi') or p.get('id', 'N/A')}\n"
        f"Abstract: {abstract[:500]}\n"
    )


def _format_papers(papers: list[dict]) -> str:
    if not papers:
        return "No papers found."
    parts = []
    for i, p in enumerate(papers, 1):
        parts.append(f"--- Paper {i} ---\n{_format_paper(p)}")
    return "\n".join(parts)
