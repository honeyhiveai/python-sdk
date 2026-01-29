#!/usr/bin/env python3
"""
Client-Side Evaluators Example

Demonstrates client-side evaluators for both:
1. Online evaluation (metrics during tracing)
2. Offline evaluation (experiments with evaluators)

Corresponds to: evaluators/client_side.mdx
"""

import os

from dotenv import load_dotenv

from honeyhive import HoneyHiveTracer, enrich_session, enrich_span, trace
from honeyhive.experiments import evaluate

load_dotenv()


# =============================================================================
# PART 1: Online Evaluation (Metrics during tracing)
# =============================================================================


def run_online_evaluation():
    """Demonstrate adding metrics to traces in real-time."""
    print("\n" + "=" * 60)
    print("PART 1: Online Evaluation (Metrics during tracing)")
    print("=" * 60)

    HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
    )

    @trace
    def get_relevant_docs(query):
        """Retrieve documents and log retrieval metrics."""
        docs = [
            "Regular exercise reduces diabetes risk by 30%.",
            "Morning exercises have better impact on blood sugar.",
        ]
        # Span-level metric
        enrich_span(metrics={"retrieval_relevance": 0.85, "num_docs": len(docs)})
        return docs

    @trace
    def generate_response(docs, query):
        """Generate response and log generation metrics."""
        response = f"Based on {len(docs)} documents: Exercise helps manage diabetes."
        # Span-level metric
        enrich_span(metrics={"response_length": len(response), "contains_citations": True})
        return response

    @trace
    def rag_pipeline(query):
        """Main pipeline with session-level metrics."""
        docs = get_relevant_docs(query)
        response = generate_response(docs, query)

        # Session-level metrics
        enrich_session(
            metrics={
                "pipeline_metrics": {
                    "num_retrieved_docs": len(docs),
                    "query_length": len(query.split()),
                }
            }
        )
        return response

    # Run the pipeline
    query = "How does exercise affect diabetes?"
    result = rag_pipeline(query)
    print(f"Query: {query}")
    print(f"Result: {result}")
    print("✓ Online metrics logged to HoneyHive")


# =============================================================================
# PART 2: Offline Evaluation (Experiments with evaluators)
# =============================================================================


def run_offline_evaluation():
    """Demonstrate running experiments with client-side evaluators."""
    print("\n" + "=" * 60)
    print("PART 2: Offline Evaluation (Experiments with evaluators)")
    print("=" * 60)

    # Define evaluators - signature: (outputs, inputs, ground_truth)
    def accuracy_evaluator(outputs, inputs, ground_truth):
        """Check if output matches expected answer."""
        expected = ground_truth.get("expected", "")
        return 1.0 if expected.lower() in outputs.lower() else 0.0

    def length_evaluator(outputs, inputs, ground_truth):
        """Score based on response length."""
        return min(len(outputs) / 100, 1.0)

    # Define the function to evaluate - receives the full datapoint dict
    def my_classifier(datapoint):
        """Simple function that processes input and returns output."""
        inputs = datapoint.get("inputs", {})
        topic = inputs.get("topic", "unknown")
        return f"This is about {topic}. It's an important subject."

    # Define test dataset
    dataset = [
        {
            "inputs": {"topic": "machine learning"},
            "ground_truth": {"expected": "machine learning"},
        },
        {
            "inputs": {"topic": "neural networks"},
            "ground_truth": {"expected": "neural networks"},
        },
        {
            "inputs": {"topic": "data science"},
            "ground_truth": {"expected": "data science"},
        },
    ]

    # Run the experiment
    result = evaluate(
        function=my_classifier,
        dataset=dataset,
        evaluators=[accuracy_evaluator, length_evaluator],
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        name="Client-Side Evaluators Demo",
        verbose=True,
    )

    print(f"\n✓ Experiment completed: {result}")


# =============================================================================
# PART 3: Multi-step Evaluation in Experiments
# =============================================================================


def run_multistep_evaluation():
    """Demonstrate multi-step pipeline evaluation with span-level metrics."""
    print("\n" + "=" * 60)
    print("PART 3: Multi-step Evaluation in Experiments")
    print("=" * 60)

    # Session-level evaluator - signature: (outputs, inputs, ground_truth)
    def consistency_evaluator(outputs, inputs, ground_truth):
        """Check if output contains expected content."""
        expected = ground_truth.get("response", "")
        return 1.0 if expected.lower() in outputs.lower() else 0.0

    # Span-level metric function
    def compute_relevance(query, docs):
        """Compute relevance score (simplified)."""
        return 0.9 if docs else 0.0

    @trace
    def get_relevant_docs(query):
        """Retrieve documents with span-level metrics."""
        docs = ["Exercise reduces diabetes risk.", "Walking is recommended."]
        enrich_span(metrics={"retrieval_relevance": compute_relevance(query, docs)})
        return docs

    @trace
    def generate_response(docs, query):
        """Generate response based on docs."""
        return f"Based on {len(docs)} sources: Exercise helps with diabetes management."

    def rag_pipeline(datapoint):
        """Main RAG pipeline that processes a datapoint."""
        query = datapoint["inputs"]["query"]
        docs = get_relevant_docs(query)
        return generate_response(docs, query)

    # Test dataset
    dataset = [
        {
            "inputs": {"query": "How does exercise affect diabetes?"},
            "ground_truth": {"response": "exercise"},
        },
        {
            "inputs": {"query": "What are the benefits of walking?"},
            "ground_truth": {"response": "walking"},
        },
    ]

    # Run experiment
    result = evaluate(
        function=rag_pipeline,
        dataset=dataset,
        evaluators=[consistency_evaluator],
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        name="Multi-Step RAG Eval",
        verbose=True,
    )

    print(f"\n✓ Multi-step experiment completed: {result}")


if __name__ == "__main__":
    print("HoneyHive Client-Side Evaluators Example")
    print("=========================================")

    # Run all parts
    run_online_evaluation()
    run_offline_evaluation()
    run_multistep_evaluation()

    print("\n✓ All examples completed successfully!")
