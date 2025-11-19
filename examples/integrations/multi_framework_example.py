"""
Multi-Framework Integration Example

This example demonstrates how to integrate HoneyHive with multiple
non-instrumentor frameworks simultaneously, showing how they can
coexist and share tracing context.
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional
from opentelemetry import trace
from honeyhive import HoneyHiveTracer

# Import mock frameworks for demonstration
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "tests"))

try:
    from tests.mocks.mock_frameworks import (
        MockFrameworkA,
        MockFrameworkB,
        MockFrameworkC,
    )

    MOCK_FRAMEWORKS_AVAILABLE = True
except ImportError:
    MOCK_FRAMEWORKS_AVAILABLE = False
    print("⚠️  Mock frameworks not available. Run from project root.")


class WorkflowOrchestrator:
    """
    Orchestrates operations across multiple frameworks.

    This demonstrates how to coordinate multiple AI frameworks
    within a single tracing session.
    """

    def __init__(self, frameworks: Dict[str, Any]):
        self.frameworks = frameworks
        self.tracer = trace.get_tracer("workflow-orchestrator")
        self.results: List[Dict[str, Any]] = []

    def execute_sequential_workflow(self, input_data: str) -> Dict[str, Any]:
        """Execute a sequential workflow across multiple frameworks."""
        with self.tracer.start_as_current_span("sequential-workflow") as workflow_span:
            workflow_span.set_attribute("workflow.type", "sequential")
            workflow_span.set_attribute("workflow.frameworks", len(self.frameworks))
            workflow_span.set_attribute("workflow.input_length", len(input_data))

            current_data = input_data
            step_results = []

            # Step 1: Framework A - Initial processing
            if "framework_a" in self.frameworks:
                with self.tracer.start_as_current_span(
                    "step-1-framework-a"
                ) as step_span:
                    step_span.set_attribute("step.number", 1)
                    step_span.set_attribute("step.framework", "framework_a")

                    result_a = self.frameworks["framework_a"].execute_operation(
                        "sequential_step_1",
                        input_data=current_data,
                        step="initial_processing",
                    )

                    step_results.append(result_a)
                    current_data = (
                        f"processed_by_a_{result_a.get('operation', 'unknown')}"
                    )
                    step_span.set_attribute("step.result", "success")

            # Step 2: Framework B - Secondary processing
            if "framework_b" in self.frameworks:
                with self.tracer.start_as_current_span(
                    "step-2-framework-b"
                ) as step_span:
                    step_span.set_attribute("step.number", 2)
                    step_span.set_attribute("step.framework", "framework_b")

                    result_b = self.frameworks["framework_b"].process_data(
                        current_data, "sequential_processing"
                    )

                    step_results.append(result_b)
                    current_data = result_b.get("processed_data", current_data)
                    step_span.set_attribute("step.result", "success")

            # Step 3: Framework C - Final analysis
            if "framework_c" in self.frameworks:
                with self.tracer.start_as_current_span(
                    "step-3-framework-c"
                ) as step_span:
                    step_span.set_attribute("step.number", 3)
                    step_span.set_attribute("step.framework", "framework_c")

                    result_c = self.frameworks["framework_c"].analyze_content(
                        current_data, "sequential_analysis"
                    )

                    step_results.append(result_c)
                    step_span.set_attribute("step.result", "success")

            # Compile final result
            final_result = {
                "workflow_type": "sequential",
                "input_data": input_data,
                "final_data": current_data,
                "steps_completed": len(step_results),
                "step_results": step_results,
                "timestamp": time.time(),
                "status": "completed",
            }

            workflow_span.set_attribute("workflow.steps_completed", len(step_results))
            workflow_span.set_attribute("workflow.status", "completed")

            self.results.append(final_result)
            return final_result

    def execute_parallel_workflow(self, input_data: List[str]) -> Dict[str, Any]:
        """Execute a parallel workflow across multiple frameworks."""
        with self.tracer.start_as_current_span("parallel-workflow") as workflow_span:
            workflow_span.set_attribute("workflow.type", "parallel")
            workflow_span.set_attribute("workflow.frameworks", len(self.frameworks))
            workflow_span.set_attribute("workflow.input_count", len(input_data))

            import concurrent.futures

            def process_with_framework(
                framework_name: str, framework: Any, data: str
            ) -> Dict[str, Any]:
                """Process data with a specific framework."""
                with self.tracer.start_as_current_span(
                    f"parallel-{framework_name}"
                ) as span:
                    span.set_attribute("parallel.framework", framework_name)
                    span.set_attribute("parallel.data_length", len(data))

                    if hasattr(framework, "execute_operation"):
                        result = framework.execute_operation(
                            f"parallel_op_{framework_name}",
                            input_data=data,
                            parallel=True,
                        )
                    elif hasattr(framework, "process_data"):
                        result = framework.process_data(data, "parallel_processing")
                    elif hasattr(framework, "analyze_content"):
                        result = framework.analyze_content(data, "parallel_analysis")
                    else:
                        result = {"error": "Unknown framework type"}

                    span.set_attribute(
                        "parallel.result",
                        "success" if "error" not in result else "error",
                    )
                    return {
                        "framework": framework_name,
                        "result": result,
                        "processing_time": time.time(),
                    }

            # Execute parallel processing
            parallel_results = []

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(self.frameworks)
            ) as executor:
                futures = []

                for i, (framework_name, framework) in enumerate(
                    self.frameworks.items()
                ):
                    data_item = input_data[
                        i % len(input_data)
                    ]  # Cycle through input data
                    future = executor.submit(
                        process_with_framework, framework_name, framework, data_item
                    )
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    parallel_results.append(result)

            # Compile final result
            final_result = {
                "workflow_type": "parallel",
                "input_data": input_data,
                "parallel_results": parallel_results,
                "frameworks_used": len(parallel_results),
                "timestamp": time.time(),
                "status": "completed",
            }

            workflow_span.set_attribute(
                "workflow.parallel_results", len(parallel_results)
            )
            workflow_span.set_attribute("workflow.status", "completed")

            self.results.append(final_result)
            return final_result

    def execute_hybrid_workflow(
        self, input_data: str, parallel_data: List[str]
    ) -> Dict[str, Any]:
        """Execute a hybrid workflow combining sequential and parallel processing."""
        with self.tracer.start_as_current_span("hybrid-workflow") as workflow_span:
            workflow_span.set_attribute("workflow.type", "hybrid")
            workflow_span.set_attribute("workflow.sequential_input", len(input_data))
            workflow_span.set_attribute("workflow.parallel_inputs", len(parallel_data))

            # Phase 1: Sequential preprocessing
            with self.tracer.start_as_current_span("phase-1-sequential") as phase1_span:
                sequential_result = self.execute_sequential_workflow(input_data)
                phase1_span.set_attribute("phase.result", "completed")

            # Phase 2: Parallel processing
            with self.tracer.start_as_current_span("phase-2-parallel") as phase2_span:
                parallel_result = self.execute_parallel_workflow(parallel_data)
                phase2_span.set_attribute("phase.result", "completed")

            # Phase 3: Final integration
            with self.tracer.start_as_current_span(
                "phase-3-integration"
            ) as phase3_span:
                integration_data = {
                    "sequential_output": sequential_result["final_data"],
                    "parallel_outputs": [
                        r["result"] for r in parallel_result["parallel_results"]
                    ],
                    "integration_timestamp": time.time(),
                }

                # Use first available framework for integration
                if self.frameworks:
                    framework_name, framework = next(iter(self.frameworks.items()))

                    if hasattr(framework, "execute_operation"):
                        integration_result = framework.execute_operation(
                            "hybrid_integration",
                            sequential_data=sequential_result["final_data"],
                            parallel_count=len(parallel_result["parallel_results"]),
                        )
                    else:
                        integration_result = {
                            "status": "integrated",
                            "method": "manual",
                        }

                    integration_data["integration_result"] = integration_result

                phase3_span.set_attribute("phase.result", "completed")

            # Compile final result
            final_result = {
                "workflow_type": "hybrid",
                "sequential_result": sequential_result,
                "parallel_result": parallel_result,
                "integration_data": integration_data,
                "timestamp": time.time(),
                "status": "completed",
            }

            workflow_span.set_attribute("workflow.status", "completed")

            self.results.append(final_result)
            return final_result

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of all executed workflows."""
        return {
            "total_workflows": len(self.results),
            "workflow_types": [r["workflow_type"] for r in self.results],
            "frameworks_available": list(self.frameworks.keys()),
            "execution_times": [r["timestamp"] for r in self.results],
        }


def demonstrate_basic_multi_framework():
    """Demonstrate basic multi-framework integration."""
    print("🚀 Basic Multi-Framework Integration")
    print("=" * 40)

    if not MOCK_FRAMEWORKS_AVAILABLE:
        print("❌ Mock frameworks not available")
        return

    # Initialize HoneyHive
    print("1. Initializing HoneyHive tracer...")
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "multi-framework-demo"),
        source="multi-framework-basic",
        test_mode=True,
        verbose=False,
    )
    print(f"   ✅ HoneyHive initialized (Session: {tracer.session_id})")

    # Initialize multiple frameworks
    print("2. Initializing multiple frameworks...")
    frameworks = {
        "framework_a": MockFrameworkA("MultiA"),
        "framework_b": MockFrameworkB("MultiB", delay_provider_setup=False),
        "framework_c": MockFrameworkC("MultiC"),
    }
    print(f"   ✅ {len(frameworks)} frameworks initialized")

    # Execute operations on each framework
    print("3. Executing operations on each framework...")

    results = {}
    for name, framework in frameworks.items():
        print(f"   Processing with {name}...")

        if hasattr(framework, "execute_operation"):
            result = framework.execute_operation(
                f"multi_test_{name}", framework_type=name
            )
        elif hasattr(framework, "process_data"):
            result = framework.process_data(f"multi_data_{name}", "multi_test")
        elif hasattr(framework, "analyze_content"):
            result = framework.analyze_content(
                f"multi content {name}", "multi_analysis"
            )

        results[name] = result
        print(f"     ✅ {name} completed: {result.get('status', 'unknown')}")

    print(f"   ✅ All {len(results)} frameworks completed successfully")
    print()


def demonstrate_workflow_orchestration():
    """Demonstrate advanced workflow orchestration."""
    print("🎯 Advanced Workflow Orchestration")
    print("=" * 38)

    if not MOCK_FRAMEWORKS_AVAILABLE:
        print("❌ Mock frameworks not available")
        return

    # Initialize HoneyHive
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "workflow-orchestration"),
        source="workflow-orchestrator",
        test_mode=True,
        verbose=False,
    )

    # Initialize frameworks
    frameworks = {
        "framework_a": MockFrameworkA("WorkflowA"),
        "framework_b": MockFrameworkB("WorkflowB", delay_provider_setup=False),
        "framework_c": MockFrameworkC("WorkflowC"),
    }

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(frameworks)

    print("1. Executing sequential workflow...")
    sequential_result = orchestrator.execute_sequential_workflow(
        "Initial data for sequential processing"
    )
    print(
        f"   ✅ Sequential workflow completed: {sequential_result['steps_completed']} steps"
    )

    print("2. Executing parallel workflow...")
    parallel_result = orchestrator.execute_parallel_workflow(
        ["Parallel data 1", "Parallel data 2", "Parallel data 3"]
    )
    print(
        f"   ✅ Parallel workflow completed: {parallel_result['frameworks_used']} frameworks"
    )

    print("3. Executing hybrid workflow...")
    hybrid_result = orchestrator.execute_hybrid_workflow(
        "Sequential input for hybrid workflow",
        ["Hybrid parallel 1", "Hybrid parallel 2"],
    )
    print(f"   ✅ Hybrid workflow completed")

    # Get summary
    summary = orchestrator.get_workflow_summary()
    print(f"4. Workflow summary:")
    print(f"   Total workflows executed: {summary['total_workflows']}")
    print(f"   Workflow types: {', '.join(set(summary['workflow_types']))}")
    print(f"   Frameworks used: {', '.join(summary['frameworks_available'])}")
    print()


def demonstrate_context_propagation():
    """Demonstrate context propagation across frameworks."""
    print("🔗 Context Propagation Across Frameworks")
    print("=" * 42)

    if not MOCK_FRAMEWORKS_AVAILABLE:
        print("❌ Mock frameworks not available")
        return

    # Initialize HoneyHive
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "context-propagation"),
        source="context-demo",
        test_mode=True,
        verbose=False,
    )

    # Initialize frameworks
    frameworks = {
        "framework_a": MockFrameworkA("ContextA"),
        "framework_b": MockFrameworkB("ContextB", delay_provider_setup=False),
        "framework_c": MockFrameworkC("ContextC"),
    }

    print("1. Creating parent context...")

    # Create parent context
    otel_tracer = trace.get_tracer("context-propagation-demo")

    with otel_tracer.start_as_current_span("user-request") as user_span:
        user_span.set_attribute("request.type", "multi-framework")
        user_span.set_attribute("request.id", "req-12345")
        user_span.set_attribute("user.id", "user-67890")

        print("2. Processing request through multiple frameworks...")

        # Framework A: Authentication/validation
        with otel_tracer.start_as_current_span("authentication") as auth_span:
            auth_span.set_attribute("auth.framework", "framework_a")
            result_a = frameworks["framework_a"].execute_operation(
                "authenticate_request", request_id="req-12345", user_id="user-67890"
            )
            auth_span.set_attribute("auth.result", result_a.get("status", "unknown"))
            print(f"   Authentication: {result_a.get('status', 'unknown')}")

        # Framework B: Business logic processing
        with otel_tracer.start_as_current_span("business-logic") as logic_span:
            logic_span.set_attribute("logic.framework", "framework_b")
            result_b = frameworks["framework_b"].process_data(
                "business_logic_data", "request_processing"
            )
            logic_span.set_attribute("logic.result", result_b.get("status", "unknown"))
            print(f"   Business Logic: {result_b.get('status', 'unknown')}")

        # Framework C: Response generation
        with otel_tracer.start_as_current_span("response-generation") as response_span:
            response_span.set_attribute("response.framework", "framework_c")
            result_c = frameworks["framework_c"].analyze_content(
                "Generate response for user request", "response_generation"
            )
            response_span.set_attribute(
                "response.result", result_c.get("status", "unknown")
            )
            print(f"   Response Generation: {result_c.get('status', 'unknown')}")

        # Set final request attributes
        user_span.set_attribute("request.status", "completed")
        user_span.set_attribute("request.frameworks_used", 3)

        print("   ✅ Request processed through all frameworks with shared context")

    print("3. ✅ Context propagation demonstration completed")
    print()


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring across multiple frameworks."""
    print("⚡ Multi-Framework Performance Monitoring")
    print("=" * 42)

    if not MOCK_FRAMEWORKS_AVAILABLE:
        print("❌ Mock frameworks not available")
        return

    # Initialize HoneyHive
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "performance-monitoring"),
        source="performance-demo",
        test_mode=True,
        verbose=False,
    )

    # Initialize frameworks
    frameworks = {
        "framework_a": MockFrameworkA("PerfA"),
        "framework_b": MockFrameworkB("PerfB", delay_provider_setup=False),
        "framework_c": MockFrameworkC("PerfC"),
    }

    print("1. Running performance benchmark...")

    # Performance test configuration
    operations_per_framework = 10
    total_operations = len(frameworks) * operations_per_framework

    start_time = time.perf_counter()

    # Execute operations on all frameworks
    all_results = []

    for framework_name, framework in frameworks.items():
        framework_start = time.perf_counter()

        for i in range(operations_per_framework):
            op_start = time.perf_counter()

            if hasattr(framework, "execute_operation"):
                result = framework.execute_operation(
                    f"perf_op_{i}", framework=framework_name
                )
            elif hasattr(framework, "process_data"):
                result = framework.process_data(f"perf_data_{i}", "performance")
            elif hasattr(framework, "analyze_content"):
                result = framework.analyze_content(f"perf content {i}", "performance")

            op_end = time.perf_counter()

            all_results.append(
                {
                    "framework": framework_name,
                    "operation": i,
                    "duration": op_end - op_start,
                    "result": result,
                }
            )

        framework_end = time.perf_counter()
        framework_duration = framework_end - framework_start

        print(
            f"   {framework_name}: {operations_per_framework} ops in {framework_duration:.3f}s "
            f"({operations_per_framework / framework_duration:.1f} ops/sec)"
        )

    end_time = time.perf_counter()
    total_duration = end_time - start_time

    # Calculate statistics
    durations = [r["duration"] for r in all_results]
    avg_duration = sum(durations) / len(durations)
    min_duration = min(durations)
    max_duration = max(durations)

    print("2. Performance Results:")
    print(f"   Total operations: {total_operations}")
    print(f"   Total time: {total_duration:.3f}s")
    print(f"   Overall throughput: {total_operations / total_duration:.1f} ops/sec")
    print(f"   Average operation time: {avg_duration:.4f}s")
    print(f"   Min operation time: {min_duration:.4f}s")
    print(f"   Max operation time: {max_duration:.4f}s")
    print("   ✅ Performance monitoring completed")
    print()


def main():
    """Run all multi-framework integration examples."""
    print("🎯 Multi-Framework Integration Examples")
    print("=" * 42)
    print()

    # Environment check
    if not os.getenv("HH_API_KEY"):
        print("⚠️  HH_API_KEY not set - using demo mode")
    if not os.getenv("HH_PROJECT"):
        print("⚠️  HH_PROJECT not set - using default project names")
    print()

    try:
        # Run all demonstrations
        demonstrate_basic_multi_framework()
        demonstrate_workflow_orchestration()
        demonstrate_context_propagation()
        demonstrate_performance_monitoring()

        print("🎉 All multi-framework integration examples completed successfully!")

    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
