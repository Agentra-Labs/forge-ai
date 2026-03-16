"""kernel.sh browser-as-a-service tools for wide research scraping.

Falls back to simple httpx scraping if KERNEL_API_KEY is not set.
"""

from __future__ import annotations

import json

import httpx

from config import settings

KERNEL_BASE = "https://api.kernel.sh/v1"


def kernel_scrape_url(url: str, goal: str = "Extract main text content") -> str:
    """Scrape a single URL using kernel.sh cloud browser infrastructure.

    Uses kernel.sh to render the page in a real browser (handles JS, auth walls)
    and extracts content based on the goal. Falls back to simple HTTP if no API key.

    Args:
        url: The URL to scrape.
        goal: What to extract from the page (e.g. 'Extract paper titles and abstracts').

    Returns:
        Extracted text content from the page.
    """
    if not settings.kernel_api_key:
        return _fallback_scrape(url)

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{KERNEL_BASE}/scrape",
                json={"url": url, "goal": goal},
                headers={
                    "Authorization": f"Bearer {settings.kernel_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("content", data.get("text", json.dumps(data)))
    except Exception as e:
        return f"kernel.sh scrape failed ({e}), falling back to basic HTTP.\n{_fallback_scrape(url)}"


def kernel_parallel_scrape(urls: list[str], goal: str = "Extract paper titles, abstracts, and metadata") -> str:
    """Scrape multiple URLs in parallel using kernel.sh browser sessions.

    Spawns simultaneous browser sessions for breadth-first crawling.
    Falls back to sequential httpx if no API key.

    Args:
        urls: List of URLs to scrape (max 10).
        goal: What to extract from each page.

    Returns:
        Combined extracted content from all pages, separated by URL markers.
    """
    urls = urls[:10]  # Cap at 10 to avoid abuse

    if not settings.kernel_api_key:
        results = []
        for url in urls:
            results.append(f"=== {url} ===\n{_fallback_scrape(url)}\n")
        return "\n".join(results)

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{KERNEL_BASE}/scrape/batch",
                json={"urls": urls, "goal": goal},
                headers={
                    "Authorization": f"Bearer {settings.kernel_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("results", []):
                url = item.get("url", "unknown")
                content = item.get("content", item.get("text", "No content extracted"))
                results.append(f"=== {url} ===\n{content}\n")
            return "\n".join(results) if results else "No results returned."
    except Exception as e:
        # Fallback to sequential
        results = []
        for url in urls:
            results.append(f"=== {url} ===\n{_fallback_scrape(url)}\n")
        return f"kernel.sh batch failed ({e}), used fallback:\n" + "\n".join(results)


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _fallback_scrape(url: str) -> str:
    """Simple HTTP GET fallback when kernel.sh is unavailable."""
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "ForgeResearchAgent/1.0"})
            resp.raise_for_status()
            text = resp.text

            # Basic HTML stripping for readability
            import re
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:5000]  # Cap at 5K chars
    except Exception as e:
        return f"Failed to scrape {url}: {e}"
