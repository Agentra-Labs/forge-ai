"""OpenAlex API tools for paper discovery and citation graph traversal."""

from __future__ import annotations

import httpx
from agno.tools import tool

from config import settings

OPENALEX_BASE = "https://api.openalex.org"


def _openalex_params(params: dict) -> dict:
    if settings.openalex_email:
        params["mailto"] = settings.openalex_email
    return params


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool()
def openalex_search_papers(query: str, limit: int = 20) -> str:
    """Search OpenAlex for papers matching a query string.

    Args:
        query: Natural language search query (e.g. 'reinforcement learning for math olympiad').
        limit: Maximum number of results to return (default 20, max 100).

    Returns:
        JSON string with a list of paper objects containing title, authors, abstract, year, citation count.
    """
    params = _openalex_params({
        "search": query,
        "per_page": min(limit, 100),
        "select": "id,title,authorships,abstract_inverted_index,doi,ids,publication_year,cited_by_count,primary_location"
    })
    
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{OPENALEX_BASE}/works", params=params)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        return _format_papers(results)


@tool()
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
        clean_id = paper_id.lower().replace("arxiv:", "").strip()
        params = _openalex_params({
            "filter": f"ids.arxiv:{clean_id}",
            "select": "id,title,authorships,abstract_inverted_index,doi,ids,publication_year,cited_by_count,primary_location"
        })
        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{OPENALEX_BASE}/works", params=params)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return f"No paper found with ArXiv ID: {clean_id}"
            return _format_paper(results[0])

    # Handle DOI or OpenAlex ID
    target = paper_id
    if not target.startswith("https://api.openalex.org/"):
        if target.startswith("W"):
            target = f"{OPENALEX_BASE}/works/{target}"
        elif "/" in target: # Assume DOI
            target = f"{OPENALEX_BASE}/works/https://doi.org/{target}"

    with httpx.Client(timeout=30) as client:
        resp = client.get(target, params=_openalex_params({}))
        resp.raise_for_status()
        paper = resp.json()
        return _format_paper(paper)


@tool()
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

    params = _openalex_params({
        "filter": f"related_to:{paper_id}",
        "per_page": limit,
        "select": "id,title,authorships,abstract_inverted_index,doi,ids,publication_year,cited_by_count,primary_location"
    })
    
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{OPENALEX_BASE}/works", params=params)
        resp.raise_for_status()
        data = resp.json()
        return _format_papers(data.get("results", []))


@tool()
def openalex_citations(paper_id: str, limit: int = 20) -> str:
    """Get papers that cite a given paper (forward citation walk).

    Args:
        paper_id: OpenAlex work ID (e.g. 'W2741809807').
        limit: Maximum number of citing papers (default 20).

    Returns:
        JSON string with papers that cite the given paper.
    """
    params = _openalex_params({
        "filter": f"cites:{paper_id}",
        "per_page": limit,
        "select": "id,title,authorships,abstract_inverted_index,doi,ids,publication_year,cited_by_count,primary_location"
    })
    
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{OPENALEX_BASE}/works", params=params)
        resp.raise_for_status()
        data = resp.json()
        return _format_papers(data.get("results", []))


@tool()
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
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{OPENALEX_BASE}/works/{paper_id}", params=_openalex_params({}))
        resp.raise_for_status()
        data = resp.json()
        refs = data.get("referenced_works", [])[:limit]
        if not refs:
            return "No references found."
        
        # OpenAlex filter for multiple IDs: id:W1|W2|...
        ref_ids = "|".join(r.split("/")[-1] for r in refs)
        params = _openalex_params({
            "filter": f"openalex:{ref_ids}",
            "per_page": limit,
            "select": "id,title,authorships,abstract_inverted_index,doi,ids,publication_year,cited_by_count,primary_location"
        })
        resp = client.get(f"{OPENALEX_BASE}/works", params=params)
        resp.raise_for_status()
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
