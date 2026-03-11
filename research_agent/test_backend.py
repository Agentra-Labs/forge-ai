#!/usr/bin/env python3
"""
Test script to verify backend components are working correctly.
"""

import os
import sys

# Add the research_agent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")

    try:
        from services.nova_bedrock import NovaLiteClient

        print("✓ NovaLiteClient imported successfully")
    except Exception as e:
        print(f"✗ Failed to import NovaLiteClient: {e}")

    try:
        from services.arxiv_client import ArxivClient, ArxivPaper

        print("✓ ArxivClient imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ArxivClient: {e}")

    try:
        from services.supermemory import Document, SupermemoryService

        print("✓ SupermemoryService imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SupermemoryService: {e}")

    try:
        from workflows.pasa_workflow import IngestRequest, IngestResult, PaSaWorkflow

        print("✓ PaSaWorkflow imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PaSaWorkflow: {e}")

    try:
        from main import app

        print("✓ FastAPI app imported successfully")
    except Exception as e:
        print(f"✗ Failed to import FastAPI app: {e}")


def test_arxiv_client():
    """Test arXiv client functionality."""
    print("\nTesting arXiv client...")

    try:
        from services.arxiv_client import ArxivClient

        client = ArxivClient()
        print("✓ ArxivClient instantiated successfully")

        # Test a simple search
        papers = client.search("machine learning", max_results=2)
        print(f"✓ Found {len(papers)} papers")
        if papers:
            print(f"  First paper: {papers[0].title}")

    except Exception as e:
        print(f"✗ Failed to test ArxivClient: {e}")


def test_supermemory_service():
    """Test Supermemory service functionality."""
    print("\nTesting Supermemory service...")

    try:
        from services.supermemory import SupermemoryService

        service = SupermemoryService()
        print("✓ SupermemoryService instantiated successfully")

        # Test adding a paper
        doc = service.add_paper(
            paper_id="test-123",
            title="Test Paper",
            content="This is a test paper content.",
            abstract="This is a test abstract.",
            authors=["Author One", "Author Two"],
            categories=["cs.AI", "cs.LG"],
        )
        print("✓ Added test paper to Supermemory")
        print(f"  Document ID: {doc.id}")

    except Exception as e:
        print(f"✗ Failed to test SupermemoryService: {e}")


if __name__ == "__main__":
    print("Running backend tests...\n")

    test_imports()
    test_arxiv_client()
    test_supermemory_service()

    print("\nTests completed!")
