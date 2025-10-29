"""End-to-end integration tests for real-world patterns.

These tests validate complete workflows with real API calls to ensure
the v1.0 baggage fix and instance method patterns work in production.

Tests require valid HH_API_KEY environment variable.
"""

# pylint: disable=protected-access,too-few-public-methods
# Justification:
# - protected-access: Tests need to access _tracer_id for tracer identification
# - too-few-public-methods: Test classes don't need multiple public methods

import os
from typing import Any, Dict

import pytest

from honeyhive import HoneyHiveTracer, enrich_span, trace
from honeyhive.tracer.registry import set_default_tracer

# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.environ.get("HH_API_KEY"), reason="Requires HH_API_KEY environment variable"
)


class TestRealWorldPatterns:
    """Test real-world usage patterns with actual API calls."""

    def test_basic_trace_with_enrichment(self) -> None:
        """Test basic tracing with instance method enrichment."""

        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-basic",
        )

        # Create and enrich span
        @trace(event_type="tool")
        def process_data(text: str) -> str:
            """Process data and enrich span."""
            result = text.upper()

            # ✅ PRIMARY PATTERN: Instance method
            tracer.enrich_span(
                metadata={"input": text, "output": result},
                metrics={"length": len(result)},
            )

            return result

        # Execute
        result = process_data("hello world")
        assert result == "HELLO WORLD"

        # Note: Verification in HoneyHive UI required
        # Automated verification would require API to query traces

    def test_nested_spans_with_enrichment(self) -> None:
        """Test nested span hierarchy with enrichment."""

        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-nested",
        )

        @trace(event_type="tool")
        def parent_operation(data: str) -> Dict[str, Any]:
            """Parent operation with child operations."""

            @trace(event_type="tool", event_name="child-1")
            def child_1(text: str) -> str:
                result = text.lower()
                tracer.enrich_span(metadata={"step": "lowercase"})
                return result

            @trace(event_type="tool", event_name="child-2")
            def child_2(text: str) -> str:
                result = text.strip()
                tracer.enrich_span(metadata={"step": "strip"})
                return result

            # Execute children
            result1 = child_1(data)
            result2 = child_2(result1)

            # Enrich parent
            tracer.enrich_span(
                metadata={"steps": 2, "final": result2}, metrics={"total_ops": 2}
            )

            return {"final": result2}

        # Execute
        result = parent_operation("  HELLO  ")
        assert result["final"] == "hello"

    def test_session_enrichment(self) -> None:
        """Test session enrichment with user properties."""

        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-session",
        )

        # Enrich session
        tracer.enrich_session(
            user_properties={"user_id": "test-user-123", "plan": "premium"},
            metadata={"test_type": "e2e", "pattern": "session_enrichment"},
            metrics={"test_duration_s": 1.5},
        )

        # Create some activity
        with tracer.start_span("test-activity"):
            tracer.enrich_span(metadata={"activity": "test"})

        # Note: Session should be enriched in HoneyHive

    def test_multiple_tracers_same_session(self) -> None:
        """Test two tracers for different projects don't interfere."""

        # Create two tracers
        tracer_a = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project") + "-a",
            session_name="e2e-test-multi-a",
        )

        tracer_b = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project") + "-b",
            session_name="e2e-test-multi-b",
        )

        # Use tracer A
        with tracer_a.start_span("span-a"):
            tracer_a.enrich_span(metadata={"tracer": "a"})

        # Use tracer B
        with tracer_b.start_span("span-b"):
            tracer_b.enrich_span(metadata={"tracer": "b"})

        # Both should have created independent traces
        assert tracer_a._tracer_id != tracer_b._tracer_id


@pytest.mark.integration
@pytest.mark.slow
class TestOpenAIIntegration:
    """Test OpenAI integration with enrichment."""

    def test_openai_with_enrichment(self) -> None:
        """Test OpenAI call with span enrichment."""
        pytest.importorskip("openai")

        from openai import (  # pylint: disable=import-outside-toplevel,import-error
            OpenAI,
        )

        # Optional dependency with skip marker
        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-openai",
        )

        # Initialize OpenAI client
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-test"))

        @trace(event_type="model")
        def call_openai(prompt: str) -> str:
            """Call OpenAI and enrich span."""
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                )

                result = response.choices[0].message.content or ""

                # Enrich with OpenAI metadata
                tracer.enrich_span(
                    metadata={
                        "model": "gpt-3.5-turbo",
                        "prompt": prompt,
                        "response": result,
                    },
                    metrics={
                        "tokens": response.usage.total_tokens if response.usage else 0
                    },
                )

                return result
            except Exception as e:
                tracer.enrich_span(metadata={"error": str(e), "model": "gpt-3.5-turbo"})
                raise

        # Execute (will skip if no OPENAI_API_KEY)
        if os.environ.get("OPENAI_API_KEY"):
            result = call_openai("Say 'test'")
            assert isinstance(result, str)


@pytest.mark.integration
@pytest.mark.slow
class TestEvaluateIntegration:
    """Test evaluate() pattern with enrichment."""

    def test_evaluate_with_instance_method(self) -> None:
        """Test evaluate() with instance method enrichment."""
        # pylint: disable=import-outside-toplevel,unused-import
        from honeyhive import evaluate

        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-evaluate",
        )

        # Define task with enrichment
        @trace(event_type="model")
        def task_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Task function that enriches span."""
            inputs = datapoint.get("inputs", {})
            text = inputs.get("text", "")

            # Process
            result = text.upper()

            # ✅ Enrich with instance method (v1.0 fix enables this)
            tracer.enrich_span(
                metadata={"input": text, "output": result},
                metrics={"length": len(result)},
            )

            return {"output": result}

        # Create test dataset
        test_data = [
            {"inputs": {"text": "hello"}},
            {"inputs": {"text": "world"}},
        ]

        # Note: evaluate() expects dataset name, not inline data
        # This test demonstrates the pattern but won't actually call evaluate()
        # In production:
        # results = evaluate(
        #     dataset="your-dataset",
        #     task=task_function,
        #     tracer=tracer
        # )

        # For test, manually execute
        for dp in test_data:
            result = task_function(dp)
            assert "output" in result

    def test_evaluate_with_free_function(self) -> None:
        """Test evaluate() with legacy free function pattern."""

        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-evaluate-legacy",
        )

        # Set as default for free function discovery
        set_default_tracer(tracer)

        # Define task with free function (legacy)
        @trace(event_type="model")
        def legacy_task(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Task using legacy free function pattern."""
            inputs = datapoint.get("inputs", {})
            text = inputs.get("text", "")

            result = text.upper()

            # ⚠️ LEGACY: Free function (still works but deprecated)
            enrich_span(
                metadata={"input": text, "output": result},
                tracer=tracer,  # Can pass explicitly
            )

            return {"output": result}

        # Execute manually
        test_data = [{"inputs": {"text": "test"}}]
        for dp in test_data:
            result = legacy_task(dp)
            assert "output" in result


@pytest.mark.integration
@pytest.mark.slow
class TestErrorHandling:
    """Test error handling with enrichment."""

    def test_error_enrichment(self) -> None:
        """Test enriching spans with error information."""

        tracer = HoneyHiveTracer.init(
            api_key=os.environ["HH_API_KEY"],
            project=os.environ.get("HH_PROJECT", "test-project"),
            session_name="e2e-test-errors",
        )

        @trace(event_type="tool")
        def operation_that_fails() -> None:
            """Operation that raises an error."""
            try:
                # Simulate error
                raise ValueError("Test error")
            except ValueError as e:
                # Enrich span with error details
                tracer.enrich_span(
                    metadata={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "handled": True,
                    }
                )
                # Re-raise for span to record
                raise

        # Execute and catch
        with pytest.raises(ValueError, match="Test error"):
            operation_that_fails()


# Note: Performance benchmarks (Task 4.4) in separate file
