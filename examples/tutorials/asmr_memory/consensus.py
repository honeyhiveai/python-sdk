"""
Decision Forest & Consensus - Multi-Variant Reasoning

Implements a 12-variant parallel reasoning system where each variant
analyzes the search results from a different perspective. A consensus
mechanism then aggregates their answers into a final response.

This maps to the "Decision Forest" and "Consensus" components
in the ASMR architecture diagram.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from openai import OpenAI

from honeyhive import HoneyHiveTracer

# 12 different reasoning perspectives for the decision forest
VARIANT_PROMPTS = [
    {
        "name": "fact_checker",
        "prompt": "You are a strict fact-checker. Only state things that are directly supported by the evidence. If something is uncertain, say so. Prioritize accuracy over completeness.",
    },
    {
        "name": "contextual_analyst",
        "prompt": "You are a contextual analyst. Look at the bigger picture and how different pieces of information relate to each other. Consider context and nuance in your answer.",
    },
    {
        "name": "temporal_expert",
        "prompt": "You are a temporal reasoning expert. Pay special attention to when things happened, how information has changed over time, and what the most current state of affairs is.",
    },
    {
        "name": "relationship_mapper",
        "prompt": "You are a relationship mapping expert. Focus on connections between people, places, events, and preferences. How do different facts relate to each other?",
    },
    {
        "name": "preference_interpreter",
        "prompt": "You are a preference and behavior interpreter. Focus on understanding what the person likes, dislikes, their habits, and behavioral patterns.",
    },
    {
        "name": "skeptical_verifier",
        "prompt": "You are a skeptical verifier. Question assumptions, look for contradictions, and only accept conclusions that are well-supported. Flag any inconsistencies you find.",
    },
    {
        "name": "comprehensive_synthesizer",
        "prompt": "You are a comprehensive synthesizer. Combine all available information into the most complete answer possible. Include relevant details and nuance.",
    },
    {
        "name": "concise_summarizer",
        "prompt": "You are a concise summarizer. Provide the most direct, brief answer possible. Cut through noise and deliver the core answer.",
    },
    {
        "name": "inference_specialist",
        "prompt": "You are an inference specialist. Go beyond literal facts to draw reasonable conclusions. What can be logically inferred from the available information?",
    },
    {
        "name": "contradiction_resolver",
        "prompt": "You are a contradiction resolver. When information conflicts, determine which is more reliable based on recency, source confidence, and corroboration.",
    },
    {
        "name": "detail_extractor",
        "prompt": "You are a detail extractor. Find specific details, numbers, names, dates, and precise information that directly answers the question.",
    },
    {
        "name": "holistic_reasoner",
        "prompt": "You are a holistic reasoner. Consider the full picture of what is known about this person/topic. Your answer should reflect a deep understanding of the overall context.",
    },
]

CONSENSUS_SYSTEM_PROMPT = """You are a consensus aggregator. You have received answers from 12 different reasoning perspectives about a question. Your job is to synthesize these into a single, authoritative final answer.

Rules:
1. If most variants agree on a fact, include it with high confidence
2. If variants disagree, go with the majority view unless a minority has stronger evidence
3. Weight the fact_checker and skeptical_verifier perspectives more heavily for accuracy
4. Weight the temporal_expert more heavily for time-related questions
5. Produce a clear, complete answer that represents the best consensus

Output a JSON object with:
- "final_answer": the consensus answer to the question
- "confidence": 0.0-1.0 overall confidence
- "agreement_level": "unanimous", "strong_majority", "majority", "split", or "contested"
- "key_facts": list of the most important facts supporting the answer
- "dissenting_views": any notable disagreements among the variants (or empty list)

Output ONLY valid JSON. No explanation text."""


def _parse_variant_response(response_text: str) -> Dict[str, Any]:
    """Parse a variant's response, falling back to plain text."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"answer": response_text, "confidence": 0.5}


def _parse_consensus_response(response_text: str) -> Dict[str, Any]:
    """Parse the consensus response."""
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
        "final_answer": response_text,
        "confidence": 0.5,
        "agreement_level": "unknown",
        "key_facts": [],
        "dissenting_views": [],
    }


class DecisionForest:
    """12-variant parallel reasoning with consensus aggregation.

    Each variant analyzes the search results from a unique perspective,
    and the consensus mechanism aggregates them into a final answer.
    """

    def __init__(
        self,
        openai_client: OpenAI,
        tracer: HoneyHiveTracer,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.client = openai_client
        self.tracer = tracer
        self.model = model

    def _run_variant(
        self,
        variant: Dict[str, str],
        query: str,
        search_context: str,
    ) -> Dict[str, Any]:
        """Run a single inference variant."""
        with self.tracer.start_span(f"variant_{variant['name']}") as span:
            if span:
                span.set_attribute("hh.event_type", "model")
                span.set_attribute("variant.name", variant["name"])

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"{variant['prompt']}\n\n"
                                "Given the search results and the question, "
                                "provide your answer as a JSON object with:\n"
                                '- "answer": your answer to the question\n'
                                '- "confidence": 0.0-1.0 confidence\n'
                                '- "key_evidence": list of key facts supporting your answer\n'
                                "Output ONLY valid JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Question: {query}\n\nSearch Results:\n{search_context}",
                        },
                    ],
                    temperature=0.3,
                )
            except Exception as e:
                self.tracer.enrich_span(metadata={"error": str(e)})
                return {
                    "answer": f"Error: {e}",
                    "confidence": 0.0,
                    "variant_name": variant["name"],
                }

            result = _parse_variant_response(
                response.choices[0].message.content or "{}"
            )
            result["variant_name"] = variant["name"]
            return result

    def _run_inference_forest(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Run all 12 variants in parallel (sequentially for simplicity)."""
        with self.tracer.start_span("parallel_inference_forest") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")
                span.set_attribute("num_variants", len(VARIANT_PROMPTS))

            # Build search context from the 3 search agent results
            search_context_parts = []
            for result in search_results:
                agent = result.get("agent", "unknown")
                answer = result.get("answer", "")
                confidence = result.get("confidence", 0)
                reasoning = result.get("reasoning", "")
                search_context_parts.append(
                    f"[{agent}] (confidence: {confidence}): {answer}\n"
                    f"  Reasoning: {reasoning}"
                )
            search_context = "\n\n".join(search_context_parts)

            # Run all variants
            variant_results = []
            for variant in VARIANT_PROMPTS:
                result = self._run_variant(variant, query, search_context)
                variant_results.append(result)

            self.tracer.enrich_span(
                metadata={"variants_completed": len(variant_results)},
                metrics={"num_variants": len(variant_results)},
            )
            return variant_results

    def _run_consensus(
        self,
        query: str,
        variant_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Aggregate variant answers into a consensus result."""
        with self.tracer.start_span("consensus_aggregation") as span:
            if span:
                span.set_attribute("hh.event_type", "model")
                span.set_attribute("num_inputs", len(variant_results))

            # Format variant answers for the consensus prompt
            variant_summary_parts = []
            for vr in variant_results:
                name = vr.get("variant_name", "unknown")
                answer = vr.get("answer", "")
                confidence = vr.get("confidence", 0)
                variant_summary_parts.append(
                    f"[{name}] (confidence: {confidence}): {answer}"
                )
            variant_summary = "\n\n".join(variant_summary_parts)

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": CONSENSUS_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": (
                                f"Question: {query}\n\n"
                                f"Variant Answers ({len(variant_results)} perspectives):\n\n"
                                f"{variant_summary}"
                            ),
                        },
                    ],
                    temperature=0.0,
                )
            except Exception as e:
                self.tracer.enrich_span(metadata={"error": str(e)})
                return {
                    "final_answer": f"Error during consensus: {e}",
                    "confidence": 0.0,
                    "agreement_level": "error",
                    "key_facts": [],
                    "dissenting_views": [],
                }

            result = _parse_consensus_response(
                response.choices[0].message.content or "{}"
            )

            self.tracer.enrich_span(
                metadata={
                    "agreement_level": result.get("agreement_level", "unknown"),
                    "confidence": result.get("confidence", 0),
                },
            )
            return result

    def decide(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run the full decision forest pipeline: 12 variants + consensus.

        Args:
            query: The user's question
            search_results: Results from the 3 search agents

        Returns:
            Consensus result with final_answer, confidence, agreement_level, etc.
        """
        with self.tracer.start_span("decision_forest_and_consensus") as span:
            if span:
                span.set_attribute("hh.event_type", "chain")

            variant_results = self._run_inference_forest(query, search_results)
            consensus = self._run_consensus(query, variant_results)

            consensus["variant_count"] = len(variant_results)
            consensus["search_agent_count"] = len(search_results)

            self.tracer.enrich_span(
                metadata={
                    "final_confidence": consensus.get("confidence", 0),
                    "agreement_level": consensus.get("agreement_level", "unknown"),
                },
            )
            return consensus
