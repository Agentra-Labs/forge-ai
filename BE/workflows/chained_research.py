"""Chained Research Workflow — Wide → Paper Reader → Deep pipeline.

The core research pipeline: broad scan, filter through 3-pass reading,
then deep-dive on the most promising candidates.
"""

from __future__ import annotations

from agents.deep_researcher import run_deep_researcher
from agents.paper_reader import run_paper_reader
from agents.wide_researcher import run_wide_researcher


async def run_chained_research(goal: str) -> str:
    """Run the full chained research pipeline: wide → read → deep.

    Args:
        goal: The research goal or question.

    Returns:
        Synthesized research output with ranked papers and integration blueprint.
    """
    # Phase 1: Wide landscape scan
    wide_results = await run_wide_researcher(goal)

    # Phase 2: 3-pass paper reading on top candidates from scan
    reading_prompt = (
        f"The user's research goal: {goal}\n\n"
        f"The Wide Researcher produced the following scan of the landscape:\n"
        f"{wide_results[:8000]}\n\n"
        "Please read through the papers mentioned above and produce review cards "
        "for the top 5-8 most relevant papers. Apply the 3-pass reading methodology.\n\n"
        "IMPORTANT GROUNDER:\n"
        "- Only create review cards for papers explicitly mentioned in the scan "
        "(with a clear title and preferably an ID like arXiv, DOI, or URL).\n"
        "- Do NOT invent papers, titles, authors, venues, or results not in the scan.\n"
        "- When a detail is missing, say 'Unknown from provided content'."
    )
    reading_results = await run_paper_reader(reading_prompt)

    # Phase 3: Deep analysis on papers scoring >= 0.6
    deep_prompt = (
        f"The user's research goal: {goal}\n\n"
        f"The Paper Reader reviewed papers and produced these review cards:\n"
        f"{reading_results[:8000]}\n\n"
        "Now deeply analyze the papers that scored relevance >= 0.6. "
        "For each, extract full methods, results, ablation studies, and code links. "
        "Then synthesize: how could these papers' techniques be combined into a "
        "unified approach for the user's goal?"
    )
    deep_results = await run_deep_researcher(deep_prompt)

    return (
        "## Wide Scan\n\n"
        f"{wide_results}\n\n"
        "---\n\n## Paper Reviews\n\n"
        f"{reading_results}\n\n"
        "---\n\n## Deep Analysis & Synthesis\n\n"
        f"{deep_results}"
    )
