"""
ASMR Memory - Main Orchestrator

Agentic Structured Memory and Recall (ASMR) system built on HoneyHive.
Ties together all components:
1. Observer Agents (knowledge extraction)
2. Knowledge Store (structured storage)
3. Search Agents (agentic retrieval)
4. Decision Forest & Consensus (multi-variant reasoning)

All operations are fully traced through HoneyHive for observability.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from honeyhive import HoneyHiveTracer

from .consensus import DecisionForest
from .knowledge_store import KnowledgeStore
from .observer_agents import ObserverAgents
from .search_agents import SearchAgents


class ASMRMemory:
    """Full ASMR pipeline orchestrator.

    Usage:
        asmr = ASMRMemory(
            api_key="hh-api-key",
            project="my-project",
            openai_api_key="sk-...",
        )
        asmr.ingest(sessions)
        result = asmr.query("What is the user's name?")
        print(result["final_answer"])
    """

    def __init__(
        self,
        api_key: str,
        project: str,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        api_url: Optional[str] = None,
    ) -> None:
        # Initialize HoneyHive tracer
        tracer_kwargs: Dict[str, Any] = {
            "api_key": api_key,
            "project": project,
            "source": "asmr_memory_tutorial",
        }
        if api_url:
            tracer_kwargs["server_url"] = api_url

        self.tracer = HoneyHiveTracer.init(**tracer_kwargs)

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=openai_api_key)

        # Initialize components
        self.store = KnowledgeStore()
        self.observer_agents = ObserverAgents(
            openai_client=self.openai_client,
            knowledge_store=self.store,
            tracer=self.tracer,
            model=model,
        )
        self.search_agents = SearchAgents(
            openai_client=self.openai_client,
            knowledge_store=self.store,
            tracer=self.tracer,
            model=model,
        )
        self.decision_forest = DecisionForest(
            openai_client=self.openai_client,
            tracer=self.tracer,
            model=model,
        )

    def ingest(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run observer agents to extract knowledge from conversation sessions.

        Args:
            sessions: List of conversation session dicts, each with:
                - session_id: unique identifier
                - timestamp: when the conversation occurred
                - messages: list of {role, content} message dicts

        Returns:
            Summary dict with ingestion statistics.
        """
        with self.tracer.start_span("asmr_ingest") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")
                span.set_attribute("num_sessions", len(sessions))

            summary = self.observer_agents.ingest_sessions(sessions)

            self.tracer.enrich_span(
                metadata=summary,
                metrics={"total_findings": summary.get("total_findings", 0)},
            )
            return summary

    def query(self, question: str) -> Dict[str, Any]:
        """Run the full query pipeline: search + decision forest + consensus.

        Args:
            question: The user's question to answer from memory.

        Returns:
            Consensus result dict with:
                - final_answer: the consensus answer
                - confidence: 0.0-1.0 confidence score
                - agreement_level: how much the variants agreed
                - key_facts: supporting evidence
                - dissenting_views: notable disagreements
        """
        with self.tracer.start_span("asmr_query") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")
                span.set_attribute("question", question)

            # Stage 1: Search agents find relevant knowledge
            search_results = self.search_agents.search(question)

            # Stage 2: Decision forest reasons over search results
            consensus = self.decision_forest.decide(question, search_results)

            self.tracer.enrich_span(
                metadata={
                    "final_answer": consensus.get("final_answer", ""),
                    "confidence": consensus.get("confidence", 0),
                    "agreement_level": consensus.get("agreement_level", "unknown"),
                },
            )
            return consensus

    def ingest_and_query(
        self,
        sessions: List[Dict[str, Any]],
        question: str,
    ) -> Dict[str, Any]:
        """Convenience method: ingest sessions then answer a question.

        Returns the full pipeline result including ingestion stats and answer.
        """
        with self.tracer.start_span("asmr_full_pipeline") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")

            ingestion_summary = self.ingest(sessions)
            answer = self.query(question)

            return {
                "ingestion": ingestion_summary,
                "answer": answer,
            }

    def get_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge store."""
        return self.store.get_stats()

    def export_knowledge(self) -> str:
        """Export the entire knowledge store as JSON."""
        all_findings = self.store.get_all()
        return json.dumps(
            [
                {
                    "id": f.id,
                    "category": f.category.value,
                    "source_agent": f.source_agent.value,
                    "content": f.content,
                    "session_ids": f.session_ids,
                    "entities": f.entities,
                    "timestamp": f.timestamp,
                    "event_date": f.event_date,
                    "confidence": f.confidence,
                    "supersedes": f.supersedes,
                    "metadata": f.metadata,
                }
                for f in all_findings
            ],
            indent=2,
        )
