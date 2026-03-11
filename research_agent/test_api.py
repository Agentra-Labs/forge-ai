#!/usr/bin/env python3
"""
Comprehensive test script to validate the Nova Forge backend system.
Tests imports, component initialization, and API endpoints.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the research_agent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestRunner:
    """Runs comprehensive backend tests."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def log_pass(self, message: str):
        """Log a passing test."""
        self.passed += 1
        print(f"✓ {message}")

    def log_fail(self, message: str, error: str = ""):
        """Log a failing test."""
        self.failed += 1
        print(f"✗ {message}")
        if error:
            print(f"  Error: {error}")
            self.errors.append((message, error))

    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print("=" * 60)

        if self.errors:
            print("\nFailed Tests Details:")
            for message, error in self.errors:
                print(f"\n{message}")
                print(f"  {error}")


def test_imports(runner: TestRunner):
    """Test that all modules can be imported successfully."""
    print("\n" + "=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)

    # Test Nova Bedrock Client
    try:
        from services.nova_bedrock import NovaLiteClient

        runner.log_pass("NovaLiteClient imported successfully")
    except Exception as e:
        runner.log_fail("NovaLiteClient import", str(e))

    # Test arXiv Client
    try:
        from services.arxiv_client import ArxivClient, ArxivPaper

        runner.log_pass("ArxivClient imported successfully")
    except Exception as e:
        runner.log_fail("ArxivClient import", str(e))

    # Test Supermemory Service
    try:
        from services.supermemory import Document, SupermemoryService

        runner.log_pass("SupermemoryService imported successfully")
    except Exception as e:
        runner.log_fail("SupermemoryService import", str(e))

    # Test PaSa Workflow
    try:
        from workflows.pasa_workflow import IngestRequest, IngestResult, PaSaWorkflow

        runner.log_pass("PaSaWorkflow imported successfully")
    except Exception as e:
        runner.log_fail("PaSaWorkflow import", str(e))

    # Test FastAPI app
    try:
        from main import app, base_app

        runner.log_pass("FastAPI app imported successfully")
    except Exception as e:
        runner.log_fail("FastAPI app import", str(e))


def test_component_initialization(runner: TestRunner):
    """Test that components can be initialized."""
    print("\n" + "=" * 60)
    print("TESTING COMPONENT INITIALIZATION")
    print("=" * 60)

    # Test Supermemory Service initialization
    try:
        from services.supermemory import SupermemoryService

        service = SupermemoryService()
        runner.log_pass("SupermemoryService initialized without API key")
    except Exception as e:
        runner.log_fail("SupermemoryService initialization", str(e))

    # Test arXiv Client initialization
    try:
        from services.arxiv_client import ArxivClient

        client = ArxivClient()
        runner.log_pass("ArxivClient initialized successfully")
    except Exception as e:
        runner.log_fail("ArxivClient initialization", str(e))

    # Test IngestRequest model
    try:
        from workflows.pasa_workflow import IngestRequest

        request = IngestRequest(
            query="machine learning",
            container_tag="test-container",
            max_candidates=5,
            citation_expansion=True,
        )
        runner.log_pass("IngestRequest model created successfully")
    except Exception as e:
        runner.log_fail("IngestRequest model creation", str(e))


def test_arxiv_search(runner: TestRunner):
    """Test arXiv search functionality."""
    print("\n" + "=" * 60)
    print("TESTING ARXIV SEARCH")
    print("=" * 60)

    try:
        from services.arxiv_client import ArxivClient

        client = ArxivClient()
        papers = client.search("quantum computing", max_results=3)

        if len(papers) > 0:
            runner.log_pass(f"arXiv search returned {len(papers)} papers")

            # Check paper structure
            paper = papers[0]
            if (
                hasattr(paper, "title")
                and hasattr(paper, "authors")
                and hasattr(paper, "abstract")
            ):
                runner.log_pass(f"Paper structure valid: {paper.title[:50]}...")
            else:
                runner.log_fail("Paper structure validation", "Missing required fields")
        else:
            runner.log_fail("arXiv search", "No papers returned")

    except Exception as e:
        runner.log_fail("arXiv search execution", str(e))


def test_supermemory_operations(runner: TestRunner):
    """Test Supermemory service operations."""
    print("\n" + "=" * 60)
    print("TESTING SUPERMEMORY OPERATIONS")
    print("=" * 60)

    try:
        from services.supermemory import SupermemoryService

        service = SupermemoryService()

        # Test adding a paper
        doc = service.add_paper(
            paper_id="test-2401.12345",
            title="Test Research Paper on AI",
            content="This is a test paper about artificial intelligence and machine learning.",
            abstract="A comprehensive study of AI systems.",
            authors=["Dr. Smith", "Prof. Johnson"],
            categories=["cs.AI", "cs.LG"],
        )

        if doc.id == "test-2401.12345":
            runner.log_pass("Paper added to Supermemory successfully")
        else:
            runner.log_fail("Paper addition", "Document ID mismatch")

        # Test retrieving documents
        docs = service.get_documents(limit=5)
        runner.log_pass(f"Retrieved {len(docs)} documents from Supermemory")

    except Exception as e:
        runner.log_fail("Supermemory operations", str(e))


def test_api_endpoints(runner: TestRunner):
    """Test FastAPI endpoint definitions."""
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)

    try:
        from main import app

        # Check if routes are registered
        routes = [route.path for route in app.routes]

        required_endpoints = [
            "/",
            "/health",
            "/ingest",
        ]

        for endpoint in required_endpoints:
            if any(endpoint in route for route in routes):
                runner.log_pass(f"Endpoint '{endpoint}' is registered")
            else:
                runner.log_fail(f"Endpoint check", f"'{endpoint}' not found in routes")

    except Exception as e:
        runner.log_fail("API endpoint check", str(e))


def test_workflow_initialization(runner: TestRunner):
    """Test PaSa workflow initialization."""
    print("\n" + "=" * 60)
    print("TESTING WORKFLOW INITIALIZATION")
    print("=" * 60)

    try:
        from services.arxiv_client import ArxivClient
        from services.nova_bedrock import NovaLiteClient
        from services.supermemory import SupermemoryService
        from workflows.pasa_workflow import PaSaWorkflow

        nova_client = NovaLiteClient()
        arxiv_client = ArxivClient()
        supermemory_service = SupermemoryService()

        workflow = PaSaWorkflow(nova_client, arxiv_client, supermemory_service)
        runner.log_pass("PaSa workflow initialized successfully")

        # Check workflow methods
        if hasattr(workflow, "run") and hasattr(workflow, "_run_async"):
            runner.log_pass("Workflow has required methods (run, _run_async)")
        else:
            runner.log_fail("Workflow methods check", "Missing required methods")

    except Exception as e:
        runner.log_fail("Workflow initialization", str(e))


def test_environment_variables(runner: TestRunner):
    """Test that environment variables are properly set."""
    print("\n" + "=" * 60)
    print("TESTING ENVIRONMENT VARIABLES")
    print("=" * 60)

    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        runner.log_pass(".env file exists")
    else:
        runner.log_fail(".env file", "Not found (optional)")

    # Check key environment variables
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    if aws_key:
        runner.log_pass("AWS_ACCESS_KEY_ID is set")
    else:
        runner.log_fail("AWS_ACCESS_KEY_ID", "Not set (required for Bedrock)")

    supermemory_key = os.getenv("SUPERMEMORY_API_KEY")
    if supermemory_key:
        runner.log_pass("SUPERMEMORY_API_KEY is set")
    else:
        runner.log_fail("SUPERMEMORY_API_KEY", "Not set (optional for testing)")

    agent_url = os.getenv("AGENT_URL")
    if agent_url:
        runner.log_pass(f"AGENT_URL is set: {agent_url}")
    else:
        runner.log_fail("AGENT_URL", "Not set (defaults to localhost:7777)")


def test_error_handling(runner: TestRunner):
    """Test error handling in components."""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)

    try:
        from services.arxiv_client import ArxivClient

        client = ArxivClient()

        # Test with empty query
        try:
            papers = client.search("", max_results=1)
            runner.log_pass("arXiv client handles empty query gracefully")
        except Exception:
            runner.log_fail("Empty query handling", "Should handle gracefully")

    except Exception as e:
        runner.log_fail("Error handling test", str(e))


def test_model_validation(runner: TestRunner):
    """Test Pydantic model validation."""
    print("\n" + "=" * 60)
    print("TESTING MODEL VALIDATION")
    print("=" * 60)

    try:
        from workflows.pasa_workflow import IngestRequest

        # Test with valid data
        try:
            request = IngestRequest(
                query="test query",
                container_tag="test-tag",
                max_candidates=10,
                citation_expansion=True,
            )
            runner.log_pass("IngestRequest validation passed with valid data")
        except Exception as e:
            runner.log_fail("IngestRequest valid data validation", str(e))

        # Test with invalid data (missing required field)
        try:
            request = IngestRequest(
                container_tag="test-tag",
            )
            runner.log_fail(
                "IngestRequest invalid data validation",
                "Should have raised validation error",
            )
        except Exception:
            runner.log_pass("IngestRequest correctly rejects invalid data")

    except Exception as e:
        runner.log_fail("Model validation test", str(e))


def test_data_structures(runner: TestRunner):
    """Test data structure definitions."""
    print("\n" + "=" * 60)
    print("TESTING DATA STRUCTURES")
    print("=" * 60)

    try:
        from services.supermemory import Document
        from workflows.pasa_workflow import IngestResult

        # Test Document model
        try:
            doc = Document(
                id="test-123",
                content="Test content",
                title="Test Title",
                url="https://example.com",
                tags=["test", "ai"],
            )
            runner.log_pass("Document model instantiation successful")
        except Exception as e:
            runner.log_fail("Document model", str(e))

        # Test IngestResult model
        try:
            result = IngestResult(
                processed_count=5,
                stored_papers=["paper1", "paper2"],
                expansion_queries=["query1", "query2"],
                synthesis="Summary of papers",
            )
            runner.log_pass("IngestResult model instantiation successful")
        except Exception as e:
            runner.log_fail("IngestResult model", str(e))

    except Exception as e:
        runner.log_fail("Data structure test", str(e))


def main():
    """Run all tests."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   NOVA FORGE BACKEND TEST SUITE                           ║")
    print("║   Comprehensive validation of all components              ║")
    print("╚════════════════════════════════════════════════════════════╝")

    runner = TestRunner()

    # Run all tests
    test_imports(runner)
    test_component_initialization(runner)
    test_environment_variables(runner)
    test_api_endpoints(runner)
    test_model_validation(runner)
    test_data_structures(runner)
    test_supermemory_operations(runner)
    test_arxiv_search(runner)
    test_workflow_initialization(runner)
    test_error_handling(runner)

    # Print summary
    runner.print_summary()

    # Exit with appropriate code
    sys.exit(0 if runner.failed == 0 else 1)


if __name__ == "__main__":
    main()
