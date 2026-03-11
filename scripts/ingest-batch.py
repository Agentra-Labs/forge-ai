#!/usr/bin/env python3
"""
Batch ingestion script for Nova Forge academic papers.

This script allows ingesting multiple research topics in sequence,
making it easy to populate the knowledge base with various domains.
"""

import argparse
import asyncio
import json
import os
import sys
from typing import List

# Add research_agent to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "research_agent"))

from research_agent.services.arxiv_client import ArxivClient
from research_agent.services.nova_bedrock import NovaLiteClient
from research_agent.services.supermemory import SupermemoryService
from research_agent.workflows.pasa_workflow import IngestRequest, PaSaWorkflow


async def ingest_topic(
    workflow: PaSaWorkflow,
    topic: str,
    container_tag: str,
    max_candidates: int = 10,
    citation_expansion: bool = True,
):
    """Ingest a single topic using the PaSa workflow."""
    print(f"🔍 Ingesting topic: {topic}")

    request = IngestRequest(
        query=topic,
        container_tag=container_tag,
        max_candidates=max_candidates,
        citation_expansion=citation_expansion,
    )

    try:
        result = workflow.run(request)
        print(f"✅ Successfully ingested {result.processed_count} papers for '{topic}'")
        print(f"📝 Synthesis: {result.synthesis[:100]}...")
        return result
    except Exception as e:
        print(f"❌ Error ingesting '{topic}': {str(e)}")
        return None


async def main(topics: List[str], max_candidates: int = 10):
    """Main function to ingest multiple topics."""
    print("🚀 Starting batch ingestion...")

    # Initialize services
    nova_client = NovaLiteClient()
    arxiv_client = ArxivClient()
    supermemory_service = SupermemoryService()
    workflow = PaSaWorkflow(nova_client, arxiv_client, supermemory_service)

    results = []

    # Process each topic
    for i, topic in enumerate(topics):
        print(f"\n[{i + 1}/{len(topics)}]")
        result = await ingest_topic(
            workflow,
            topic,
            container_tag=f"batch-{i + 1}",
            max_candidates=max_candidates,
        )
        if result:
            results.append(
                {
                    "topic": topic,
                    "processed_count": result.processed_count,
                    "synthesis": result.synthesis,
                }
            )

    # Print summary
    print("\n📊 Ingestion Summary:")
    total_papers = sum(r["processed_count"] for r in results if r)
    print(f"Total topics processed: {len([r for r in results if r])}")
    print(f"Total papers ingested: {total_papers}")

    # Save results to file
    with open("ingestion-results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("💾 Results saved to ingestion-results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch ingest academic papers")
    parser.add_argument(
        "--topics",
        nargs="+",
        help="Topics to ingest (e.g., 'machine learning' 'quantum computing')",
    )
    parser.add_argument("--file", help="JSON file containing topics to ingest")
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=10,
        help="Maximum number of papers to retrieve per topic",
    )

    args = parser.parse_args()

    # Get topics from command line or file
    topics = []
    if args.topics:
        topics = args.topics
    elif args.file:
        with open(args.file, "r") as f:
            topics = json.load(f)
    else:
        # Default topics if none provided
        topics = [
            "artificial intelligence",
            "machine learning",
            "climate change",
            "gene therapy",
        ]

    # Run the ingestion
    asyncio.run(main(topics, args.max_candidates))
