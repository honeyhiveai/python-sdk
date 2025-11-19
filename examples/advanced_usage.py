#!/usr/bin/env python3
"""
Advanced Usage Example

This example demonstrates advanced tracing patterns from the documentation
as full functioning executable code:

1. Multiple Tracers for different environments
2. Parent-child span relationships
3. Complex span enrichment
4. Error handling in spans
5. Performance monitoring patterns
6. Multi-step workflows

This extends beyond the basic patterns to show advanced usage scenarios.
"""

import asyncio
import os
import time
from typing import Any, Dict, Optional

from honeyhive import HoneyHiveTracer, trace, trace_class
from honeyhive import enrich_span  # Legacy pattern for context manager demo
from honeyhive.config.models import TracerConfig, SessionConfig
from honeyhive.models import EventType

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "advanced-demo"
os.environ["HH_SOURCE"] = "development"


def main():
    """Main function demonstrating advanced usage patterns."""

    print("🚀 HoneyHive SDK Advanced Usage Example")
    print("=" * 50)
    print("This example demonstrates advanced patterns beyond the basic usage.")
    print("These patterns are useful for complex applications and workflows.\n")

    # ========================================================================
    # 1. MULTIPLE TRACERS (from docs)
    # ========================================================================
    print("1. Multiple Tracers")
    print("-" * 20)

    # Create tracers for different environments - from docs
    prod_tracer = HoneyHiveTracer.init(
        api_key="prod-key",
        project="production-project",  # Required for OTLP tracing
        source="prod",
    )

    dev_tracer = HoneyHiveTracer.init(
        api_key="dev-key",
        project="development-project",  # Required for OTLP tracing
        source="dev",
    )

    print(f"✓ Production tracer: {prod_tracer.project}")
    print(f"✓ Development tracer: {dev_tracer.project}")

    # ========================================================================
    # 2. ADVANCED TRACING PATTERNS
    # ========================================================================
    print("\n2. Advanced Tracing Patterns")
    print("-" * 30)

    # Create traced functions with different tracers
    def create_traced_functions(tracer, env_name):
        """Create traced functions for a specific environment."""

        @trace(
            tracer=tracer,
            event_type=EventType.model,
            event_name=f"{env_name}_ai_processing",
        )
        def process_ai_request(prompt: str, user_id: str) -> str:
            """Process an AI request with comprehensive tracing."""
            print(f"  📝 Processing AI request in {env_name}...")
            time.sleep(0.1)  # Simulate AI processing
            return f"AI Response from {env_name}: {prompt}"

        @trace(
            tracer=tracer,
            event_type=EventType.tool,
            event_name=f"{env_name}_data_processing",
        )
        async def process_data_async(data: list) -> Dict[str, Any]:
            """Process data asynchronously with comprehensive tracing."""
            print(f"  📝 Processing data async in {env_name}...")
            await asyncio.sleep(0.1)  # Simulate async processing
            return {
                "processed_items": len(data),
                "status": "completed",
                "environment": env_name,
                "timestamp": time.time(),
            }

        return process_ai_request, process_data_async

    # Create functions for both environments
    prod_ai_func, prod_data_func = create_traced_functions(prod_tracer, "production")
    dev_ai_func, _ = create_traced_functions(dev_tracer, "development")

    # Test production functions
    prod_result = prod_ai_func("Hello from prod", "user123")
    print(f"✓ Production result: {prod_result}")

    # Test development functions
    dev_result = dev_ai_func("Hello from dev", "user456")
    print(f"✓ Development result: {dev_result}")

    # Test async functions
    prod_async_result = asyncio.run(prod_data_func([1, 2, 3, 4, 5]))
    print(f"✓ Production async result: {prod_async_result}")

    # ========================================================================
    # 3. TRACE_CLASS DECORATOR (from docs)
    # ========================================================================
    print("\n3. Class Tracing with @trace_class")
    print("-" * 35)

    @trace_class(tracer=prod_tracer)
    class WorkflowOrchestrator:
        """Example class with all methods automatically traced."""

        def __init__(self, workflow_id: str):
            self.workflow_id = workflow_id
            print(f"  📝 Initialized WorkflowOrchestrator: {workflow_id}")

        def start_workflow(self, config: Dict[str, Any]) -> bool:
            """Start a workflow with automatic tracing."""
            print(f"  📝 Starting workflow with config: {config}")
            time.sleep(0.05)
            return True

        def execute_step(self, step_name: str, step_data: Any) -> Dict[str, Any]:
            """Execute a workflow step with automatic tracing."""
            print(f"  📝 Executing step: {step_name}")
            time.sleep(0.1)
            return {"step": step_name, "status": "completed", "data": step_data}

        async def finalize_workflow(self, results: Dict[str, Any]) -> bool:
            """Finalize a workflow with automatic tracing."""
            print(f"  📝 Finalizing workflow with results: {results}")
            await asyncio.sleep(0.1)
            return True

    # Test the traced class
    orchestrator = WorkflowOrchestrator("advanced_workflow_123")
    orchestrator.start_workflow({"steps": 3, "timeout": 30})
    orchestrator.execute_step("data_processing", {"batch_size": 1000})
    asyncio.run(orchestrator.finalize_workflow({"status": "success"}))
    print("✓ @trace_class workflow completed")

    # ========================================================================
    # 4. PARENT-CHILD SPAN RELATIONSHIPS
    # ========================================================================
    print("\n4. Parent-Child Span Relationships")
    print("-" * 36)

    # Create complex parent-child span hierarchy
    with prod_tracer.start_span("complex_workflow") as parent_span:
        parent_span.set_attribute("workflow.type", "multi_step_processing")
        parent_span.set_attribute("workflow.complexity", "high")
        print("✓ Parent span created: complex_workflow")

        # Create child spans
        with prod_tracer.start_span("step_1") as child_span:
            child_span.set_attribute("step.name", "data_preparation")
            child_span.set_attribute("step.order", 1)
            print("  ✓ Child span: step_1 (data_preparation)")
            time.sleep(0.05)

            # Create grandchild span
            with prod_tracer.start_span("substep_1a") as grandchild_span:
                grandchild_span.set_attribute("substep.name", "data_validation")
                grandchild_span.set_attribute("substep.type", "validation")
                print("    ✓ Grandchild span: substep_1a (validation)")
                time.sleep(0.03)

        # Create another child span
        with prod_tracer.start_span("step_2") as child_span2:
            child_span2.set_attribute("step.name", "data_processing")
            child_span2.set_attribute("step.order", 2)
            print("  ✓ Child span: step_2 (data_processing)")
            time.sleep(0.05)

    print("✓ Parent-child span hierarchy completed")

    # ========================================================================
    # 5. SPAN ENRICHMENT PATTERNS
    # ========================================================================
    print("\n5. Advanced Span Enrichment")
    print("-" * 28)

    # PRIMARY PATTERN (v1.0+): Instance method enrichment
    print("  📝 Instance Method Pattern (v1.0+ Primary)...")
    
    @trace(tracer=prod_tracer, event_type=EventType.tool)
    def complex_operation(data):
        """Operation with comprehensive span enrichment."""
        result = f"Processed: {data}"
        
        # ✅ PRIMARY PATTERN: Use instance method
        prod_tracer.enrich_span(
            metadata={
                "operation": "complex_processing",
                "data_type": type(data).__name__,
                "result": result
            },
            metrics={
                "processing_time_ms": 150,
                "performance_score": 0.95
            }
        )
        
        return result
    
    result = complex_operation({"key": "value"})
    print(f"  ✓ Instance method enrichment completed: {result}")

    # LEGACY PATTERN: Context manager (still works but deprecated)
    print("\n  📝 Context Manager Pattern (Legacy)...")
    with prod_tracer.start_span("enriched_operation") as span:
        print("  ✓ Base span created: enriched_operation")

        # ⚠️ LEGACY: Free function with context manager (backward compatibility)
        with enrich_span(
            event_type=EventType.tool,
            event_name="context_enrichment",
            inputs={"source": "advanced_demo", "operation": "enrichment"},
            metadata={"enrichment_type": "context_manager", "level": "advanced"},
            metrics={"enrichment_count": 10, "performance_score": 0.95},
            feedback={"quality": "excellent", "completeness": "full"},
        ):
            print("  ✓ Span enriched with comprehensive attributes (legacy pattern)")
            time.sleep(0.1)
            print("  ✓ Enrichment context manager completed")

    print("✓ Advanced span enrichment patterns demonstrated")

    # ========================================================================
    # 6. ERROR HANDLING IN SPANS
    # ========================================================================
    print("\n6. Error Handling in Spans")
    print("-" * 27)

    # Demonstrate proper error handling in spans
    @trace(tracer=dev_tracer, event_type=EventType.tool, event_name="error_handling")
    def function_with_error(should_fail: bool = False):
        """Function that demonstrates error handling in spans."""
        if should_fail:
            raise ValueError("Intentional error for demonstration")
        return "Success!"

    # Test successful execution
    try:
        result = function_with_error(should_fail=False)
        print(f"✓ Success case: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test error handling
    try:
        result = function_with_error(should_fail=True)
        print(f"✓ This shouldn't print: {result}")
    except ValueError as e:
        print(f"✓ Error properly handled and traced: {e}")

    # ========================================================================
    # 7. PERFORMANCE MONITORING
    # ========================================================================
    print("\n7. Performance Monitoring")
    print("-" * 26)

    # Create multiple spans to demonstrate performance patterns
    start_time = time.time()

    for i in range(3):
        with dev_tracer.start_span(f"performance_test_{i}") as span:
            span.set_attribute("iteration", i)
            span.set_attribute("batch_id", "performance_demo")
            span.set_attribute("start_time", time.time())

            # Simulate varying workloads
            work_time = 0.02 * (i + 1)  # Increasing work time
            time.sleep(work_time)

            span.set_attribute("work_duration", work_time)
            span.set_attribute("end_time", time.time())

    total_time = time.time() - start_time
    print(f"✓ Created 3 performance monitoring spans in {total_time:.3f}s")
    print("✓ Each span includes timing and performance metrics")

    print("\n🎉 Advanced usage example completed successfully!")
    print("\nAdvanced patterns demonstrated:")
    print("✅ Multiple tracer instances for different environments")
    print("✅ @trace_class decorator for automatic method tracing")
    print("✅ Parent-child span relationships")
    print("✅ Span enrichment with instance methods (v1.0+ primary pattern)")
    print("✅ Legacy context manager enrichment pattern (backward compatibility)")
    print("✅ Proper error handling in traced functions")
    print("✅ Performance monitoring patterns")
    print("✅ Complex multi-step workflows")
    print(
        "\nThese patterns enable sophisticated observability in production applications!"
    )


if __name__ == "__main__":
    main()
