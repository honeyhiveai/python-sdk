"""Integration tests for multi-instance tracer functionality in HoneyHive."""

import time

import pytest

from honeyhive.tracer.decorators import atrace, trace
from honeyhive.tracer.otel_tracer import HoneyHiveTracer


@pytest.mark.integration
@pytest.mark.multi_instance
class TestMultiInstanceTracerIntegration:
    """Test multi-instance tracer integration and end-to-end functionality."""

    def test_multiple_tracers_coexistence(
        self, real_api_key, real_project, real_source
    ):
        """Test that multiple tracers can coexist and work independently."""
        # Create multiple tracers with different configurations
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="tracer1-session",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="tracer2-session",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Verify they're independent instances
        assert tracer1 is not tracer2
        assert tracer1.session_name == "tracer1-session"
        assert tracer2.session_name == "tracer2-session"

        # Test both can create spans independently
        with tracer1.start_span("span1") as span1:
            span1.set_attribute("tracer", "tracer1")
            span1.set_attribute("test", "coexistence")
            assert span1.is_recording()

        with tracer2.start_span("span2") as span2:
            span2.set_attribute("tracer", "tracer2")
            span2.set_attribute("test", "coexistence")
            assert span2.is_recording()

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_tracer_independence(self, real_api_key, real_project, real_source):
        """Test that tracers are completely independent."""
        # Create tracers with different configurations
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="independent-session-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="independent-session-2",
            test_mode=False,
            disable_http_tracing=True,
        )

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
        self, real_api_key, real_project, real_source
    ):
        """Test @trace decorator with explicit tracer parameter."""
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="decorator-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        @trace(event_name="test_event", event_type="test", tracer=tracer)
        def test_function(x, y):
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
        self, real_api_key, real_project, real_source
    ):
        """Test @atrace decorator with explicit tracer parameter."""
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="async-decorator-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        @atrace(event_name="async_test_event", event_type="test", tracer=tracer)
        async def async_test_function(x, y):
            return x * y

        # Test that the async function works
        import asyncio

        result = asyncio.run(async_test_function(4, 6))
        assert result == 24

        # Verify the tracer is properly configured
        assert tracer.project == real_project
        assert tracer.source == real_source

        # Clean up
        tracer.shutdown()

    def test_multiple_tracers_with_different_configs(
        self, real_api_key, real_project, real_source
    ):
        """Test multiple tracers with different configurations."""
        # Create tracers with different session names and configurations
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="config1-session",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="config2-session",
            test_mode=False,
            disable_http_tracing=False,  # Different config
        )

        # Verify they have different configurations
        assert tracer1.session_name == "config1-session"
        assert tracer2.session_name == "config2-session"
        assert tracer1.disable_http_tracing != tracer2.disable_http_tracing

        # Test both can work simultaneously
        with tracer1.start_span("span1") as span1:
            span1.set_attribute("config", "tracer1")

        with tracer2.start_span("span2") as span2:
            span2.set_attribute("config", "tracer2")

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_tracer_lifecycle_management(self, real_api_key, real_project, real_source):
        """Test proper lifecycle management of multiple tracers."""
        tracers = []

        # Create multiple tracers
        for i in range(3):
            tracer = HoneyHiveTracer(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name=f"lifecycle-session-{i}",
                test_mode=False,
                disable_http_tracing=True,
            )
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
            tracer.shutdown()

    def test_session_creation_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test that multiple tracers can create sessions independently."""
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="session-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="session-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

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
        self, real_api_key, real_project, real_source
    ):
        """Test error handling when multiple tracers are involved."""
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="error-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="error-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

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

    def test_concurrent_tracer_usage(self, real_api_key, real_project, real_source):
        """Test concurrent usage of multiple tracers."""
        import threading

        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="concurrent-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="concurrent-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        results = []

        def use_tracer1():
            with tracer1.start_span("thread1_span") as span:
                span.set_attribute("thread", "thread1")
                results.append("tracer1_used")

        def use_tracer2():
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
        self, real_api_key, real_project, real_source
    ):
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
        with tracer1.start_span("multi_instance_span_1") as span:
            span.set_attribute("tracer_id", "tracer1")
            span.set_attribute("test_type", "multi_instance_flush")

        with tracer2.start_span("multi_instance_span_2") as span:
            span.set_attribute("tracer_id", "tracer2")
            span.set_attribute("test_type", "multi_instance_flush")

        # Test force_flush from both tracers
        result1 = tracer1.force_flush(timeout_millis=5000)
        result2 = tracer2.force_flush(timeout_millis=5000)

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_force_flush_sequence_multi_instance_integration(
        self, real_api_key, real_project, real_source
    ):
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
            with tracer.start_span(f"sequential_span_{i}") as span:
                span.set_attribute("tracer_index", i)
                span.set_attribute("sequence_test", True)

            # Force flush
            result = tracer.force_flush(timeout_millis=3000)
            assert isinstance(result, bool)

        # Final concurrent flush from all tracers
        results = []
        for tracer in tracers:
            result = tracer.force_flush(timeout_millis=2000)
            results.append(result)
            assert isinstance(result, bool)

        # Verify all flushes completed
        assert len(results) == 3

        # Clean up all tracers
        for tracer in tracers:
            tracer.shutdown()

    def test_force_flush_with_enrich_span_multi_instance_integration(
        self, real_api_key, real_project, real_source
    ):
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
        from honeyhive.tracer.otel_tracer import enrich_span

        with enrich_span(
            metadata={"tracer": "first", "operation": "multi_instance_test"},
            outputs={"status": "processing"},
            error=None,
            tracer=tracer1,
        ):
            with tracer1.start_span("enriched_span_1") as span:
                span.set_attribute("enriched_by", "tracer1")

        # Use enrich_span with second tracer (direct call)
        success = tracer2.enrich_span(
            metadata={"tracer": "second", "operation": "direct_call_test"},
            outputs={"result": "completed"},
            error=None,
        )
        assert isinstance(success, bool)

        # Force flush both tracers
        result1 = tracer1.force_flush(timeout_millis=4000)
        result2 = tracer2.force_flush(timeout_millis=4000)

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()
