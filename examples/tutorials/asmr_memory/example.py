#!/usr/bin/env python3
"""
ASMR Memory System - Example Usage

Demonstrates the full ASMR (Agentic Structured Memory and Recall) pipeline
running on top of HoneyHive APIs with complete tracing and observability.

This example:
1. Creates sample conversation sessions (simulating multi-session histories)
2. Ingests them through 3 parallel observer agents
3. Queries the memory with user questions
4. Runs 12-way parallel inference + consensus aggregation
5. All operations are fully traced in HoneyHive

Requirements:
    pip install honeyhive openai

Environment variables:
    OPENAI_API_KEY: Your OpenAI API key
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    HH_API_URL: (Optional) HoneyHive API URL

Usage:
    python -m examples.tutorials.asmr_memory.example
"""

from __future__ import annotations

import os
import sys

# Sample conversation sessions demonstrating various memory challenges:
# personal info, preferences, temporal reasoning, knowledge updates
SAMPLE_SESSIONS = [
    {
        "session_id": "session_001",
        "timestamp": "2024-01-15T10:00:00Z",
        "messages": [
            {
                "role": "user",
                "content": "Hi! I'm Alex Chen, I work as a software engineer at TechCorp in San Francisco.",
            },
            {
                "role": "assistant",
                "content": "Nice to meet you, Alex! How can I help you today?",
            },
            {
                "role": "user",
                "content": "I'm looking for restaurant recommendations. I love Italian food, especially pasta dishes.",
            },
            {
                "role": "assistant",
                "content": "Great taste! San Francisco has some amazing Italian restaurants. I'd recommend Flour + Water in the Mission District.",
            },
            {
                "role": "user",
                "content": "That sounds perfect. I'm also vegetarian, so I prefer places with good veggie options.",
            },
            {
                "role": "assistant",
                "content": "Flour + Water has excellent vegetarian pasta options. You might also enjoy Greens Restaurant at Fort Mason.",
            },
        ],
    },
    {
        "session_id": "session_002",
        "timestamp": "2024-02-20T14:30:00Z",
        "messages": [
            {
                "role": "user",
                "content": "I just got promoted to Senior Engineer at TechCorp! Starting next month.",
            },
            {
                "role": "assistant",
                "content": "Congratulations on the promotion, Alex! That's a great achievement.",
            },
            {
                "role": "user",
                "content": "Thanks! Also, I've been thinking about learning Rust for our new systems project.",
            },
            {
                "role": "assistant",
                "content": "Rust is excellent for systems programming. Would you like some learning resources?",
            },
            {
                "role": "user",
                "content": "Yes please. Also, I've switched from being vegetarian to vegan since January.",
            },
            {
                "role": "assistant",
                "content": "Noted! I'll keep that in mind for future food recommendations. For Rust, I'd suggest 'The Rust Programming Language' book.",
            },
        ],
    },
    {
        "session_id": "session_003",
        "timestamp": "2024-03-10T09:15:00Z",
        "messages": [
            {
                "role": "user",
                "content": "I'm planning a trip to Japan in April. It'll be my first time there.",
            },
            {
                "role": "assistant",
                "content": "How exciting! April is cherry blossom season in Japan. How long will you be staying?",
            },
            {
                "role": "user",
                "content": "Two weeks. I want to visit Tokyo, Kyoto, and Osaka. My budget is around $5000.",
            },
            {
                "role": "assistant",
                "content": "That's a great itinerary! With $5000 for two weeks, you'll want to mix hotels and traditional ryokans.",
            },
            {
                "role": "user",
                "content": "I should mention I'm allergic to shellfish, so I'll need to be careful with food there.",
            },
            {
                "role": "assistant",
                "content": "Good to know. In Japan, you'll want to learn the phrase 'ebi arerugi' for shrimp allergy. Many dishes use dashi which can contain shellfish.",
            },
        ],
    },
    {
        "session_id": "session_004",
        "timestamp": "2024-04-05T16:00:00Z",
        "messages": [
            {
                "role": "user",
                "content": "Just got back from Japan! It was amazing. I especially loved Kyoto.",
            },
            {
                "role": "assistant",
                "content": "Welcome back! Kyoto is beautiful, especially during cherry blossom season. What were your highlights?",
            },
            {
                "role": "user",
                "content": "The temples were incredible. Also, I've decided to move to the Portland office of TechCorp next month.",
            },
            {
                "role": "assistant",
                "content": "That's a big change! Portland is a wonderful city. Will you still be in the Senior Engineer role?",
            },
            {
                "role": "user",
                "content": "Yes, same role but I'll be leading the Rust migration project there. Also, I adopted a cat named Mochi!",
            },
            {
                "role": "assistant",
                "content": "Congratulations on the new project lead role and on Mochi! Portland is very pet-friendly.",
            },
        ],
    },
    {
        "session_id": "session_005",
        "timestamp": "2024-05-20T11:00:00Z",
        "messages": [
            {
                "role": "user",
                "content": "I'm settled in Portland now. Can you recommend some good vegan restaurants here?",
            },
            {
                "role": "assistant",
                "content": "Portland is a vegan paradise! Some top picks: Farm Spirit, Bye and Bye, and Homegrown Smoker.",
            },
            {
                "role": "user",
                "content": "Those sound great. Oh, and I've been getting into rock climbing lately. Any good spots nearby?",
            },
            {
                "role": "assistant",
                "content": "Portland has amazing climbing! Smith Rock State Park is about 2.5 hours away and is world-class.",
            },
            {
                "role": "user",
                "content": "Perfect. My partner Jamie and I want to try it this weekend.",
            },
            {
                "role": "assistant",
                "content": "Smith Rock is great for couples! The Misery Ridge trail has stunning views even if you're not climbing.",
            },
        ],
    },
    {
        "session_id": "session_006",
        "timestamp": "2024-06-15T08:30:00Z",
        "messages": [
            {
                "role": "user",
                "content": "The Rust migration is going well. We've moved 3 of 8 services so far.",
            },
            {
                "role": "assistant",
                "content": "That's great progress! How's the team adapting to Rust?",
            },
            {
                "role": "user",
                "content": "Most are enjoying it. Oh, I should mention - Mochi has been sick and we found out she's allergic to chicken.",
            },
            {
                "role": "assistant",
                "content": "Sorry to hear about Mochi! Cat allergies can be tricky. There are good chicken-free cat food brands available.",
            },
            {
                "role": "user",
                "content": "Thanks. Also, Jamie and I got engaged last weekend!",
            },
            {
                "role": "assistant",
                "content": "Congratulations to you and Jamie! What wonderful news. Have you started thinking about wedding plans?",
            },
        ],
    },
]


def main() -> None:
    """Run the full ASMR pipeline example."""

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    hh_api_key = os.environ.get("HH_API_KEY")
    hh_project = os.environ.get("HH_PROJECT")
    hh_api_url = os.environ.get("HH_API_URL")

    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    if not hh_api_key:
        print("Error: HH_API_KEY environment variable is required")
        sys.exit(1)
    if not hh_project:
        print("Error: HH_PROJECT environment variable is required")
        sys.exit(1)

    from .asmr import ASMRMemory

    print("=" * 70)
    print("ASMR (Agentic Structured Memory and Recall) - HoneyHive Demo")
    print("=" * 70)
    print()

    # Initialize the ASMR memory system
    print("Initializing ASMR Memory System...")
    memory = ASMRMemory(
        api_key=hh_api_key,
        project=hh_project,
        openai_api_key=openai_api_key,
        api_url=hh_api_url,
    )
    print()

    # Stage 1: Ingest conversation sessions
    print("-" * 70)
    print("STAGE 1: Data Ingestion (3 Parallel Observer Agents)")
    print("-" * 70)
    print(f"  Ingesting {len(SAMPLE_SESSIONS)} conversation sessions...")
    print("  - Fact Hunter: sessions 1, 4 (NER, explicit facts, relationships)")
    print("  - Context Weaver: sessions 2, 5 (patterns, implications, clustering)")
    print("  - Timeline Tracker: sessions 3, 6 (temporal, chronology, updates)")
    print()

    ingestion_result = memory.ingest(SAMPLE_SESSIONS)

    print("  Ingestion Results:")
    print(f"    Fact Hunter findings: {ingestion_result['fact_hunter_findings']}")
    print(f"    Context Weaver findings: {ingestion_result['context_weaver_findings']}")
    print(
        f"    Timeline Tracker findings: {ingestion_result['timeline_tracker_findings']}"
    )
    print(f"    Total findings stored: {ingestion_result['total_findings']}")
    print()

    # Display store stats
    stats = memory.get_store_stats()
    print("  Knowledge Store Stats:")
    print(f"    Total findings: {stats['total_findings']}")
    print(f"    Total sessions indexed: {stats['total_sessions']}")
    print(f"    Total entities tracked: {stats['total_entities']}")
    if stats.get("categories"):
        print("    Categories:")
        for cat, count in stats["categories"].items():
            print(f"      {cat}: {count}")
    print()

    # Stage 2-4: Query the memory
    test_queries = [
        "Where does Alex currently live and work?",
        "What are Alex's dietary restrictions?",
        "What happened during Alex's Japan trip?",
        "Who is Jamie and what is their relationship to Alex?",
        "What programming language is Alex currently focused on?",
    ]

    print("-" * 70)
    print("STAGE 2-4: Search + Decision Forest + Consensus")
    print("-" * 70)

    for i, query in enumerate(test_queries):
        print(f"\n  Query {i + 1}: {query}")
        print("  " + "-" * 50)

        result = memory.query(query)

        print(f"  Answer: {result.get('final_answer', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        print(f"  Agreement: {result.get('agreement_level', 'N/A')}")
        if result.get("key_facts"):
            print(f"  Key facts: {result['key_facts']}")
        print()

    # Summary
    print("=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    final_stats = memory.get_store_stats()
    print(f"  Knowledge store: {final_stats['total_findings']} findings")
    print(f"  Sessions indexed: {final_stats['total_sessions']}")
    print(f"  Entities tracked: {final_stats['total_entities']}")
    print(f"  Queries answered: {len(test_queries)}")
    print()
    print("  All operations traced in HoneyHive!")
    print("  View traces at: https://app.honeyhive.ai")
    print("=" * 70)


if __name__ == "__main__":
    main()
