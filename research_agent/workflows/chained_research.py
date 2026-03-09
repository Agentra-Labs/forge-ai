"""Chained Research Workflow — Wide → Paper Reader → Deep pipeline.

The core research pipeline: broad scan, filter through 3-pass reading,
then deep-dive on the most promising candidates.
"""

from __future__ import annotations

from typing import AsyncIterator, Union

from agno.workflow.step import Step, StepInput, StepOutput, WorkflowRunOutputEvent
from agno.workflow.workflow import Workflow
from agno.db.sqlite import SqliteDb

from agents.wide_researcher import wide_researcher
from agents.deep_researcher import deep_researcher
from agents.paper_reader import paper_reader


# ---------------------------------------------------------------------------
# Custom Step: Paper Reading Pass
# ---------------------------------------------------------------------------

async def paper_reading_step(
    step_input: StepInput,
) -> AsyncIterator[Union[WorkflowRunOutputEvent, StepOutput]]:
    """Run Paper Reader on the Wide Researcher's top candidates.

    Takes the wide scan results, extracts the top papers mentioned,
    and runs them through the 3-pass reading methodology.
    """
    message = step_input.input
    wide_results = step_input.previous_step_content or ""

    reading_prompt = f"""
    The user's research goal: {message}

    The Wide Researcher produced the following scan of the landscape:
    {wide_results[:8000]}

    Please read through the papers mentioned above and produce review cards
    for the top 5-8 most relevant papers. Apply the 3-pass reading methodology.
    Focus on papers most likely to contribute to the user's goal.

    IMPORTANT GROUNDER:
    - Only create review cards for papers that are explicitly and unambiguously mentioned
      in the Wide Researcher scan (with a clear title and preferably an ID like arXiv, DOI, or URL).
    - Do NOT invent new papers, titles, authors, venues, or results that are not present
      in the scan text.
    - When a detail is missing (e.g. year, exact numbers), say "Unknown from provided content"
      instead of guessing.
    """

    response_iter = paper_reader.arun(reading_prompt, stream=True, stream_events=True)
    async for event in response_iter:
        yield event

    response = paper_reader.get_last_run_output()
    yield StepOutput(content=response.content if response else "No review cards generated.")


# ---------------------------------------------------------------------------
# Custom Step: Deep Analysis
# ---------------------------------------------------------------------------

async def deep_analysis_step(
    step_input: StepInput,
) -> AsyncIterator[Union[WorkflowRunOutputEvent, StepOutput]]:
    """Run Deep Researcher on papers that scored ≥ 0.6 in Paper Reader pass.

    Takes the reading results and does full extraction on the highest-scored papers.
    """
    message = step_input.input
    reading_results = step_input.previous_step_content or ""

    deep_prompt = f"""
    The user's research goal: {message}

    The Paper Reader reviewed papers and produced these review cards:
    {reading_results[:8000]}

    Now deeply analyze the papers that scored relevance ≥ 0.6.
    For each, extract full methods, results, ablation studies, and code links.
    Then synthesize: how could these papers' techniques be combined into a
    unified approach for the user's goal?
    """

    response_iter = deep_researcher.arun(deep_prompt, stream=True, stream_events=True)
    async for event in response_iter:
        yield event

    response = deep_researcher.get_last_run_output()
    yield StepOutput(content=response.content if response else "No deep analysis generated.")


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

chained_research_workflow = Workflow(
    id="chained-research",
    name="Chained Research",
    description=(
        "Full research pipeline: Wide scan → Paper Reader 3-pass filter → "
        "Deep extraction on top candidates. Produces a comprehensive research "
        "synthesis with ranked papers and integration blueprint."
    ),
    db=SqliteDb(
        session_table="chained_research_sessions",
        db_file="tmp/forge_research.db",
    ),
    steps=[
        Step(
            name="Wide Scan",
            agent=wide_researcher,
        ),
        Step(
            name="Paper Reading",
            executor=paper_reading_step,
        ),
        Step(
            name="Deep Analysis",
            executor=deep_analysis_step,
        ),
    ],
)
