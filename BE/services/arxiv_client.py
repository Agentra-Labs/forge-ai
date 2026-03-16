from datetime import datetime

import arxiv
from pydantic import BaseModel


class ArxivPaper(BaseModel):
    """Represents an arXiv paper with key metadata."""

    id: str
    title: str
    authors: list[str]
    abstract: str
    published: datetime
    categories: list[str]
    pdf_url: str


class ArxivClient:
    def __init__(self, search_limit: int = 100) -> None:
        """
        Initialize the arXiv client.

        Args:
            search_limit: Maximum number of papers to retrieve per search
        """
        self.search_limit: int = search_limit
        self.client: arxiv.Client = arxiv.Client()

    def search(self, query: str, max_results: int = 10) -> list[ArxivPaper]:
        """
        Search for papers on arXiv.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of ArxivPaper objects
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []
        for paper in self.client.results(search):
            # Convert authors list to strings
            authors = [str(author) for author in paper.authors]

            # Get categories
            categories = paper.categories

            # Create paper object
            paper_obj = ArxivPaper(
                id=paper.get_short_id(),
                title=paper.title,
                authors=authors,
                abstract=paper.summary,
                published=paper.published,
                categories=categories,
                pdf_url=paper.pdf_url
                or "https://arxiv.org/pdf/" + paper.get_short_id() + ".pdf",
            )
            results.append(paper_obj)

            # Limit results
            if len(results) >= max_results:
                break

        return results
