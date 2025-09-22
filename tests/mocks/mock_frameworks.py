"""
Mock frameworks for testing multi-framework integration scenarios.

These mock frameworks simulate different patterns of OpenTelemetry usage
that real AI frameworks might employ.
"""

import threading
import time
from typing import Any, Dict, List

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


class MockFrameworkA:
    """
    Mock framework that uses OpenTelemetry directly with TracerProvider.

    Simulates a framework that sets up its own TracerProvider and expects
    to maintain control over tracing configuration.
    """

    def __init__(self, name: str = "MockFrameworkA"):
        self.name = name
        self.provider = TracerProvider()
        trace.set_tracer_provider(self.provider)
        self.tracer = trace.get_tracer(f"{name}.tracer")
        self._operations: List[Dict[str, Any]] = []

    def execute_operation(self, operation_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a traced operation."""
        with self.tracer.start_as_current_span(f"{self.name}.{operation_name}") as span:
            span.set_attribute("framework.name", self.name)
            span.set_attribute("framework.type", "MockFrameworkA")
            span.set_attribute("operation.name", operation_name)

            # Add custom attributes
            for key, value in kwargs.items():
                span.set_attribute(f"operation.{key}", str(value))

            # Simulate work
            time.sleep(0.01)

            result = {
                "operation": operation_name,
                "framework": self.name,
                "status": "completed",
                "span_id": format(span.get_span_context().span_id, "016x"),
                "trace_id": format(span.get_span_context().trace_id, "032x"),
                **kwargs,
            }

            span.set_attribute("operation.result", "success")
            self._operations.append(result)

            return result

    def get_operations(self) -> List[Dict[str, Any]]:
        """Get list of executed operations."""
        return self._operations.copy()

    def reset(self) -> None:
        """Reset operation history."""
        self._operations.clear()


class MockFrameworkB:
    """
    Mock framework that uses OpenTelemetry with ProxyTracerProvider initially.

    Simulates a framework that might start with a ProxyTracerProvider
    and later replace it with a real provider.
    """

    def __init__(self, name: str = "MockFrameworkB", delay_provider_setup: bool = True):
        self.name = name
        self.delay_provider_setup = delay_provider_setup
        self._operations: List[Dict[str, Any]] = []

        if not delay_provider_setup:
            self._setup_provider()
        else:
            # Start with whatever provider is currently set
            self.tracer = trace.get_tracer(f"{name}.tracer")

    def _setup_provider(self) -> None:
        """Set up the real TracerProvider."""
        self.provider = TracerProvider()
        trace.set_tracer_provider(self.provider)
        self.tracer = trace.get_tracer(f"{self.name}.tracer")

    def initialize(self) -> None:
        """Initialize the framework (potentially setting up provider)."""
        if self.delay_provider_setup:
            self._setup_provider()

    def process_data(
        self, data: str, processing_type: str = "standard"
    ) -> Dict[str, Any]:
        """Process data with tracing."""
        with self.tracer.start_as_current_span(f"{self.name}.process_data") as span:
            span.set_attribute("framework.name", self.name)
            span.set_attribute("framework.type", "MockFrameworkB")
            span.set_attribute("data.type", processing_type)
            span.set_attribute("data.length", len(data))

            # Simulate nested operation
            with self.tracer.start_as_current_span("data_validation") as nested_span:
                nested_span.set_attribute("validation.type", "format_check")
                time.sleep(0.005)
                is_valid = len(data) > 0
                nested_span.set_attribute("validation.result", is_valid)

            # Main processing
            time.sleep(0.01)
            processed_data = f"processed_{processing_type}_{data}"

            result = {
                "original_data": data,
                "processed_data": processed_data,
                "processing_type": processing_type,
                "framework": self.name,
                "span_id": format(span.get_span_context().span_id, "016x"),
                "trace_id": format(span.get_span_context().trace_id, "032x"),
                "status": "completed",
            }

            span.set_attribute("processing.result", "success")
            self._operations.append(result)

            return result

    def get_operations(self) -> List[Dict[str, Any]]:
        """Get list of executed operations."""
        return self._operations.copy()

    def reset(self) -> None:
        """Reset operation history."""
        self._operations.clear()


class MockFrameworkC:
    """
    Mock framework that uses OpenTelemetry with custom span attributes.

    Simulates a framework that adds framework-specific attributes
    and expects them to be preserved alongside HoneyHive attributes.
    """

    def __init__(self, name: str = "MockFrameworkC"):
        self.name = name
        self.tracer = trace.get_tracer(f"{name}.tracer")
        self._operations: List[Dict[str, Any]] = []
        self._custom_attributes = {
            f"{name.lower()}.version": "1.0.0",
            f"{name.lower()}.mode": "production",
            f"{name.lower()}.feature_flags": "advanced_tracing,custom_metrics",
        }

    def analyze_content(
        self, content: str, analysis_type: str = "sentiment"
    ) -> Dict[str, Any]:
        """Analyze content with custom tracing attributes."""
        with self.tracer.start_as_current_span(f"{self.name}.analyze_content") as span:
            # Framework identification
            span.set_attribute("framework.name", self.name)
            span.set_attribute("framework.type", "MockFrameworkC")

            # Add custom framework attributes
            for key, value in self._custom_attributes.items():
                span.set_attribute(key, value)

            # Analysis-specific attributes
            span.set_attribute("analysis.type", analysis_type)
            span.set_attribute("content.length", len(content))
            span.set_attribute("content.word_count", len(content.split()))

            # Simulate analysis steps
            steps = [
                "preprocessing",
                "feature_extraction",
                "analysis",
                "post_processing",
            ]
            results = {}

            for step in steps:
                with self.tracer.start_as_current_span(f"analysis_{step}") as step_span:
                    step_span.set_attribute("step.name", step)
                    step_span.set_attribute("step.order", steps.index(step) + 1)
                    time.sleep(0.003)

                    step_result = f"{step}_result_for_{analysis_type}"
                    results[step] = step_result
                    step_span.set_attribute("step.result", step_result)

            # Final result
            final_result = {
                "content": content,
                "analysis_type": analysis_type,
                "results": results,
                "framework": self.name,
                "span_id": format(span.get_span_context().span_id, "016x"),
                "trace_id": format(span.get_span_context().trace_id, "032x"),
                "confidence": 0.95,
                "status": "completed",
            }

            span.set_attribute("analysis.confidence", 0.95)
            span.set_attribute("analysis.status", "completed")
            self._operations.append(final_result)

            return final_result

    def get_operations(self) -> List[Dict[str, Any]]:
        """Get list of executed operations."""
        return self._operations.copy()

    def reset(self) -> None:
        """Reset operation history."""
        self._operations.clear()


class ConcurrentFrameworkManager:
    """
    Manager for testing concurrent framework operations.

    Simulates scenarios where multiple frameworks are running
    operations simultaneously.
    """

    def __init__(self) -> None:
        self.frameworks: Dict[str, Any] = {}
        self.results: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add_framework(self, name: str, framework: Any) -> None:
        """Add a framework to the manager."""
        self.frameworks[name] = framework

    def run_concurrent_operations(
        self, operations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run operations concurrently across frameworks.

        Args:
            operations: List of operation specs with format:
                {
                    "framework": "framework_name",
                    "method": "method_name",
                    "args": [...],
                    "kwargs": {...}
                }
        """
        threads = []

        def execute_operation(op_spec: Dict[str, Any]) -> None:
            try:
                framework = self.frameworks[op_spec["framework"]]
                method = getattr(framework, op_spec["method"])
                args = op_spec.get("args", [])
                kwargs = op_spec.get("kwargs", {})

                result = method(*args, **kwargs)

                with self._lock:
                    self.results.append(
                        {
                            "framework": op_spec["framework"],
                            "method": op_spec["method"],
                            "result": result,
                            "thread_id": threading.get_ident(),
                            "success": True,
                        }
                    )
            except Exception as e:
                with self._lock:
                    self.results.append(
                        {
                            "framework": op_spec.get("framework", "unknown"),
                            "method": op_spec.get("method", "unknown"),
                            "error": str(e),
                            "thread_id": threading.get_ident(),
                            "success": False,
                        }
                    )

        # Start all operations concurrently
        for op_spec in operations:
            thread = threading.Thread(target=execute_operation, args=(op_spec,))
            threads.append(thread)
            thread.start()

        # Wait for all operations to complete
        for thread in threads:
            thread.join()

        return self.results.copy()

    def get_all_framework_operations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get operations from all frameworks."""
        all_operations = {}
        for name, framework in self.frameworks.items():
            if hasattr(framework, "get_operations"):
                all_operations[name] = framework.get_operations()
        return all_operations

    def reset_all(self) -> None:
        """Reset all frameworks and results."""
        self.results.clear()
        for framework in self.frameworks.values():
            if hasattr(framework, "reset"):
                framework.reset()
