import os
from typing import List, Optional

import requests
from pydantic import BaseModel


class Document(BaseModel):
    """Represents a document stored in Supermemory."""

    id: str
    content: str
    title: str
    url: Optional[str] = None
    tags: List[str] = []
    metadata: dict = {}


class SupermemoryService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.supermemory.ai",
    ):
        """
        Initialize the Supermemory service client.

        Args:
            api_key: Supermemory API key (defaults to SUPERMEMORY_API_KEY env var)
            base_url: Base URL for the Supermemory API
        """
        self.api_key = api_key or os.getenv("SUPERMEMORY_API_KEY")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def add_paper(
        self,
        paper_id: str,
        title: str,
        content: str,
        abstract: str = "",
        authors: List[str] = None,
        categories: List[str] = None,
    ) -> Document:
        """
        Add a paper to Supermemory.

        Args:
            paper_id: Unique identifier for the paper
            title: Paper title
            content: Full content/text of the paper
            abstract: Paper abstract
            authors: List of authors
            categories: List of categories/tags

        Returns:
            Document object representing the stored paper
        """
        # Combine abstract with content for storage
        full_content = f"Abstract: {abstract}\n\n{content}"

        # Prepare tags from authors and categories
        tags = []
        if authors:
            tags.extend([f"author:{author}" for author in authors])
        if categories:
            tags.extend(categories)

        document_data = {
            "id": paper_id,
            "content": full_content,
            "title": title,
            "url": f"https://arxiv.org/abs/{paper_id}",
            "tags": tags,
            "metadata": {
                "source": "arxiv",
                "authors": authors or [],
                "categories": categories or [],
            },
        }

        # In a real implementation, this would make an API call to Supermemory
        # For now, we'll simulate the storage and return a Document object
        return Document(**document_data)

    def get_documents(
        self, tags: Optional[List[str]] = None, limit: int = 10
    ) -> List[Document]:
        """
        Retrieve documents from Supermemory.

        Args:
            tags: Optional list of tags to filter by
            limit: Maximum number of documents to retrieve

        Returns:
            List of Document objects
        """
        # In a real implementation, this would query the Supermemory API
        # For now, returning an empty list as placeholder
        return []
