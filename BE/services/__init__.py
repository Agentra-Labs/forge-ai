"""
Nova Forge Research Agent Services

This package contains core services for the research agent:
- nova_bedrock: Amazon Bedrock integration for Nova Lite model
- arxiv_client: arXiv paper search and retrieval
- supermemory: Document storage and management
"""

from .arxiv_client import ArxivClient, ArxivPaper
from .nova_bedrock import NovaLiteClient
from .supermemory import Document, SupermemoryService

__all__ = [
    "NovaLiteClient",
    "ArxivClient",
    "ArxivPaper",
    "SupermemoryService",
    "Document",
]
