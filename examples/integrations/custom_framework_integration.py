"""
Custom Framework Integration Example

This example demonstrates how to integrate HoneyHive with a custom framework
that uses OpenTelemetry directly. This serves as a template for integrating
with any non-instrumentor framework.
"""

import os
import time
import threading
from typing import Dict, Any, List
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from honeyhive import HoneyHiveTracer


class CustomAIFramework:
    """
    Example custom AI framework that uses OpenTelemetry directly.

    This simulates a framework that:
    - Sets up its own TracerProvider
    - Creates spans for operations
    - Manages its own tracing context
    """

    def __init__(self, name: str = "CustomAI", setup_provider: bool = True):
        self.name = name
        self.setup_provider = setup_provider
        self._operations: List[Dict[str, Any]] = []

        if setup_provider:
            # Framework sets up its own TracerProvider
            self.provider = TracerProvider()
            trace.set_tracer_provider(self.provider)

        # Get tracer (will use whatever provider is currently set)
        self.tracer = trace.get_tracer(f"{name}.tracer")

    def process_text(
        self, text: str, operation_type: str = "analysis"
    ) -> Dict[str, Any]:
        """Process text with tracing."""
        with self.tracer.start_as_current_span(f"{self.name}.process_text") as span:
            # Set framework-specific attributes
            span.set_attribute("framework.name", self.name)
            span.set_attribute("framework.version", "1.0.0")
            span.set_attribute("operation.type", operation_type)
            span.set_attribute("text.length", len(text))
            span.set_attribute("text.word_count", len(text.split()))

            # Simulate processing steps
            with self.tracer.start_as_current_span("preprocessing") as prep_span:
                prep_span.set_attribute("step.name", "preprocessing")
                time.sleep(0.01)  # Simulate work
                processed_text = text.lower().strip()
                prep_span.set_attribute("preprocessing.result", "completed")

            with self.tracer.start_as_current_span("analysis") as analysis_span:
                analysis_span.set_attribute("step.name", "analysis")
                time.sleep(0.02)  # Simulate work

                # Simulate analysis results
                sentiment = "positive" if "good" in processed_text else "neutral"
                confidence = 0.85

                analysis_span.set_attribute("analysis.sentiment", sentiment)
                analysis_span.set_attribute("analysis.confidence", confidence)

            with self.tracer.start_as_current_span("postprocessing") as post_span:
                post_span.set_attribute("step.name", "postprocessing")
                time.sleep(0.005)  # Simulate work

                result = {
                    "original_text": text,
                    "processed_text": processed_text,
                    "operation_type": operation_type,
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "framework": self.name,
                    "timestamp": time.time(),
                    "span_id": format(span.get_span_context().span_id, "016x"),
                    "trace_id": format(span.get_span_context().trace_id, "032x"),
                }

                post_span.set_attribute("postprocessing.result", "completed")

            # Set final span attributes
            span.set_attribute("operation.result", "success")
            span.set_attribute("operation.sentiment", sentiment)
            span.set_attribute("operation.confidence", confidence)

            self._operations.append(result)
            return result

    def batch_process(
        self, texts: List[str], batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """Process multiple texts in batches."""
        with self.tracer.start_as_current_span(f"{self.name}.batch_process") as span:
            span.set_attribute("batch.size", len(texts))
            span.set_attribute("batch.max_size", batch_size)
            span.set_attribute(
                "batch.count", (len(texts) + batch_size - 1) // batch_size
            )

            results = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_num = i // batch_size + 1

                with self.tracer.start_as_current_span(
                    f"batch_{batch_num}"
                ) as batch_span:
                    batch_span.set_attribute("batch.number", batch_num)
                    batch_span.set_attribute("batch.items", len(batch))

                    batch_results = []
                    for j, text in enumerate(batch):
                        with self.tracer.start_as_current_span(
                            f"item_{j+1}"
                        ) as item_span:
                            item_span.set_attribute("item.index", i + j)
                            item_span.set_attribute("item.text_length", len(text))

                            result = self.process_text(text, "batch_analysis")
                            batch_results.append(result)

                    results.extend(batch_results)
                    batch_span.set_attribute("batch.processed", len(batch_results))

            span.set_attribute("batch.total_processed", len(results))
            return results

    def get_operations(self) -> List[Dict[str, Any]]:
        """Get all processed operations."""
        return self._operations.copy()

    def reset(self):
        """Reset operation history."""
        self._operations.clear()


def demonstrate_honeyhive_first_integration():
    """Demonstrate HoneyHive initialized first (main provider strategy)."""
    print("🚀 Integration Pattern 1: HoneyHive First (Main Provider)")
    print("=" * 60)

    # Step 1: Initialize HoneyHive first
    print("1. Initializing HoneyHive tracer...")
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "custom-framework-demo"),
        source="custom-framework-example",
        test_mode=True,
        verbose=True,
    )
    print(f"   ✅ HoneyHive tracer initialized (Session: {tracer.session_id})")

    # Step 2: Initialize custom framework (without setting up its own provider)
    print("2. Initializing custom framework...")
    framework = CustomAIFramework("CustomAI-HH-First", setup_provider=False)
    print("   ✅ Custom framework initialized (using HoneyHive's provider)")

    # Step 3: Execute operations
    print("3. Executing traced operations...")

    # Single operation
    result1 = framework.process_text(
        "This is a good example of integration!", "sentiment"
    )
    print(
        f"   Single operation result: {result1['sentiment']} ({result1['confidence']})"
    )

    # Batch operation
    texts = [
        "Hello world!",
        "This is great!",
        "Processing multiple texts",
        "Custom framework integration",
        "HoneyHive tracing works!",
    ]
    batch_results = framework.batch_process(texts, batch_size=2)
    print(f"   Batch operation processed: {len(batch_results)} texts")

    print("   ✅ All operations completed successfully")
    print()


def demonstrate_framework_first_integration():
    """Demonstrate framework initialized first (secondary provider strategy)."""
    print("🚀 Integration Pattern 2: Framework First (Secondary Provider)")
    print("=" * 65)

    # Step 1: Initialize custom framework first (sets up its own provider)
    print("1. Initializing custom framework...")
    framework = CustomAIFramework("CustomAI-Framework-First", setup_provider=True)
    print("   ✅ Custom framework initialized (with its own TracerProvider)")

    # Step 2: Initialize HoneyHive (will integrate with existing provider)
    print("2. Initializing HoneyHive tracer...")
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "custom-framework-demo"),
        source="custom-framework-example",
        test_mode=True,
        verbose=True,
    )
    print(
        f"   ✅ HoneyHive integrated with existing provider (Session: {tracer.session_id})"
    )

    # Step 3: Execute operations
    print("3. Executing traced operations...")

    # Test operations
    result1 = framework.process_text("Framework first integration test", "integration")
    print(f"   Integration test result: {result1['sentiment']}")

    # Test batch processing
    texts = ["Test 1", "Test 2", "Test 3"]
    batch_results = framework.batch_process(texts)
    print(f"   Batch test processed: {len(batch_results)} items")

    print("   ✅ All operations completed successfully")
    print()


def demonstrate_multi_framework_integration():
    """Demonstrate multiple frameworks with single HoneyHive tracer."""
    print("🚀 Integration Pattern 3: Multiple Frameworks")
    print("=" * 50)

    # Initialize HoneyHive first
    print("1. Initializing HoneyHive tracer...")
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "multi-framework-demo"),
        source="multi-framework-example",
        test_mode=True,
        verbose=False,  # Reduce noise
    )
    print(f"   ✅ HoneyHive tracer initialized")

    # Initialize multiple frameworks
    print("2. Initializing multiple frameworks...")
    framework_a = CustomAIFramework("FrameworkA", setup_provider=False)
    framework_b = CustomAIFramework("FrameworkB", setup_provider=False)
    framework_c = CustomAIFramework("FrameworkC", setup_provider=False)
    print("   ✅ Three frameworks initialized")

    # Execute operations across frameworks
    print("3. Executing operations across frameworks...")

    # Create a workflow that uses multiple frameworks
    from opentelemetry import trace

    otel_tracer = trace.get_tracer("multi-framework-workflow")

    with otel_tracer.start_as_current_span("multi-framework-workflow") as workflow_span:
        workflow_span.set_attribute("workflow.frameworks", 3)
        workflow_span.set_attribute("workflow.type", "multi-framework")

        # Framework A: Initial processing
        with otel_tracer.start_as_current_span("framework-a-processing") as fa_span:
            fa_span.set_attribute("framework.name", "FrameworkA")
            result_a = framework_a.process_text(
                "Initial text for processing", "initial"
            )
            fa_span.set_attribute("processing.result", result_a["sentiment"])

        # Framework B: Secondary analysis
        with otel_tracer.start_as_current_span("framework-b-analysis") as fb_span:
            fb_span.set_attribute("framework.name", "FrameworkB")
            result_b = framework_b.process_text(result_a["processed_text"], "secondary")
            fb_span.set_attribute("analysis.result", result_b["sentiment"])

        # Framework C: Final processing
        with otel_tracer.start_as_current_span("framework-c-finalization") as fc_span:
            fc_span.set_attribute("framework.name", "FrameworkC")
            result_c = framework_c.process_text("Final processing step", "final")
            fc_span.set_attribute("finalization.result", result_c["sentiment"])

        workflow_span.set_attribute("workflow.status", "completed")
        workflow_span.set_attribute("workflow.final_sentiment", result_c["sentiment"])

    print(
        f"   Workflow completed: {result_a['sentiment']} → {result_b['sentiment']} → {result_c['sentiment']}"
    )
    print("   ✅ Multi-framework workflow completed successfully")
    print()


def demonstrate_concurrent_operations():
    """Demonstrate concurrent operations with custom framework."""
    print("🚀 Integration Pattern 4: Concurrent Operations")
    print("=" * 50)

    # Initialize HoneyHive
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "concurrent-demo"),
        source="concurrent-example",
        test_mode=True,
        verbose=False,
    )

    # Initialize framework
    framework = CustomAIFramework("ConcurrentFramework", setup_provider=False)

    print("1. Starting concurrent operations...")

    def worker_task(worker_id: int, texts: List[str]) -> List[Dict[str, Any]]:
        """Worker function for concurrent processing."""
        results = []
        for i, text in enumerate(texts):
            result = framework.process_text(
                f"Worker {worker_id}: {text}", f"concurrent_worker_{worker_id}"
            )
            results.append(result)
        return results

    # Prepare work
    texts_per_worker = [
        ["Text A1", "Text A2", "Text A3"],
        ["Text B1", "Text B2", "Text B3"],
        ["Text C1", "Text C2", "Text C3"],
        ["Text D1", "Text D2", "Text D3"],
    ]

    # Execute concurrent operations
    import concurrent.futures

    start_time = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(worker_task, i, texts)
            for i, texts in enumerate(texts_per_worker)
        ]

        all_results = []
        for future in concurrent.futures.as_completed(futures):
            worker_results = future.result()
            all_results.extend(worker_results)

    end_time = time.perf_counter()

    print(f"2. Concurrent processing completed:")
    print(f"   Total operations: {len(all_results)}")
    print(f"   Total time: {end_time - start_time:.3f}s")
    print(
        f"   Average per operation: {(end_time - start_time) / len(all_results):.3f}s"
    )
    print("   ✅ Concurrent operations completed successfully")
    print()


def demonstrate_error_handling():
    """Demonstrate error handling in custom framework integration."""
    print("🔧 Error Handling and Resilience")
    print("=" * 35)

    # Initialize HoneyHive with error handling
    try:
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "demo-api-key"),
            project=os.getenv("HH_PROJECT", "error-demo"),
            source="error-handling-example",
            test_mode=True,
            verbose=False,
        )
        print("1. ✅ HoneyHive initialized successfully")
    except Exception as e:
        print(f"1. ❌ HoneyHive initialization failed: {e}")
        return

    # Initialize framework with error handling
    try:
        framework = CustomAIFramework("ErrorHandlingFramework", setup_provider=False)
        print("2. ✅ Framework initialized successfully")
    except Exception as e:
        print(f"2. ❌ Framework initialization failed: {e}")
        return

    # Test operations with error handling
    print("3. Testing operations with error handling...")

    test_cases = [
        ("Normal text", "normal"),
        ("", "empty"),  # Edge case: empty text
        ("Very " * 1000 + "long text", "long"),  # Edge case: very long text
        (None, "null"),  # Edge case: None input
    ]

    for i, (text, case_type) in enumerate(test_cases, 1):
        try:
            if text is None:
                # Simulate handling None input
                print(f"   Case {i} ({case_type}): Skipping None input")
                continue

            result = framework.process_text(text, case_type)
            print(f"   Case {i} ({case_type}): ✅ Success - {result['sentiment']}")

        except Exception as e:
            print(f"   Case {i} ({case_type}): ❌ Error - {e}")

    print("   ✅ Error handling tests completed")
    print()


def main():
    """Run all integration examples."""
    print("🎯 Custom Framework Integration Examples")
    print("=" * 45)
    print()

    # Check environment
    if not os.getenv("HH_API_KEY"):
        print("⚠️  HH_API_KEY not set - using demo mode")
    if not os.getenv("HH_PROJECT"):
        print("⚠️  HH_PROJECT not set - using default project names")
    print()

    try:
        # Run integration patterns
        demonstrate_honeyhive_first_integration()
        demonstrate_framework_first_integration()
        demonstrate_multi_framework_integration()
        demonstrate_concurrent_operations()
        demonstrate_error_handling()

        print("🎉 All custom framework integration examples completed successfully!")

    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
