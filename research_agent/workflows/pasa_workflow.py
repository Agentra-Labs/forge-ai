import asyncio
from typing import List, Optional

from pydantic import BaseModel
from research_agent.services.arxiv_client import ArxivClient, ArxivPaper
from research_agent.services.nova_bedrock import NovaLiteClient
from research_agent.services.supermemory import SupermemoryService


class IngestRequest(BaseModel):
    """Request payload for ingesting papers."""

    query: str
    container_tag: str
    max_candidates: int = 10
    citation_expansion: bool = True


class IngestResult(BaseModel):
    """Result of ingestion process."""

    processed_count: int
    stored_papers: List[str]
    expansion_queries: List[str]
    synthesis: str


class PaSaWorkflow:
    def __init__(
        self,
        nova_client: NovaLiteClient,
        arxiv_client: ArxivClient,
        supermemory_service: SupermemoryService,
    ):
        """
        Initialize the PaSa workflow.

        Args:
            nova_client: Nova Lite client for AI processing
            arxiv_client: arXiv client for paper search
            supermemory_service: Supermemory service for storage
        """
        self.nova_client = nova_client
        self.arxiv_client = arxiv_client
        self.supermemory_service = supermemory_service

    def run(self, request: IngestRequest) -> IngestResult:
        """Run the PaSa workflow synchronously."""
        return asyncio.run(self._run_async(request))

    async def _run_async(self, request: IngestRequest) -> IngestResult:
        """
        Run the PaSa workflow asynchronously.

        Args:
            request: Ingest request parameters

        Returns:
            IngestResult with processing results
        """
        # Step 1: Search for papers
        print(f"Searching for papers with query: {request.query}")
        papers = self.arxiv_client.search(
            query=request.query, max_results=request.max_candidates
        )

        # Step 2: Process and store papers
        stored_papers = []
        paper_contents = []

        for paper in papers:
            # Store paper in Supermemory
            doc = self.supermemory_service.add_paper(
                paper_id=paper.id,
                title=paper.title,
                content=paper.abstract,  # Using abstract as content for now
                abstract=paper.abstract,
                authors=paper.authors,
                categories=paper.categories,
            )
            stored_papers.append(doc.id)
            paper_contents.append(f"Title: {paper.title}\nAbstract: {paper.abstract}")

        # Step 3: Build expansion queries if enabled
        expansion_queries = []
        if request.citation_expansion and paper_contents:
            expansion_queries = self._build_expansion_queries(
                request.query,
                paper_contents[:3],  # Use top 3 papers for expansion
            )

        # Step 4: Synthesize summary
        synthesis = ""
        if paper_contents:
            synthesis = self._synthesize_summary(request.query, paper_contents)

        return IngestResult(
            processed_count=len(stored_papers),
            stored_papers=stored_papers,
            expansion_queries=expansion_queries,
            synthesis=synthesis,
        )

    def _build_expansion_queries(
        self, original_query: str, paper_contents: List[str]
    ) -> List[str]:
        """
        Build expansion queries based on retrieved papers.

        Args:
            original_query: Original search query
            paper_contents: List of paper contents

        Returns:
            List of expansion queries
        """
        # Combine papers for context
        papers_context = "\n\n".join(paper_contents)

        prompt = f"""
        Original query: {original_query}

        Retrieved papers:
        {papers_context}

        Based on these papers, generate 3 additional search queries that would
        expand the literature search to related topics. Each query should be
        on a separate line and focus on different aspects or related concepts.
        """

        try:
            response = self.nova_client.complete(prompt, max_tokens=200)
            # Split response into lines and filter out empty ones
            queries = [line.strip() for line in response.split("\n") if line.strip()]
            return queries[:3]  # Return up to 3 queries
        except Exception as e:
            print(f"Error building expansion queries: {e}")
            return []

    def _synthesize_summary(self, query: str, paper_contents: List[str]) -> str:
        """
        Synthesize a summary from multiple papers.

        Args:
            query: Original search query
            paper_contents: List of paper contents

        Returns:
            Synthesized summary
        """
        # Combine papers for summarization
        papers_context = "\n\n---\n\n".join(paper_contents[:5])  # Use top 5 papers

        prompt = f"""
        Query: {query}

        Papers:
        {papers_context}

        Please provide a concise synthesis of the key findings across these papers
        that are relevant to the query. Focus on common themes, disagreements, and
        significant insights. Keep it under 300 words.
        """

        try:
            return self.nova_client.complete(prompt, max_tokens=400)
        except Exception as e:
            print(f"Error synthesizing summary: {e}")
            return "Unable to generate summary due to processing error."
