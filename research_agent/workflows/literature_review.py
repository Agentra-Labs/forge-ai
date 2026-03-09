"""Literature Review Workflow — comprehensive academic literature review.

Composes all 3 agents: Wide scan for field survey, Paper Reader for
structured critique, and a synthesis step that clusters papers by theme,
identifies gaps, contradictions, and trends.
"""

from __future__ import annotations

from typing import AsyncIterator, Union

from agno.workflow.step import Step, StepInput, StepOutput, WorkflowRunOutputEvent
from agno.workflow.workflow import Workflow
from agno.db.sqlite import SqliteDb

from agents.wide_researcher import wide_researcher
from agents.paper_reader import paper_reader
from agents.deep_researcher import deep_researcher


# ---------------------------------------------------------------------------
# Custom Step: Batch Paper Reading
# ---------------------------------------------------------------------------

async def batch_reading_step(
    step_input: StepInput,
) -> AsyncIterator[Union[WorkflowRunOutputEvent, StepOutput]]:
    """Read and review all discovered papers using the 3-pass model."""
    message = step_input.input
    wide_results = step_input.previous_step_content or ""

    reading_prompt = f"""
    LITERATURE REVIEW — PAPER READING PHASE

    Research topic: {message}

    Papers discovered in the wide scan:
    {wide_results[:10000]}

    Review ALL papers mentioned above using the 3-pass methodology.
    For each paper, produce a review card with:
    - Relevance score to the research topic
    - Category (empirical/theoretical/systems/survey)
    - Key techniques and methods
    - Main results
    - Limitations

    IMPORTANT GROUNDER:
    - Only review papers that are explicitly and unambiguously mentioned in the wide-scan text
      (with a clear title and preferably an ID like arXiv, DOI, or URL).
    - Do NOT invent additional papers, titles, authors, venues, or results that are not present
      in the scan.
    - When a detail is missing (e.g. year, exact numbers), say "Unknown from provided content"
      instead of guessing.

    Be thorough — this is a literature review, so every paper matters.
    """

    response_iter = paper_reader.arun(reading_prompt, stream=True, stream_events=True)
    async for event in response_iter:
        yield event

    response = paper_reader.get_last_run_output()
    yield StepOutput(content=response.content if response else "No reviews generated.")


# ---------------------------------------------------------------------------
# Custom Step: Synthesis & Gap Analysis
# ---------------------------------------------------------------------------

async def synthesis_step(
    step_input: StepInput,
) -> AsyncIterator[Union[WorkflowRunOutputEvent, StepOutput]]:
    """Synthesize all reviews into a structured literature review.

    Clusters papers by theme, identifies gaps, contradictions, and trends.
    """
    message = step_input.input
    reading_results = step_input.previous_step_content or ""

    synthesis_prompt = f"""
    LITERATURE REVIEW — SYNTHESIS PHASE

    Research topic: {message}

    Paper review cards from the reading phase:
    {reading_results[:12000]}

    Now synthesize these reviews into a comprehensive literature review:

    1. **Thematic Clusters**: Group papers by technique family or approach type.
       Name each cluster and list the papers in it.

    2. **Timeline**: When did key advances happen? Show the evolution.

    3. **Contradiction Map**: Where do papers disagree with each other?
       Which experimental results contradict?

    4. **Gap Analysis**: What questions remain unanswered?
       What approaches haven't been tried? What combinations could be powerful?

    5. **Trend Analysis**: Where is the field heading?
       Which approaches are gaining momentum?

    6. **Recommendations**: Based on the gaps and trends, what are the
       most promising directions for new research on this topic?

    Output a well-structured literature review that a PhD student could
    use as the related work section of their thesis.
    """

    response_iter = deep_researcher.arun(synthesis_prompt, stream=True, stream_events=True)
    async for event in response_iter:
        yield event

    response = deep_researcher.get_last_run_output()
    yield StepOutput(content=response.content if response else "No synthesis generated.")


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

literature_review_workflow = Workflow(
    id="literature-review",
    name="Literature Review",
    description=(
        "Comprehensive academic literature review: Wide scan of the field → "
        "3-pass reading of all papers → thematic clustering, gap analysis, "
        "contradiction detection, and trend identification."
    ),
    db=SqliteDb(
        session_table="literature_review_sessions",
        db_file="tmp/forge_research.db",
    ),
    steps=[
        Step(
            name="Field Survey",
            agent=wide_researcher,
        ),
        Step(
            name="Paper Review",
            executor=batch_reading_step,
        ),
        Step(
            name="Synthesis & Gap Analysis",
            executor=synthesis_step,
        ),
    ],
)
