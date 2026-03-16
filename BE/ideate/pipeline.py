"""Ideate pipeline — transforms arXiv papers into product opportunity reports.

5-phase adversarial multi-agent pipeline:
  Phase 1 — Decomposer: extract technical primitives
  Phase 2 — Parallel: pain scanner + infra inversion + temporal arbitrage
  Phase 3 — Cross-pollinator: non-obvious cross-domain ideas
  Phase 4 — Destroyer (red team): brutal critique of all ideas
  Phase 5 — Synthesizer: final ranked report
"""

from __future__ import annotations

import asyncio
import os
from time import perf_counter

from backend import call_agent_text, gather_agent_calls, spawn_agent
from prompts import DEFAULT_MODEL

from .ingestion import fetch_paper
from .models import PaperContent
from .prompts import (
    CROSSPOLLINATOR_PREMISE,
    DECOMPOSER_PREMISE,
    DESTROYER_PREMISE,
    INFRA_INVERSION_PREMISE,
    PAIN_SCANNER_PREMISE,
    SYNTHESIZER_PREMISE,
    TEMPORAL_PREMISE,
)
from .reporting import build_report
from .search import SearchTrace, make_disabled_web_search_tool, make_web_search_tool

# ---------------------------------------------------------------------------
# Context limits
# ---------------------------------------------------------------------------

PRIORITY_SECTION_KEYS = [
    "abstract", "preamble", "introduction", "method", "approach",
    "experiments", "results", "conclusion", "discussion",
]
FULL_SECTION_CHARS = 5_000
FULL_CONTEXT_CHARS = 25_000
COMPACT_SECTION_CHARS = 2_500
COMPACT_CONTEXT_CHARS = 10_000
FULL_FIGURE_COUNT = 15
FULL_TABLE_COUNT = 6
FULL_REFERENCE_COUNT = 30
COMPACT_FIGURE_COUNT = 6
COMPACT_TABLE_COUNT = 4
COMPACT_REFERENCE_COUNT = 10
PRIMITIVE_SUMMARY_CHARS = 4_500
PAIN_SUMMARY_CHARS = 3_000
IDEA_SUMMARY_CHARS = 2_500

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


def _redteam_search_enabled() -> bool:
    return os.getenv("ENABLE_REDTEAM_SEARCH", "0").strip().lower() in {"1", "true", "yes"}


def _truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[...truncated...]"


def _phase_started(label: str) -> float:
    print(label)
    return perf_counter()


def _phase_finished(label: str, started_at: float, details: str = "") -> None:
    elapsed = perf_counter() - started_at
    suffix = f" {details}" if details else ""
    print(f"  done: {label} in {elapsed:.1f}s{suffix}")


# ---------------------------------------------------------------------------
# Paper context builders
# ---------------------------------------------------------------------------


def _collect_key_sections(
    paper: PaperContent,
    *,
    section_char_limit: int,
) -> dict[str, str]:
    key_sections: dict[str, str] = {}
    for key in PRIORITY_SECTION_KEYS:
        for section_name, content in paper.sections.items():
            if key in section_name.lower():
                key_sections[section_name] = content[:section_char_limit]
    return key_sections


def _build_paper_context(
    paper: PaperContent,
    *,
    section_char_limit: int,
    context_char_limit: int,
    figure_count: int,
    table_count: int,
    reference_count: int,
    primitives_summary: str = "",
) -> str:
    key_sections = _collect_key_sections(paper, section_char_limit=section_char_limit)
    context = (
        f"TITLE: {paper.title}\n"
        f"AUTHORS: {', '.join(paper.authors[:10])}\n"
        f"ABSTRACT: {paper.abstract}\n\n"
        f"KEY SECTIONS:\n"
        + "\n\n".join(f"=== {name} ===\n{content}" for name, content in key_sections.items())
        + "\n\nFIGURE CAPTIONS:\n"
        + "\n".join(paper.figures_captions[:figure_count])
        + "\n\nTABLE SUMMARIES:\n"
        + "\n".join(paper.tables_text[:table_count])
        + "\n\nREFERENCED WORKS:\n"
        + "\n".join(paper.references_titles[:reference_count])
    )
    if primitives_summary:
        context += "\n\nTECHNICAL PRIMITIVES SUMMARY:\n" + primitives_summary
    if len(context) > context_char_limit:
        return context[:context_char_limit] + "\n\n[...truncated...]"
    return context


def build_full_paper_context(paper: PaperContent) -> str:
    return _build_paper_context(
        paper,
        section_char_limit=FULL_SECTION_CHARS,
        context_char_limit=FULL_CONTEXT_CHARS,
        figure_count=FULL_FIGURE_COUNT,
        table_count=FULL_TABLE_COUNT,
        reference_count=FULL_REFERENCE_COUNT,
    )


def build_compact_paper_context(paper: PaperContent, *, primitives_summary: str) -> str:
    return _build_paper_context(
        paper,
        section_char_limit=COMPACT_SECTION_CHARS,
        context_char_limit=COMPACT_CONTEXT_CHARS,
        figure_count=COMPACT_FIGURE_COUNT,
        table_count=COMPACT_TABLE_COUNT,
        reference_count=COMPACT_REFERENCE_COUNT,
        primitives_summary=primitives_summary,
    )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


async def run_pipeline(arxiv_id_or_url: str, model: str = DEFAULT_MODEL) -> str:
    """Run the 5-phase paper-to-product ideation pipeline.

    Args:
        arxiv_id_or_url: ArXiv paper ID (e.g. "2312.00752") or URL.
        model: Model slug (OpenRouter/Agentica format).

    Returns:
        Full markdown report string.
    """
    print(f"Fetching paper: {arxiv_id_or_url}")
    paper = await fetch_paper(arxiv_id_or_url)
    print(f"Loaded: {paper.title} ({len(paper.full_text)} chars)")

    full_context = build_full_paper_context(paper)
    print(f"Phase 1 context: {len(full_context)} chars")

    # -------------------------------------------------------------------------
    # Phase 1: Extract technical primitives
    # -------------------------------------------------------------------------
    t = _phase_started("Phase 1: Extracting technical primitives...")
    decomposer = await spawn_agent(premise=DECOMPOSER_PREMISE, model=model)
    primitives_raw = await call_agent_text(
        decomposer,
        f"Analyze this paper and extract all atomic technical primitives:\n\n{full_context}",
        phase="technical primitive extraction",
    )
    _phase_finished("Phase 1", t)

    primitives_summary = _truncate_text(primitives_raw, PRIMITIVE_SUMMARY_CHARS)
    compact_context = build_compact_paper_context(paper, primitives_summary=primitives_summary)
    print(f"Downstream context: {len(compact_context)} chars")

    # -------------------------------------------------------------------------
    # Phase 2: Parallel analysis (pain + infra + temporal)
    # -------------------------------------------------------------------------
    t = _phase_started("Phase 2: Running parallel analysis agents...")
    pain_trace = SearchTrace(section_name="Market Pain Mapping")
    temporal_trace = SearchTrace(section_name="Temporal Arbitrage")

    pain_agent = await spawn_agent(
        premise=PAIN_SCANNER_PREMISE,
        model=model,
        scope={"web_search": make_web_search_tool(default_intent="fast", trace=pain_trace)},
    )
    infra_agent = await spawn_agent(premise=INFRA_INVERSION_PREMISE, model=model)
    temporal_agent = await spawn_agent(
        premise=TEMPORAL_PREMISE,
        model=model,
        scope={"web_search": make_web_search_tool(default_intent="fresh", trace=temporal_trace)},
    )

    phase_two_results = await gather_agent_calls({
        "pain scanner": call_agent_text(
            pain_agent,
            f"Technical primitives:\n\n{primitives_summary}\n\n"
            f"Paper context:\n{compact_context}\n\n"
            "Search the web to find real, current market pain mapping to these primitives. "
            "Go FAR beyond the paper's own domain.",
            phase="pain scanner",
        ),
        "infrastructure inversion": call_agent_text(
            infra_agent,
            f"Paper context:\n{compact_context}\n\n"
            f"Technical primitives:\n{primitives_summary}\n\n"
            "What NEW problems does widespread adoption of this technique CREATE? "
            "What products solve those second-order problems?",
            phase="infrastructure inversion",
        ),
        "temporal arbitrage": call_agent_text(
            temporal_agent,
            f"Paper context:\n{compact_context}\n\n"
            f"Technical primitives:\n{primitives_summary}\n\n"
            "Identify temporal arbitrage windows. What can be built RIGHT NOW that "
            "won't be obvious for 12-24 months? Search the web for recent related "
            "papers and industry trends.",
            phase="temporal arbitrage",
        ),
    })

    pain_raw = phase_two_results["pain scanner"]
    infra_raw = phase_two_results["infrastructure inversion"]
    temporal_raw = phase_two_results["temporal arbitrage"]
    _phase_finished(
        "Phase 2", t,
        details=f"(pain web={pain_trace.calls_used}, temporal web={temporal_trace.calls_used})",
    )

    # -------------------------------------------------------------------------
    # Phase 3: Cross-pollination
    # -------------------------------------------------------------------------
    t = _phase_started("Phase 3: Cross-pollination...")
    crosspoll_agent = await spawn_agent(premise=CROSSPOLLINATOR_PREMISE, model=model)
    crosspoll_raw = await call_agent_text(
        crosspoll_agent,
        f"Technical primitives:\n{primitives_summary}\n\n"
        f"Market pain points found:\n{_truncate_text(pain_raw, PAIN_SUMMARY_CHARS)}\n\n"
        "Force non-obvious cross-pollination. Skip direct/obvious matches.",
        phase="cross-pollination",
    )
    _phase_finished("Phase 3", t)

    # -------------------------------------------------------------------------
    # Phase 4: Red team destruction
    # -------------------------------------------------------------------------
    t = _phase_started("Phase 4: Red team destruction...")
    all_ideas = (
        f"=== IDEAS FROM PAIN MAPPING ===\n{_truncate_text(pain_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== IDEAS FROM CROSS-POLLINATION ===\n{_truncate_text(crosspoll_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== IDEAS FROM INFRASTRUCTURE INVERSION ===\n{_truncate_text(infra_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== IDEAS FROM TEMPORAL ARBITRAGE ===\n{_truncate_text(temporal_raw, IDEA_SUMMARY_CHARS)}\n\n"
    )
    destroyer_scope = (
        {"web_search": make_web_search_tool(default_intent="fast")}
        if _redteam_search_enabled()
        else {"web_search": make_disabled_web_search_tool()}
    )
    destroyer = await spawn_agent(
        premise=DESTROYER_PREMISE,
        model=model,
        scope=destroyer_scope,
    )
    redteam_raw = await call_agent_text(
        destroyer,
        f"Here are product ideas from a research paper. Destroy every one.\n\n"
        f"Paper: {paper.title}\n\n{all_ideas}",
        phase="red team destruction",
    )
    _phase_finished(
        "Phase 4", t,
        details="" if _redteam_search_enabled() else "(red-team search disabled)",
    )

    # -------------------------------------------------------------------------
    # Phase 5: Final synthesis
    # -------------------------------------------------------------------------
    t = _phase_started("Phase 5: Final synthesis...")
    synthesizer = await spawn_agent(premise=SYNTHESIZER_PREMISE, model=model)
    final_raw = await call_agent_text(
        synthesizer,
        f"PAPER: {paper.title}\nABSTRACT: {paper.abstract}\n\n"
        f"=== TECHNICAL PRIMITIVES ===\n{primitives_summary}\n\n"
        f"=== MARKET PAIN MAPPING ===\n{_truncate_text(pain_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== CROSS-POLLINATED IDEAS ===\n{_truncate_text(crosspoll_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== INFRASTRUCTURE INVERSION ===\n{_truncate_text(infra_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== TEMPORAL ARBITRAGE ===\n{_truncate_text(temporal_raw, IDEA_SUMMARY_CHARS)}\n\n"
        f"=== RED TEAM DESTRUCTION RESULTS ===\n{_truncate_text(redteam_raw, IDEA_SUMMARY_CHARS)}\n\n"
        "Synthesize all of the above into a final ranked list of the BEST ideas. "
        "Only include ideas that survived red-teaming or were strengthened by it.",
        phase="final synthesis",
    )
    _phase_finished("Phase 5", t)

    return build_report(
        paper=paper,
        primitives=primitives_raw,
        pain=pain_raw,
        pain_sources=pain_trace.render_markdown(),
        crosspoll=crosspoll_raw,
        infra=infra_raw,
        temporal=temporal_raw,
        temporal_sources=temporal_trace.render_markdown(),
        redteam=redteam_raw,
        redteam_sources="",
        final=final_raw,
    )
