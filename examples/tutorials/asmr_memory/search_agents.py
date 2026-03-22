"""
Search Agents - Active Search Orchestration

Three specialized search agents that query the knowledge store
to answer user questions:
1. Direct Seeker - exact match, literal facts
2. Inference Engine - related context, implications
3. Temporal Reasoner - timeline, duration, state changes

This maps to the "Active Search" component in the ASMR architecture diagram.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from openai import OpenAI

from honeyhive import HoneyHiveTracer

from .knowledge_store import KnowledgeStore

DIRECT_SEEKER_SYSTEM_PROMPT = """You are the Direct Seeker search agent. Your job is to find exact, literal answers to the user's question from the provided knowledge base.

Focus on:
- Exact match: Find facts that directly answer the question
- Literal interpretation: Take the question at face value
- Recent-first: Prefer more recent findings when multiple answers exist
- High confidence: Only include findings you are confident about

Given the user's question and the knowledge base context, produce a JSON object with:
- "relevant_findings": list of the most relevant fact strings from the knowledge base
- "answer": your direct answer based on those findings
- "confidence": 0.0-1.0 how confident you are
- "reasoning": brief explanation of how you arrived at the answer

Output ONLY valid JSON. No explanation text."""

INFERENCE_ENGINE_SYSTEM_PROMPT = """You are the Inference Engine search agent. Your job is to find answers that require reasoning, inference, or connecting multiple pieces of information.

Focus on:
- Related context: Find information that helps answer the question even if not directly stated
- Implications: What can be inferred from the combination of known facts
- Cross-referencing: Connect facts from different sessions or time periods
- Pattern-based answers: Use identified patterns to answer questions

Given the user's question and the knowledge base context, produce a JSON object with:
- "relevant_findings": list of findings that support your inference
- "answer": your inferred answer based on connecting the facts
- "confidence": 0.0-1.0 how confident you are
- "reasoning": explanation of the inference chain

Output ONLY valid JSON. No explanation text."""

TEMPORAL_REASONER_SYSTEM_PROMPT = """You are the Temporal Reasoner search agent. Your job is to answer questions that involve time, sequence, change, or evolution of information.

Focus on:
- Timeline construction: Order events and facts chronologically
- State changes: Track how information has changed over time
- Duration and frequency: Answer questions about how long or how often
- Supersession: When newer information replaces older information, use the latest

Given the user's question and the knowledge base context, produce a JSON object with:
- "relevant_findings": list of temporally relevant findings
- "answer": your answer considering the temporal dimension
- "confidence": 0.0-1.0 how confident you are
- "reasoning": explanation of the temporal reasoning applied

Output ONLY valid JSON. No explanation text."""


def _parse_search_response(response_text: str) -> Dict[str, Any]:
    """Parse the JSON response from a search agent."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response_text[start:end])
            except json.JSONDecodeError:
                pass
    return {
        "relevant_findings": [],
        "answer": "Unable to parse response",
        "confidence": 0.0,
        "reasoning": "JSON parse error",
    }


class SearchAgents:
    """Orchestrates three search agents for agentic retrieval.

    Each agent approaches the question from a different perspective,
    and their combined results feed into the decision forest.
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

    def _run_direct_seeker(
        self,
        query: str,
        context: str,
    ) -> Dict[str, Any]:
        """Search Agent 1: Direct Seeker - exact match, literal facts."""
        with self.tracer.start_span("direct_seeker_agent") as span:
            if span:
                span.set_attribute("hh.event_type", "tool")
                span.set_attribute("agent.name", "direct_seeker")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DIRECT_SEEKER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nKnowledge Base:\n{context}",
                    },
                ],
                temperature=0.0,
            )

            result = _parse_search_response(response.choices[0].message.content or "{}")
            result["agent"] = "direct_seeker"

            self.tracer.enrich_span(
                metadata={"confidence": result.get("confidence", 0)},
            )
            return result

    def _run_inference_engine(
        self,
        query: str,
        context: str,
    ) -> Dict[str, Any]:
        """Search Agent 2: Inference Engine - related context, implications."""
        with self.tracer.start_span("inference_engine_agent") as span:
            if span:
                span.set_attribute("hh.event_type", "tool")
                span.set_attribute("agent.name", "inference_engine")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INFERENCE_ENGINE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nKnowledge Base:\n{context}",
                    },
                ],
                temperature=0.2,
            )

            result = _parse_search_response(response.choices[0].message.content or "{}")
            result["agent"] = "inference_engine"

            self.tracer.enrich_span(
                metadata={"confidence": result.get("confidence", 0)},
            )
            return result

    def _run_temporal_reasoner(
        self,
        query: str,
        context: str,
    ) -> Dict[str, Any]:
        """Search Agent 3: Temporal Reasoner - timeline, duration, state changes."""
        with self.tracer.start_span("temporal_reasoner_agent") as span:
            if span:
                span.set_attribute("hh.event_type", "tool")
                span.set_attribute("agent.name", "temporal_reasoner")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": TEMPORAL_REASONER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nKnowledge Base:\n{context}",
                    },
                ],
                temperature=0.1,
            )

            result = _parse_search_response(response.choices[0].message.content or "{}")
            result["agent"] = "temporal_reasoner"

            self.tracer.enrich_span(
                metadata={"confidence": result.get("confidence", 0)},
            )
            return result

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Run all 3 search agents and return combined results.

        The knowledge store is queried for relevant context, which is then
        passed to each search agent for analysis from their perspective.
        """
        with self.tracer.start_span("agentic_search_orchestration") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")
                span.set_attribute("query", query)

            # Build context from knowledge store
            text_results = self.store.search_text(query)
            context = self.store.to_context_string(text_results)

            if not context.strip():
                context = self.store.to_context_string(self.store.get_all())

            # Run all three search agents
            direct_result = self._run_direct_seeker(query, context)
            inference_result = self._run_inference_engine(query, context)
            temporal_result = self._run_temporal_reasoner(query, context)

            results = [direct_result, inference_result, temporal_result]

            self.tracer.enrich_span(
                metadata={
                    "num_agents": 3,
                    "context_findings_count": len(text_results),
                },
            )
            return results
