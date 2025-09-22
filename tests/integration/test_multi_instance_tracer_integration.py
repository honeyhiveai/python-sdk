"""Integration tests for multi-instance tracer functionality in HoneyHive."""

# pylint: disable=duplicate-code  # Integration tests share common patterns

# Removed unused import: time
import asyncio
import threading
from typing import Any

import pytest

from honeyhive.tracer import HoneyHiveTracer, atrace, enrich_span, trace
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)


@pytest.mark.integration
@pytest.mark.multi_instance
class TestMultiInstanceTracerIntegration:
    """Test multi-instance tracer integration and end-to-end functionality."""

    def test_multiple_tracers_coexistence(
        self, tracer_factory: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test that multiple tracers can coexist and work independently
        with backend verification."""

        # Create multiple tracers using standardized factory
        tracer1 = tracer_factory("tracer1-session")
        tracer2 = tracer_factory("tracer2-session")

        # Verify they're independent instances
        assert tracer1 is not tracer2
        assert "tracer1-session" in tracer1.session_name
        assert "tracer2-session" in tracer2.session_name

        # Test both can create spans independently with backend verification
        _, unique_id1 = generate_test_id("coexistence_test", "tracer1")
        verified_event1 = verify_tracer_span(
            tracer=tracer1,
            client=integration_client,
            project=real_project,
            span_name="multi_tracer_span1",
            unique_identifier=unique_id1,
            span_attributes={
                "tracer": "tracer1",
                "test": "coexistence",
                "test.type": "multi_instance",
            },
        )

        _, unique_id2 = generate_test_id("coexistence_test", "tracer2")
        verified_event2 = verify_tracer_span(
            tracer=tracer2,
            client=integration_client,
            project=real_project,
            span_name="multi_tracer_span2",
            unique_identifier=unique_id2,
            span_attributes={
                "tracer": "tracer2",
                "test": "coexistence",
                "test.type": "multi_instance",
            },
        )

        # Verify both spans were exported to backend
        assert verified_event1.event_name == "multi_tracer_span1"
        assert verified_event2.event_name == "multi_tracer_span2"

        # Verify spans have different session contexts
        assert verified_event1.session_id != verified_event2.session_id

    def test_tracer_independence(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test that tracers are completely independent."""
        # Create tracers with different configurations using factory
        tracer1 = tracer_factory("independent-session-1")
        tracer2 = tracer_factory("independent-session-2")

        # Verify they have different session names
        assert tracer1.session_name != tracer2.session_name

        # Test that changing one doesn't affect the other
        original_session2 = tracer2.session_name

        # Simulate some operations on tracer1
        with tracer1.start_span("operation1") as span:
            span.set_attribute("operation", "test1")

        # Verify tracer2 is unchanged
        assert tracer2.session_name == original_session2

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_decorator_with_explicit_tracer(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test @trace decorator with explicit tracer parameter."""
        tracer = tracer_factory("decorator-test")

        @trace(  # type: ignore[misc]
            event_name="test_event", event_type="tool", tracer=tracer
        )
        def test_function(x: Any, y: Any) -> Any:
            return x + y

        # Test that the function works and tracing is applied
        result = test_function(5, 3)
        assert result == 8

        # Verify the tracer is properly configured
        assert tracer.project == real_project
        assert tracer.source == real_source

        # Clean up
        tracer.shutdown()

    def test_async_decorator_with_explicit_tracer(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test @atrace decorator with explicit tracer parameter."""
        tracer = tracer_factory("async-decorator-test")

        @atrace(  # type: ignore[misc]
            event_name="async_test_event", event_type="tool", tracer=tracer
        )
        async def async_test_function(x: Any, y: Any) -> Any:
            return x * y

        # Test that the async function works
        # asyncio imported at top level

        result = asyncio.run(async_test_function(4, 6))
        assert result == 24

        # Verify the tracer is properly configured
        assert tracer.project == real_project
        assert tracer.source == real_source

        # Clean up
        tracer.shutdown()

    def test_multiple_tracers_with_different_configs(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test multiple tracers with different configurations."""
        # Create tracers with different session names and configurations
        tracer1 = tracer_factory("config1-session")

        tracer2 = tracer_factory("config2-session")

        # Verify they have different session names (both use standard factory config)
        assert "config1-session" in tracer1.session_name
        assert "config2-session" in tracer2.session_name
        assert tracer1.session_name != tracer2.session_name

        # Test both can work simultaneously
        with tracer1.start_span("span1") as span1:
            span1.set_attribute("config", "tracer1")

        with tracer2.start_span("span2") as span2:
            span2.set_attribute("config", "tracer2")

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_tracer_lifecycle_management(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test proper lifecycle management of multiple tracers."""
        tracers = []

        # Create multiple tracers
        for i in range(3):
            tracer = tracer_factory(f"lifecycle-session-{i}")
            tracers.append(tracer)

        # Verify all are independent
        assert len(set(tracers)) == 3  # All different instances

        # Test they can all work
        for i, tracer in enumerate(tracers):
            with tracer.start_span(f"span-{i}") as span:
                span.set_attribute("tracer_index", i)
                assert span.is_recording()

        # Clean up all tracers
        for tracer in tracers:
            tracer.shutdown()  # type: ignore[attr-defined]

    def test_session_creation_with_multiple_tracers(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test that multiple tracers can create sessions independently."""
        tracer1 = tracer_factory("session-test-1")

        tracer2 = tracer_factory("session-test-2")

        # Test session creation with both tracers
        with tracer1.start_span("session1") as span1:
            span1.set_attribute("session", "tracer1")
            span1.add_event("session_started", {"tracer": "tracer1"})

        with tracer2.start_span("session2") as span2:
            span2.set_attribute("session", "tracer2")
            span2.add_event("session_started", {"tracer": "tracer2"})

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_error_handling_with_multiple_tracers(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test error handling when multiple tracers are involved."""
        tracer1 = tracer_factory("error-test-1")

        tracer2 = tracer_factory("error-test-2")

        # Test that errors in one tracer don't affect the other
        try:
            with tracer1.start_span("error_span") as span:
                # Simulate an error
                raise ValueError("Test error")
        except ValueError:
            # Error should be caught and not affect tracer2
            pass

        # Tracer2 should still work normally
        with tracer2.start_span("normal_span") as span:
            span.set_attribute("status", "working")
            assert span.is_recording()

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_concurrent_tracer_usage(
        self,
        tracer_factory: Any,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test concurrent usage of multiple tracers."""
        # threading imported at top level

        tracer1 = tracer_factory("concurrent-1")

        tracer2 = tracer_factory("concurrent-2")

        results = []

        def use_tracer1() -> None:
            with tracer1.start_span("thread1_span") as span:
                span.set_attribute("thread", "thread1")
                results.append("tracer1_used")

        def use_tracer2() -> None:
            with tracer2.start_span("thread2_span") as span:
                span.set_attribute("thread", "thread2")
                results.append("tracer2_used")

        # Run both tracers concurrently
        thread1 = threading.Thread(target=use_tracer1)
        thread2 = threading.Thread(target=use_tracer2)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Verify both tracers were used
        assert "tracer1_used" in results
        assert "tracer2_used" in results
        assert len(results) == 2

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_force_flush_multi_instance_integration(
        self,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test force_flush functionality with multiple tracer instances."""
        # Create multiple tracer instances
        tracer1 = HoneyHiveTracer.init(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-multi-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer.init(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-multi-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Create spans from both tracers
        with tracer1.start_span(  # type: ignore[attr-defined]
            "multi_instance_span_1"
        ) as span:
            span.set_attribute("tracer_id", "tracer1")
            span.set_attribute("test_type", "multi_instance_flush")

        with tracer2.start_span(  # type: ignore[attr-defined]
            "multi_instance_span_2"
        ) as span:
            span.set_attribute("tracer_id", "tracer2")
            span.set_attribute("test_type", "multi_instance_flush")

        # Test force_flush from both tracers
        result1 = tracer1.force_flush(timeout_millis=5000)  # type: ignore[attr-defined]
        result2 = tracer2.force_flush(timeout_millis=5000)  # type: ignore[attr-defined]

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

        # Clean up
        tracer1.shutdown()  # type: ignore[attr-defined]
        tracer2.shutdown()  # type: ignore[attr-defined]

    def test_force_flush_sequence_multi_instance_integration(
        self,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test sequential force_flush operations across multiple tracers."""
        tracers = []

        # Create multiple tracers
        for i in range(3):
            tracer = HoneyHiveTracer.init(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name=f"force-flush-seq-{i}",
                test_mode=False,
                disable_http_tracing=True,
            )
            tracers.append(tracer)

        # Create spans and flush sequentially
        for i, tracer in enumerate(tracers):
            # Create spans
            with tracer.start_span(  # type: ignore[attr-defined]
                f"sequential_span_{i}"
            ) as span:
                span.set_attribute("tracer_index", i)
                span.set_attribute("sequence_test", True)

            # Force flush
            result = tracer.force_flush(  # type: ignore[attr-defined]
                timeout_millis=3000
            )
            assert isinstance(result, bool)

        # Final concurrent flush from all tracers
        results = []
        for tracer in tracers:
            result = tracer.force_flush(  # type: ignore[attr-defined]
                timeout_millis=2000
            )
            results.append(result)
            assert isinstance(result, bool)

        # Verify all flushes completed
        assert len(results) == 3

        # Clean up all tracers
        for tracer in tracers:
            tracer.shutdown()  # type: ignore[attr-defined]

    def test_force_flush_with_enrich_span_multi_instance_integration(
        self,
        real_api_key: Any,  # pylint: disable=unused-argument
        real_project: Any,  # pylint: disable=unused-argument
        real_source: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test force_flush with enrich_span across multiple tracer instances."""
        tracer1 = HoneyHiveTracer.init(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-enrich-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer.init(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-enrich-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Use enrich_span with first tracer
        # enrich_span imported at top level

        with enrich_span(
            metadata={"tracer": "first", "operation": "multi_instance_test"},
            outputs={"status": "processing"},
            error=None,
            tracer=tracer1,
        ):
            with tracer1.start_span(  # type: ignore[attr-defined]
                "enriched_span_1"
            ) as span:
                span.set_attribute("enriched_by", "tracer1")

        # Use enrich_span with second tracer (direct call)
        success = tracer2.enrich_span(  # type: ignore[attr-defined]
            metadata={"tracer": "second", "operation": "direct_call_test"},
            outputs={"result": "completed"},
            error=None,
        )
        assert isinstance(success, bool)

        # Force flush both tracers
        result1 = tracer1.force_flush(timeout_millis=4000)  # type: ignore[attr-defined]
        result2 = tracer2.force_flush(timeout_millis=4000)  # type: ignore[attr-defined]

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

        # Clean up
        tracer1.shutdown()  # type: ignore[attr-defined]
        tracer2.shutdown()  # type: ignore[attr-defined]
