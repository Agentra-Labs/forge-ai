"""RLM (Recursive Language Model) synthesis engine.

Stores extracted papers as named variables in a REPL-like environment.
The root agent never sees the full context — it uses peek/grep/subquery tools
to build synthesis incrementally, avoiding context rot.

Pattern based on: https://alexzhang13.github.io/blog/2025/rlm/
"""

from __future__ import annotations

import json
from typing import Optional

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools import tool


class PaperREPL:
    """In-memory REPL storing paper content as named variables.

    Papers are stored as `paper_000`, `paper_001`, etc.
    The root agent queries this store through tool calls instead of
    reading all papers at once (which would cause context degradation).
    """

    def __init__(self):
        self._store: dict[str, dict] = {}
        self._counter = 0

    def add_paper(self, title: str, content: str, metadata: Optional[dict] = None) -> str:
        """Add a paper to the REPL store and return its variable name."""
        var_name = f"paper_{self._counter:03d}"
        self._store[var_name] = {
            "title": title,
            "content": content,
            "metadata": metadata or {},
        }
        self._counter += 1
        return var_name

    def list_vars(self) -> list[dict]:
        """List all variables with titles (no full content)."""
        return [
            {"var": k, "title": v["title"], "content_length": len(v["content"])}
            for k, v in self._store.items()
        ]

    def peek(self, var_name: str, start: int = 0, length: int = 1000) -> str:
        """Peek at a slice of a paper's content."""
        if var_name not in self._store:
            return f"Variable {var_name} not found."
        content = self._store[var_name]["content"]
        return content[start:start + length]

    def grep(self, pattern: str) -> list[dict]:
        """Search all papers for a pattern (case-insensitive)."""
        results = []
        pattern_lower = pattern.lower()
        for var_name, data in self._store.items():
            content_lower = data["content"].lower()
            if pattern_lower in content_lower:
                # Find the position and return context around it
                idx = content_lower.index(pattern_lower)
                start = max(0, idx - 100)
                end = min(len(data["content"]), idx + len(pattern) + 100)
                results.append({
                    "var": var_name,
                    "title": data["title"],
                    "match_context": data["content"][start:end],
                })
        return results

    @property
    def size(self) -> int:
        return len(self._store)


def create_rlm_tools(repl: PaperREPL):
    """Create agno tools bound to a specific PaperREPL instance."""

    @tool()
    def repl_list_papers() -> str:
        """List all papers stored in the REPL with their variable names and titles.

        Returns:
            A formatted list of all stored papers with variable names, titles, and content lengths.
        """
        papers = repl.list_vars()
        if not papers:
            return "No papers in store."
        lines = [f"  {p['var']}: {p['title']} ({p['content_length']} chars)" for p in papers]
        return f"Papers in REPL ({len(papers)} total):\n" + "\n".join(lines)

    @tool()
    def repl_peek_paper(var_name: str, start: int = 0, length: int = 1000) -> str:
        """Read a specific section of a paper's content from the REPL store.

        Args:
            var_name: Variable name (e.g. 'paper_000').
            start: Character position to start reading from (default 0).
            length: Number of characters to read (default 1000).

        Returns:
            The requested section of the paper content.
        """
        return repl.peek(var_name, start, length)

    @tool()
    def repl_grep_papers(pattern: str) -> str:
        """Search all stored papers for a text pattern (case-insensitive).

        Args:
            pattern: Text pattern to search for across all papers.

        Returns:
            Matching excerpts from papers containing the pattern, with surrounding context.
        """
        results = repl.grep(pattern)
        if not results:
            return f"No matches for '{pattern}'."
        lines = [
            f"  {r['var']} ({r['title']}): ...{r['match_context']}..."
            for r in results
        ]
        return f"Matches for '{pattern}' ({len(results)} papers):\n" + "\n".join(lines)

    @tool()
    def repl_all_summaries() -> str:
        """Get the first 300 characters of every paper in the store.

        Returns:
            Brief summaries (first 300 chars) of all stored papers for quick orientation.
        """
        papers = repl.list_vars()
        if not papers:
            return "No papers in store."
        summaries = []
        for p in papers:
            preview = repl.peek(p["var"], 0, 300)
            summaries.append(f"  {p['var']}: {p['title']}\n    {preview}...")
        return "\n\n".join(summaries)

    return [repl_list_papers, repl_peek_paper, repl_grep_papers, repl_all_summaries]


def create_rlm_synthesizer(repl: PaperREPL) -> Agent:
    """Create an RLM synthesis agent bound to a PaperREPL instance.

    The agent can peek at individual papers, grep across all papers,
    and build up synthesis incrementally without full context exposure.
    """
    return Agent(
        id="rlm-synthesizer",
        name="RLM Synthesizer",
        model=AwsBedrock(id="amazon.nova-lite-v1:0"),
        tools=create_rlm_tools(repl),
        instructions="""You are the RLM Synthesizer — you build comprehensive research syntheses
by querying a store of extracted papers incrementally.

**IMPORTANT:** You NEVER see all papers at once. Use your tools:
- repl_list_papers: See what papers are available
- repl_peek_paper: Read sections of specific papers
- repl_grep_papers: Search across all papers for specific topics or techniques
- repl_all_summaries: Get brief overviews of all papers

**YOUR PROCESS:**
1. First, list all papers to orient yourself
2. Get brief summaries of all papers
3. Identify common themes by grepping for key terms
4. Deep-read the most relevant sections of the most important papers
5. Build your synthesis incrementally — compare, contrast, find gaps

**OUTPUT:** A comprehensive synthesis covering:
- Key technique clusters
- How papers relate to each other
- What gaps remain
- Recommended integration strategy for the user's goal
""",
        markdown=True,
    )
