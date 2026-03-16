"""Literature Review Workflow — comprehensive academic literature review.

Composes Wide Researcher, Paper Reader, and Deep Researcher into a full
literature review: wide scan → batch reading → thematic synthesis.
"""

from __future__ import annotations

from agents.deep_researcher import run_deep_researcher
from agents.paper_reader import run_paper_reader
from agents.wide_researcher import run_wide_researcher


async def run_literature_review(topic: str) -> str:
    """Run a comprehensive literature review on the given topic.

    Args:
        topic: Research topic for the full review.

    Returns:
        Structured literature review with clusters, gaps, contradictions,
        and trend analysis.
    """
    # Phase 1: Wide field survey
    wide_results = await run_wide_researcher(topic)

    # Phase 2: Batch paper reading
    reading_prompt = (
        f"LITERATURE REVIEW — PAPER READING PHASE\n\n"
        f"Research topic: {topic}\n\n"
        f"Papers discovered in the wide scan:\n{wide_results[:10000]}\n\n"
        "Review ALL papers mentioned above using the 3-pass methodology.\n\n"
        "IMPORTANT GROUNDER:\n"
        "- Only review papers explicitly mentioned in the scan text "
        "(with a clear title and preferably an ID).\n"
        "- Do NOT invent papers, titles, authors, venues, or results.\n"
        "- When a detail is missing, say 'Unknown from provided content'."
    )
    reading_results = await run_paper_reader(reading_prompt)

    # Phase 3: Synthesis and gap analysis
    synthesis_prompt = (
        f"LITERATURE REVIEW — SYNTHESIS PHASE\n\n"
        f"Research topic: {topic}\n\n"
        f"Paper review cards from the reading phase:\n{reading_results[:12000]}\n\n"
        "Synthesize these reviews into a comprehensive literature review:\n\n"
        "1. **Thematic Clusters**: Group papers by technique family or approach. "
        "Name each cluster and list the papers.\n"
        "2. **Timeline**: When did key advances happen? Show the evolution.\n"
        "3. **Contradiction Map**: Where do papers disagree with each other?\n"
        "4. **Gap Analysis**: What questions remain unanswered? "
        "What approaches haven't been tried?\n"
        "5. **Trend Analysis**: Where is the field heading?\n"
        "6. **Recommendations**: Most promising directions for new research."
    )
    synthesis_results = await run_deep_researcher(synthesis_prompt)

    return (
        "## Field Survey\n\n"
        f"{wide_results}\n\n"
        "---\n\n## Paper Reviews\n\n"
        f"{reading_results}\n\n"
        "---\n\n## Synthesis & Gap Analysis\n\n"
        f"{synthesis_results}"
    )
