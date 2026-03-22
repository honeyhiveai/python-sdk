"""
Observer Agents - Parallel Knowledge Extraction Pipeline

Three parallel observer agents that process conversation histories
and extract structured knowledge across six vectors:
1. Personal Information
2. Preferences
3. Events
4. Temporal Data
5. Updates
6. Assistant Info

This maps to the "Data Ingestion" component in the ASMR architecture diagram.
Sessions are distributed round-robin across the 3 agents.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from openai import OpenAI

from honeyhive import HoneyHiveTracer

from .knowledge_store import Finding, FindingCategory, FindingSource, KnowledgeStore

# System prompts for each observer agent

FACT_HUNTER_SYSTEM_PROMPT = """You are the Fact Hunter agent. Your job is to extract concrete, factual information from conversation sessions.

Focus on:
- Named Entity Recognition (NER): Identify people, places, organizations, products, dates
- Explicit statement extraction: Direct facts stated by the user or assistant
- Relationship mapping: How entities relate to each other

For each finding, output a JSON array of objects with these fields:
- "category": one of "personal_info", "preferences", "events", "temporal_data", "updates", "assistant_info"
- "content": a clear, atomic statement of the fact
- "entities": list of named entities mentioned
- "timestamp": when this was mentioned (if available from context)
- "event_date": when the event described actually occurred (if different from timestamp)
- "confidence": 0.0-1.0 confidence score

Output ONLY valid JSON array. No explanation text."""

CONTEXT_WEAVER_SYSTEM_PROMPT = """You are the Context Weaver agent. Your job is to identify patterns, implications, and cross-session correlations from conversation sessions.

Focus on:
- Pattern recognition: Recurring themes, habits, or behaviors
- Implications: What can be inferred from statements (not just literal meaning)
- Semantic clustering: Group related concepts together
- Cross-reference: Note when information connects to or reinforces other facts

For each finding, output a JSON array of objects with these fields:
- "category": one of "personal_info", "preferences", "events", "temporal_data", "updates", "assistant_info"
- "content": a clear statement of the pattern or implication discovered
- "entities": list of named entities involved
- "timestamp": when this pattern was observed
- "confidence": 0.0-1.0 confidence score
- "metadata": object with "pattern_type" (one of "recurring", "implication", "correlation", "cluster")

Output ONLY valid JSON array. No explanation text."""

TIMELINE_TRACKER_SYSTEM_PROMPT = """You are the Timeline Tracker agent. Your job is to extract temporal information and track how knowledge evolves over time.

Focus on:
- Temporal sequence extraction: Order of events as described by the user
- Event chronology mapping: Build a timeline of key events
- Knowledge update detection: Identify when newer information supersedes older information
- Duration and frequency: How long things last, how often they occur

For each finding, output a JSON array of objects with these fields:
- "category": one of "personal_info", "preferences", "events", "temporal_data", "updates", "assistant_info"
- "content": a clear temporal statement
- "entities": list of named entities involved
- "timestamp": when this was recorded
- "event_date": the actual date/time of the event described
- "confidence": 0.0-1.0 confidence score
- "supersedes_content": if this updates previous knowledge, describe what it replaces (or null)
- "metadata": object with "temporal_type" (one of "sequence", "chronology", "update", "duration", "frequency")

Output ONLY valid JSON array. No explanation text."""


def _distribute_sessions_round_robin(
    sessions: List[Dict[str, Any]],
) -> Dict[int, List[Dict[str, Any]]]:
    """Distribute sessions across 3 agents using round-robin.

    Agent 0 gets sessions 0, 3, 6, ...
    Agent 1 gets sessions 1, 4, 7, ...
    Agent 2 gets sessions 2, 5, 8, ...
    """
    distribution: Dict[int, List[Dict[str, Any]]] = {0: [], 1: [], 2: []}
    for i, session in enumerate(sessions):
        agent_idx = i % 3
        distribution[agent_idx].append(session)
    return distribution


def _format_session_for_prompt(session: Dict[str, Any]) -> str:
    """Format a conversation session for inclusion in an LLM prompt."""
    session_id = session.get("session_id", "unknown")
    timestamp = session.get("timestamp", "unknown")
    messages = session.get("messages", [])

    lines = [f"=== Session {session_id} (timestamp: {timestamp}) ==="]
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        lines.append(f"[{role}]: {content}")
    lines.append("=== End Session ===\n")

    return "\n".join(lines)


def _parse_agent_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse the JSON response from an observer agent."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response_text[start:end])
            except json.JSONDecodeError:
                pass
    return []


def _build_findings(
    raw_findings: List[Dict[str, Any]],
    source_agent: FindingSource,
    default_category: FindingCategory,
    session_ids: List[str],
    default_confidence: float,
) -> List[Finding]:
    """Build Finding objects from raw LLM output."""
    findings = []
    for raw in raw_findings:
        category_str = raw.get("category", default_category.value)
        try:
            category = FindingCategory(category_str)
        except ValueError:
            category = default_category

        finding = Finding(
            id="",
            category=category,
            source_agent=source_agent,
            content=raw.get("content", ""),
            session_ids=session_ids,
            entities=raw.get("entities", []),
            timestamp=raw.get("timestamp"),
            event_date=raw.get("event_date"),
            confidence=raw.get("confidence", default_confidence),
            supersedes=raw.get("supersedes_content"),
            metadata=raw.get("metadata", {}),
        )
        findings.append(finding)
    return findings


class ObserverAgents:
    """Orchestrates the three parallel observer agents for knowledge extraction.

    All LLM calls are traced through HoneyHive using manual span management
    for full observability of each agent's processing.
    """

    def __init__(
        self,
        openai_client: OpenAI,
        knowledge_store: KnowledgeStore,
        tracer: HoneyHiveTracer,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.client = openai_client
        self.store = knowledge_store
        self.tracer = tracer
        self.model = model

    def _run_fact_hunter(self, sessions: List[Dict[str, Any]]) -> List[Finding]:
        """Observer Agent 1: Fact Hunter - NER, explicit statements, relationships."""
        if not sessions:
            return []

        with self.tracer.start_span("fact_hunter_agent") as span:
            session_text = "\n".join(_format_session_for_prompt(s) for s in sessions)
            session_ids = [s.get("session_id", "unknown") for s in sessions]

            if span:
                span.set_attribute("hh.event_type", "tool")
                span.set_attribute("agent.name", "fact_hunter")
                span.set_attribute("sessions.count", len(sessions))

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": FACT_HUNTER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Extract factual knowledge from these conversation sessions:\n\n{session_text}",
                    },
                ],
                temperature=0.1,
            )

            raw_findings = _parse_agent_response(
                response.choices[0].message.content or "[]"
            )

            findings = _build_findings(
                raw_findings,
                FindingSource.FACT_HUNTER,
                FindingCategory.PERSONAL_INFO,
                session_ids,
                0.8,
            )

            self.tracer.enrich_span(
                metadata={
                    "findings_count": len(findings),
                    "sessions_processed": len(sessions),
                },
                metrics={"extraction_count": len(findings)},
            )
            return findings

    def _run_context_weaver(self, sessions: List[Dict[str, Any]]) -> List[Finding]:
        """Observer Agent 2: Context Weaver - patterns, implications, correlations."""
        if not sessions:
            return []

        with self.tracer.start_span("context_weaver_agent") as span:
            session_text = "\n".join(_format_session_for_prompt(s) for s in sessions)
            session_ids = [s.get("session_id", "unknown") for s in sessions]

            if span:
                span.set_attribute("hh.event_type", "tool")
                span.set_attribute("agent.name", "context_weaver")
                span.set_attribute("sessions.count", len(sessions))

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CONTEXT_WEAVER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Identify patterns and implications from these conversation sessions:\n\n{session_text}",
                    },
                ],
                temperature=0.2,
            )

            raw_findings = _parse_agent_response(
                response.choices[0].message.content or "[]"
            )

            findings = _build_findings(
                raw_findings,
                FindingSource.CONTEXT_WEAVER,
                FindingCategory.PREFERENCES,
                session_ids,
                0.7,
            )

            self.tracer.enrich_span(
                metadata={
                    "findings_count": len(findings),
                    "sessions_processed": len(sessions),
                },
                metrics={"extraction_count": len(findings)},
            )
            return findings

    def _run_timeline_tracker(self, sessions: List[Dict[str, Any]]) -> List[Finding]:
        """Observer Agent 3: Timeline Tracker - temporal sequences, knowledge updates."""
        if not sessions:
            return []

        with self.tracer.start_span("timeline_tracker_agent") as span:
            session_text = "\n".join(_format_session_for_prompt(s) for s in sessions)
            session_ids = [s.get("session_id", "unknown") for s in sessions]

            if span:
                span.set_attribute("hh.event_type", "tool")
                span.set_attribute("agent.name", "timeline_tracker")
                span.set_attribute("sessions.count", len(sessions))

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": TIMELINE_TRACKER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Extract temporal information and track knowledge evolution from these sessions:\n\n{session_text}",
                    },
                ],
                temperature=0.1,
            )

            raw_findings = _parse_agent_response(
                response.choices[0].message.content or "[]"
            )

            findings = _build_findings(
                raw_findings,
                FindingSource.TIMELINE_TRACKER,
                FindingCategory.TEMPORAL_DATA,
                session_ids,
                0.75,
            )

            self.tracer.enrich_span(
                metadata={
                    "findings_count": len(findings),
                    "sessions_processed": len(sessions),
                },
                metrics={"extraction_count": len(findings)},
            )
            return findings

    def ingest_sessions(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run all 3 observer agents on the sessions and store findings.

        Sessions are distributed round-robin across the agents:
        - Fact Hunter gets sessions 0, 3, 6, ...
        - Context Weaver gets sessions 1, 4, 7, ...
        - Timeline Tracker gets sessions 2, 5, 8, ...

        Returns a summary of the ingestion results.
        """
        with self.tracer.start_span("parallel_knowledge_extraction") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")
                span.set_attribute("total_sessions", len(sessions))

            distribution = _distribute_sessions_round_robin(sessions)

            fact_findings = self._run_fact_hunter(distribution[0])
            context_findings = self._run_context_weaver(distribution[1])
            timeline_findings = self._run_timeline_tracker(distribution[2])

            all_findings = fact_findings + context_findings + timeline_findings
            stored_ids = self.store.add_findings_batch(all_findings)

            summary = {
                "total_sessions": len(sessions),
                "fact_hunter_findings": len(fact_findings),
                "context_weaver_findings": len(context_findings),
                "timeline_tracker_findings": len(timeline_findings),
                "total_findings": len(all_findings),
                "stored_ids": stored_ids,
                "store_stats": self.store.get_stats(),
            }

            self.tracer.enrich_span(
                metadata=summary,
                metrics={
                    "total_findings": len(all_findings),
                    "total_sessions_processed": len(sessions),
                },
            )
            return summary
