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

        session_id = tracer.session_id

        # Enrich session with metadata
        enrich_session(session_id, metadata={"user_id": "test-user-123", "environment": "test"})

        # Enrich with feedback (using tracer instance method)
        tracer.enrich_session(feedback={"rating": 5, "comment": "Test session"})

        # Enrich with metrics
        tracer.enrich_session(metrics={"total_operations": 10})

        tracer.flush()

    def test_combined_enrichment(self):
        """Test combined span and session enrichment."""
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_combined_enrichment",
            source="pytest",
        )

        # Session-level enrichment (using instance method)
        tracer.enrich_session(metadata={"workflow": "combined_test"})

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

        # Session-level feedback (using instance method)
        tracer.enrich_session(feedback={"completed": True})

        tracer.flush()


class TestUserFeedback:
    """Test user feedback functionality (per /tracing/setting-user-feedback.mdx)."""

    def test_session_feedback_boolean_rating(self):
        """Test boolean rating (thumbs up/down) on session."""
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_session_feedback_boolean",
            source="pytest",
        )

        # Thumbs up
        tracer.enrich_session(feedback={
            "rating": True,
            "comment": "The response was helpful",
        })

        tracer.flush()

    def test_session_feedback_numeric_rating(self):
        """Test numeric rating (1-5 scale) on session."""
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_session_feedback_numeric",
            source="pytest",
        )

        # 5-star rating
        tracer.enrich_session(feedback={
            "rating": 5,
            "comment": "Excellent response!",
        })

        tracer.flush()

    def test_session_feedback_with_ground_truth(self):
        """Test feedback with ground truth for evaluation."""
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_session_feedback_ground_truth",
            source="pytest",
        )

        tracer.enrich_session(feedback={
            "rating": True,
            "ground_truth": "The capital of France is Paris.",
        })

        tracer.flush()

    def test_span_feedback(self):
        """Test feedback on specific span."""
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_span_feedback",
            source="pytest",
        )

        @trace
        def generate_response(query: str) -> str:
            result = f"Response to: {query}"
            # Add feedback to this specific span
            enrich_span(feedback={
                "rating": True,
                "comment": "Good response quality",
            })
            return result

        result = generate_response("What is Python?")
        assert "Response to" in result

        tracer.flush()


class TestUserProperties:
    """Test user properties functionality (per /tracing/setting-user-properties.mdx)."""

    def test_session_user_properties(self):
        """Test adding user properties to session."""
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_session_user_properties",
            source="pytest",
        )

        tracer.enrich_session(user_properties={
            "user_id": "user_12345",
            "email": "test@example.com",
            "plan": "premium",
            "is_beta": True,
        })

        tracer.flush()

    def test_span_user_properties(self):
        """Test adding user properties to specific span."""
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_span_user_properties",
            source="pytest",
        )

        @trace
        def process_request(query: str, user_id: str) -> str:
            # Add user context to this span
            enrich_span(user_properties={
                "user_id": user_id,
                "request_type": "query",
            })
            return f"Processed for {user_id}: {query}"

        result = process_request("Hello", "user_456")
        assert "user_456" in result

        tracer.flush()

    def test_combined_user_context(self):
        """Test combining user properties with other enrichments."""
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_combined_user_context",
            source="pytest",
        )

        # Session-level user context
        tracer.enrich_session(
            user_properties={"user_id": "user_789", "plan": "enterprise"},
            metadata={"session_type": "api_request"},
        )

        @trace
        def handle_request(data: str) -> str:
            enrich_span(
                user_properties={"request_source": "api"},
                metadata={"input_size": len(data)},
                metrics={"latency_ms": 50},
            )
            return data.upper()

        result = handle_request("test data")
        assert result == "TEST DATA"

        # Session feedback after processing
        tracer.enrich_session(feedback={"rating": True})

        tracer.flush()


class TestDistributedTracing:
    """Test distributed tracing with session_id propagation."""

    def test_session_id_retrieval(self):
        """Test that session_id can be retrieved from tracer."""
        from honeyhive import HoneyHiveTracer, trace

        # Create tracer
        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_session_id_retrieval",
            source="pytest",
        )

        # Session ID should be available
        session_id = tracer.session_id
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0

        # Session ID should be a valid UUID format
        import uuid
        try:
            uuid.UUID(session_id)
        except ValueError:
            pytest.fail(f"session_id is not a valid UUID: {session_id}")

        @trace
        def traced_operation(data: str) -> str:
            return f"processed: {data}"

        result = traced_operation("test")
        assert "processed" in result

        tracer.flush()

    def test_multiple_sessions(self):
        """Test that multiple tracers have different session IDs."""
        from honeyhive import HoneyHiveTracer

        tracer1 = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_multi_session_1",
            source="pytest",
        )

        tracer2 = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "tracing-integration-test"),
            session_name="test_multi_session_2",
            source="pytest",
        )

        # Different tracers should have different session IDs
        assert tracer1.session_id != tracer2.session_id

        tracer1.flush()
        tracer2.flush()
