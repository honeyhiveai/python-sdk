"""
Tracing Integration Tests

Tests core tracing functionality with real API calls.
Based on examples/basic_usage.py and examples/tracing_decorators.py.

Requirements:
    pip install honeyhive

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
"""

import os
import asyncio
import pytest
from typing import Any, Dict


# Skip entire module if key not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.slow,
]


class TestTracerInitialization:
    """Test tracer initialization patterns."""

    def test_basic_init(self):
        """Test basic tracer initialization."""
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_basic_init",
            source="pytest",
        )

        assert tracer is not None
        assert tracer.session_id is not None
        assert tracer.project_name == os.getenv("HH_PROJECT", "tracing-integration-test")

        tracer.flush()

    def test_init_with_config_object(self):
        """Test tracer initialization with TracerConfig object."""
        from honeyhive import HoneyHiveTracer
        from honeyhive.config.models import TracerConfig

        config = TracerConfig(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            source="pytest-config",
        )
        tracer = HoneyHiveTracer(config=config)

        assert tracer is not None
        assert tracer.session_id is not None

        tracer.flush()

    def test_multiple_tracers(self):
        """Test multiple tracer instances can coexist."""
        from honeyhive import HoneyHiveTracer

        tracer1 = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_multiple_tracers_1",
            source="pytest",
        )

        tracer2 = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_multiple_tracers_2",
            source="pytest",
        )

        assert tracer1.session_id != tracer2.session_id

        tracer1.flush()
        tracer2.flush()


class TestTraceDecorator:
    """Test @trace decorator functionality."""

    def test_trace_sync_function(self):
        """Test @trace on synchronous function."""
        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_trace_sync_function",
            source="pytest",
        )

        @trace
        def sync_function(x: int, y: int) -> int:
            return x + y

        result = sync_function(2, 3)
        assert result == 5

        tracer.flush()

    def test_trace_async_function(self):
        """Test @trace on async function."""
        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_trace_async_function",
            source="pytest",
        )

        @trace
        async def async_function(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        result = asyncio.run(async_function(5))
        assert result == 10

        tracer.flush()

    def test_trace_with_event_type(self):
        """Test @trace with event_type parameter."""
        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_trace_with_event_type",
            source="pytest",
        )

        @trace(event_type="tool")
        def tool_function(data: str) -> Dict[str, Any]:
            return {"processed": data.upper()}

        @trace(event_type="chain")
        def chain_function(items: list) -> list:
            return [item * 2 for item in items]

        @trace(event_type="model")
        def model_function(prompt: str) -> str:
            return f"Response to: {prompt}"

        result1 = tool_function("test")
        result2 = chain_function([1, 2, 3])
        result3 = model_function("hello")

        assert result1 == {"processed": "TEST"}
        assert result2 == [2, 4, 6]
        assert "hello" in result3

        tracer.flush()

    def test_nested_traces(self):
        """Test nested @trace decorators."""
        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_nested_traces",
            source="pytest",
        )

        @trace(event_type="chain")
        def outer_function(x: int) -> int:
            return middle_function(x)

        @trace(event_type="tool")
        def middle_function(x: int) -> int:
            return inner_function(x) + 1

        @trace
        def inner_function(x: int) -> int:
            return x * 2

        result = outer_function(5)
        assert result == 11  # (5 * 2) + 1

        tracer.flush()


class TestEnrichment:
    """Test span and session enrichment."""

    def test_enrich_span(self):
        """Test enrich_span functionality."""
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_enrich_span",
            source="pytest",
        )

        @trace
        def function_with_enrichment(data: str) -> str:
            enrich_span(metadata={"input_length": len(data)})
            result = data.upper()
            enrich_span(
                metadata={"output_length": len(result)},
                metrics={"processing_score": 0.95},
            )
            return result

        result = function_with_enrichment("hello world")
        assert result == "HELLO WORLD"

        tracer.flush()

    def test_enrich_session(self):
        """Test enrich_session functionality."""
        from honeyhive import HoneyHiveTracer, enrich_session

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_enrich_session",
            source="pytest",
        )

        # Enrich session with metadata
        enrich_session(metadata={"user_id": "test-user-123", "environment": "test"})

        # Enrich with feedback
        enrich_session(feedback={"rating": 5, "comment": "Test session"})

        # Enrich with metrics
        enrich_session(metrics={"total_operations": 10})

        tracer.flush()

    def test_combined_enrichment(self):
        """Test combined span and session enrichment."""
        from honeyhive import HoneyHiveTracer, trace, enrich_span, enrich_session

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_combined_enrichment",
            source="pytest",
        )

        # Session-level enrichment
        enrich_session(metadata={"workflow": "combined_test"})

        @trace(event_type="chain")
        def workflow(data: Dict[str, Any]) -> Dict[str, Any]:
            enrich_span(metadata={"step": "processing"})

            result = step1(data)
            result = step2(result)

            enrich_span(metrics={"steps_completed": 2})
            return result

        @trace(event_type="tool")
        def step1(data: Dict[str, Any]) -> Dict[str, Any]:
            enrich_span(metadata={"step_name": "step1"})
            return {**data, "step1": True}

        @trace(event_type="tool")
        def step2(data: Dict[str, Any]) -> Dict[str, Any]:
            enrich_span(metadata={"step_name": "step2"})
            return {**data, "step2": True}

        result = workflow({"initial": True})
        assert result["step1"] is True
        assert result["step2"] is True

        # Session-level feedback
        enrich_session(feedback={"completed": True})

        tracer.flush()


class TestDistributedTracing:
    """Test distributed tracing with session_id propagation."""

    def test_session_id_propagation(self):
        """Test that session_id can be propagated to child tracers."""
        from honeyhive import HoneyHiveTracer, trace

        # Parent tracer (Service A)
        parent_tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_distributed_parent",
            source="pytest-parent",
        )

        parent_session_id = parent_tracer.session_id

        # Child tracer (Service B) - would normally be in different process
        child_tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_distributed_child",
            session_id=parent_session_id,  # Propagate session ID
            source="pytest-child",
        )

        assert child_tracer.session_id == parent_session_id

        @trace
        def child_operation(data: str) -> str:
            return f"child processed: {data}"

        result = child_operation("test")
        assert "child processed" in result

        parent_tracer.flush()
        child_tracer.flush()
