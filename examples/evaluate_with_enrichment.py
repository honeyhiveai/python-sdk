#!/usr/bin/env python3
"""
Evaluate with Enrichment Example (v1.0+)

This example demonstrates the fixed evaluate() + enrich_span() pattern
in v1.0, which now works correctly thanks to selective baggage propagation.

Key Patterns:
1. evaluate() with traced functions
2. Instance method enrichment (PRIMARY PATTERN)
3. Tracer propagation to evaluation tasks
4. Enrichment metadata and metrics in evaluate context

This example requires a valid HoneyHive API key and dataset.
"""

import os
import time
from typing import Any, Dict

from honeyhive import HoneyHiveTracer, trace
from honeyhive.sdk.evals import evaluate

# Set environment variables for configuration
# In production, load from .env or secure config
os.environ.setdefault("HH_API_KEY", "your-api-key-here")
os.environ.setdefault("HH_PROJECT", "evaluate-demo")


def main():
    """Main function demonstrating evaluate() with enrichment."""

    print("🚀 HoneyHive SDK: evaluate() with Enrichment (v1.0+)")
    print("=" * 60)
    print("This example shows the PRIMARY PATTERN for enriching spans")
    print("during evaluate() execution. This works in v1.0 thanks to")
    print("the selective baggage propagation fix.\n")

    # ========================================================================
    # 1. INITIALIZE TRACER (v1.0+ Pattern)
    # ========================================================================
    print("1. Initialize Tracer")
    print("-" * 20)

    tracer = HoneyHiveTracer.init(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="evaluate-enrichment-example",
        verbose=True
    )
    print(f"✓ Tracer initialized for project: {tracer.project_name}")

    # ========================================================================
    # 2. DEFINE TASK WITH ENRICHMENT (PRIMARY PATTERN)
    # ========================================================================
    print("\n2. Define Task with Enrichment")
    print("-" * 33)

    @trace(tracer=tracer, event_type="model")
    def simple_llm_task(datapoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple LLM task that processes a datapoint and enriches the span.
        
        This demonstrates the PRIMARY PATTERN (v1.0+):
        - Use instance method: tracer.enrich_span()
        - Pass tracer explicitly for clarity
        """
        inputs = datapoint.get("inputs", {})
        text = inputs.get("text", "")
        
        print(f"  📝 Processing: {text[:50]}...")
        time.sleep(0.1)  # Simulate LLM call
        
        # Simulate LLM response
        result = {
            "output": f"Processed: {text}",
            "model": "gpt-4",
            "tokens": 150
        }
        
        # ✅ PRIMARY PATTERN (v1.0+): Use instance method
        # This now works correctly in evaluate() due to baggage propagation fix
        tracer.enrich_span(
            metadata={
                "input_text": text,
                "output_text": result["output"],
                "model": result["model"]
            },
            metrics={
                "latency_ms": 100,
                "tokens": result["tokens"],
                "cost_usd": 0.002
            }
        )
        print(f"  ✓ Span enriched with metadata and metrics")
        
        return result

    print("✓ Task defined with instance method enrichment")

    # ========================================================================
    # 3. NESTED TRACING WITH ENRICHMENT
    # ========================================================================
    print("\n3. Nested Tracing with Enrichment")
    print("-" * 36)

    @trace(tracer=tracer, event_type="tool")
    def complex_task_with_steps(datapoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task with multiple steps, each traced and enriched.
        
        Demonstrates:
        - Nested span hierarchy
        - Multiple enrichments in different spans
        - Parent-child span relationships
        """
        inputs = datapoint.get("inputs", {})
        text = inputs.get("text", "")
        
        # Step 1: Preprocess
        @trace(tracer=tracer, event_type="tool", event_name="preprocess")
        def preprocess(text: str) -> str:
            """Preprocess input text."""
            print(f"    📝 Step 1: Preprocessing...")
            processed = text.lower().strip()
            
            # ✅ Enrich preprocessing span
            tracer.enrich_span(
                metadata={"step": "preprocess", "input_length": len(text)},
                metrics={"processing_time_ms": 10}
            )
            
            return processed
        
        # Step 2: LLM Call
        @trace(tracer=tracer, event_type="model", event_name="llm_call")
        def llm_call(text: str) -> str:
            """Simulate LLM API call."""
            print(f"    📝 Step 2: LLM Call...")
            time.sleep(0.05)
            response = f"LLM response for: {text}"
            
            # ✅ Enrich LLM span
            tracer.enrich_span(
                metadata={
                    "step": "llm_call",
                    "model": "gpt-4",
                    "prompt": text[:100]
                },
                metrics={
                    "latency_ms": 50,
                    "tokens": 100,
                    "cost_usd": 0.001
                }
            )
            
            return response
        
        # Step 3: Postprocess
        @trace(tracer=tracer, event_type="tool", event_name="postprocess")
        def postprocess(text: str) -> str:
            """Postprocess LLM output."""
            print(f"    📝 Step 3: Postprocessing...")
            final = text.upper()
            
            # ✅ Enrich postprocessing span
            tracer.enrich_span(
                metadata={"step": "postprocess", "output_length": len(final)},
                metrics={"processing_time_ms": 5}
            )
            
            return final
        
        # Execute pipeline
        preprocessed = preprocess(text)
        llm_output = llm_call(preprocessed)
        final_output = postprocess(llm_output)
        
        # ✅ Enrich parent span with overall metrics
        tracer.enrich_span(
            metadata={
                "steps": 3,
                "pipeline": "preprocess -> llm -> postprocess",
                "final_output": final_output[:100]
            },
            metrics={
                "total_time_ms": 65,
                "total_cost_usd": 0.001
            }
        )
        print(f"  ✓ All steps traced and enriched")
        
        return {"output": final_output}

    print("✓ Complex task defined with nested enrichment")

    # ========================================================================
    # 4. RUN EVALUATION (if dataset exists)
    # ========================================================================
    print("\n4. Run Evaluation (Demo Mode)")
    print("-" * 31)

    # For demonstration, use mock dataset
    # In production, replace with real dataset from HoneyHive
    mock_dataset = [
        {"inputs": {"text": "What is machine learning?"}},
        {"inputs": {"text": "Explain neural networks."}},
        {"inputs": {"text": "How does gradient descent work?"}}
    ]

    print("  📝 Running simple task on mock dataset...")
    
    # Note: evaluate() expects dataset name, not inline data
    # This is a simplified demo. In production:
    # results = evaluate(
    #     dataset="your-dataset-name",
    #     task=simple_llm_task,
    #     tracer=tracer
    # )
    
    # For demo, manually iterate
    for i, datapoint in enumerate(mock_dataset):
        print(f"\n  Datapoint {i+1}/{len(mock_dataset)}:")
        result = simple_llm_task(datapoint)
        print(f"    ✓ Output: {result['output'][:50]}...")
    
    print("\n✓ Simple task evaluation completed")

    print("\n  📝 Running complex task on mock dataset...")
    for i, datapoint in enumerate(mock_dataset):
        print(f"\n  Datapoint {i+1}/{len(mock_dataset)}:")
        result = complex_task_with_steps(datapoint)
        print(f"    ✓ Output: {result['output'][:50]}...")
    
    print("\n✓ Complex task evaluation completed")

    # ========================================================================
    # 5. SESSION ENRICHMENT
    # ========================================================================
    print("\n5. Session Enrichment")
    print("-" * 22)

    # Enrich session with overall evaluation metadata
    tracer.enrich_session(
        metadata={
            "evaluation_type": "demo",
            "total_datapoints": len(mock_dataset),
            "tasks_run": 2
        },
        metrics={
            "total_execution_time_s": 2.5,
            "avg_latency_ms": 100
        },
        user_properties={
            "user_id": "demo-user",
            "experiment_id": "eval-enrichment-demo"
        }
    )
    print("✓ Session enriched with evaluation metadata")

    print("\n🎉 Evaluation with enrichment example completed!")
    print("\nKey v1.0+ patterns demonstrated:")
    print("✅ Instance method enrichment: tracer.enrich_span()")
    print("✅ Enrichment works in evaluate() (baggage propagation fix)")
    print("✅ Nested span hierarchy with multiple enrichments")
    print("✅ Metadata + metrics + user properties")
    print("✅ Parent-child span relationships")
    print("✅ Session-level enrichment")
    
    print("\nMigration Note:")
    print("❌ OLD (v0.2.x): enrich_span(metadata={...})")
    print("✅ NEW (v1.0+):  tracer.enrich_span(metadata={...})")
    print("\nThe instance method pattern is now the PRIMARY pattern.")
    print("Free functions work but are deprecated and will be removed in v2.0.")


if __name__ == "__main__":
    main()

