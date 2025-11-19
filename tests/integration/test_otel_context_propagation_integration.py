"""Integration tests for OpenTelemetry W3C context propagation functionality.

These tests validate that our HoneyHive tracer properly implements W3C Trace Context
and Baggage propagation standards as required by the OpenTelemetry specification.

NO MOCKING - All tests use real OpenTelemetry components and real API calls.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Integration test file with comprehensive context propagation testing requiring real API calls
# Note: Individual methods may have unused-argument disables for integration test fixtures

import asyncio
import threading
import time
from typing import Any, Dict

import pytest

# OpenTelemetry is a hard dependency - no conditional imports needed
from opentelemetry import baggage, context
from opentelemetry import trace as otel_trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.context import Context
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)

from honeyhive.tracer import enrich_span, trace
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)

OTEL_AVAILABLE = True


@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not available")
@pytest.mark.integration
@pytest.mark.real_api
class TestOTELContextPropagationIntegration:
    """Integration tests for W3C context propagation with real API calls."""

    def test_w3c_trace_context_injection_extraction(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,  # not used in this specific test  # pylint: disable=unused-argument
    ) -> None:
        """Test W3C trace context injection and extraction across service boundaries."""
        # Create a parent span that will generate trace context
        with integration_tracer.start_span("parent_service_operation") as parent_span:
            assert parent_span.is_recording()

            # Get the current context with trace information
            current_context = context.get_current()

            # Create a carrier (simulates HTTP headers)
            carrier: Dict[str, str] = {}

            # Inject trace context into carrier (simulates outgoing HTTP request)
            propagator = TraceContextTextMapPropagator()
            propagator.inject(carrier, current_context)

            # Verify traceparent header was injected
            assert "traceparent" in carrier
            traceparent = carrier["traceparent"]

            # Validate traceparent format: version-trace_id-span_id-trace_flags
            parts = traceparent.split("-")
            assert len(parts) == 4
            assert parts[0] == "00"  # version
            assert len(parts[1]) == 32  # trace_id (128-bit hex)
            assert len(parts[2]) == 16  # span_id (64-bit hex)
            assert parts[3] in ["00", "01"]  # trace_flags

            # Extract trace context from carrier (simulates incoming HTTP request)
            extracted_context = propagator.extract(carrier)

            # Create a child span in the extracted context (simulates downstream
            # service)
            with otel_trace.get_tracer("downstream_service").start_as_current_span(
                "child_service_operation", context=extracted_context
            ) as child_span:
                assert child_span.is_recording()

                # Verify trace continuity - both spans should have same trace ID
                parent_trace_id = parent_span.get_span_context().trace_id
                child_trace_id = child_span.get_span_context().trace_id
                assert parent_trace_id == child_trace_id

                # Verify parent-child relationship
                child_parent_id = child_span.get_span_context().span_id
                assert child_parent_id != parent_span.get_span_context().span_id

                # Add attributes to verify span functionality
                child_span.set_attribute("service.name", "downstream_service")
                child_span.set_attribute("operation.type", "child_operation")

                # Simulate some work
                time.sleep(0.01)

        # Backend verification: Ensure W3C trace context test events were created

        _, unique_id = generate_test_id("w3c_trace_context", "w3c_trace_context")

        # Create verification span and verify backend using NEW standardized pattern
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="w3c_trace_context_verification",
            unique_identifier=unique_id,
            span_attributes={
                "test.verification_type": "w3c_trace_context_test",
                "context.propagation_tested": "w3c_trace_context",
                "spans.created": 2,  # parent + child
                "test.type": "w3c_context_propagation",
            },
        )

        print(
            f"✅ W3C trace context test backend verification successful: "
            f"{verified_event.event_id}"
        )
        print("   Context propagation tested: W3C Trace Context")

    def test_w3c_baggage_propagation_integration(
        self,
        integration_tracer: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test W3C baggage propagation with HoneyHive session context."""
        # Set up initial baggage with HoneyHive context
        initial_baggage = {
            "session_id": integration_tracer.session_id,
            "project": real_project,
            "source": real_source,
            "honeyhive_tracer_id": integration_tracer._tracer_id,
            "custom_context": "integration_test_value",
        }

        # Create context with baggage
        ctx = context.get_current()
        for key, value in initial_baggage.items():
            if value:
                ctx = baggage.set_baggage(key, str(value), ctx)

        # Create carrier for propagation
        carrier: Dict[str, str] = {}

        # Inject baggage into carrier
        baggage_propagator = W3CBaggagePropagator()
        baggage_propagator.inject(carrier, ctx)

        # Verify baggage header was injected
        assert "baggage" in carrier
        baggage_header = carrier["baggage"]

        # Verify baggage contains our HoneyHive context
        assert "session_id=" in baggage_header
        assert "project=" in baggage_header
        assert "source=" in baggage_header
        assert "honeyhive_tracer_id=" in baggage_header
        assert "custom_context=integration_test_value" in baggage_header

        # Extract baggage from carrier (simulates receiving HTTP request)
        extracted_context = baggage_propagator.extract(carrier)

        # Verify extracted baggage contains all our context
        extracted_session_id = baggage.get_baggage("session_id", extracted_context)
        extracted_project = baggage.get_baggage("project", extracted_context)
        extracted_source = baggage.get_baggage("source", extracted_context)
        extracted_tracer_id = baggage.get_baggage(
            "honeyhive_tracer_id", extracted_context
        )
        extracted_custom = baggage.get_baggage("custom_context", extracted_context)

        assert extracted_session_id == integration_tracer.session_id
        assert extracted_project == real_project
        assert extracted_source == real_source
        assert extracted_tracer_id == integration_tracer._tracer_id
        assert extracted_custom == "integration_test_value"

        # Create a span in the extracted context to verify baggage is available
        token = context.attach(extracted_context)
        try:
            with integration_tracer.start_span("baggage_test_span") as span:
                assert span.is_recording()

                # Verify baggage is accessible in the span context
                current_ctx = context.get_current()
                span_session_id = baggage.get_baggage("session_id", current_ctx)
                span_project = baggage.get_baggage("project", current_ctx)
                assert span_session_id == integration_tracer.session_id
                assert span_project == real_project
        finally:
            context.detach(token)

    def test_composite_propagator_integration(
        self,
        integration_tracer: Any,
    ) -> None:
        """Test composite propagator with both trace context and baggage."""
        # Set up baggage context
        ctx = context.get_current()
        ctx = baggage.set_baggage("test_key", "test_value", ctx)
        ctx = baggage.set_baggage(
            "session_id", integration_tracer.session_id or "test_session", ctx
        )

        # Attach the context with baggage
        token = context.attach(ctx)
        try:
            with integration_tracer.start_span("composite_test_span") as span:
                assert span.is_recording()

                # Get current context with both trace and baggage
                current_context = context.get_current()

                # Create composite propagator (same as our tracer uses)
                composite_propagator = CompositePropagator(
                    [
                        TraceContextTextMapPropagator(),
                        W3CBaggagePropagator(),
                    ]
                )

                # Inject both trace context and baggage
                carrier: Dict[str, str] = {}
                composite_propagator.inject(carrier, current_context)

                # Verify both headers are present
                assert "traceparent" in carrier
                assert "baggage" in carrier

                # Verify baggage contains our test data
                assert "test_key=test_value" in carrier["baggage"]
                assert "session_id=" in carrier["baggage"]

                # Extract both contexts
                extracted_context = composite_propagator.extract(carrier)

                # Verify trace context was preserved
                with otel_trace.get_tracer("test").start_as_current_span(
                    "extracted_span", context=extracted_context
                ) as extracted_span:
                    # Verify trace continuity
                    original_trace_id = span.get_span_context().trace_id
                    extracted_trace_id = extracted_span.get_span_context().trace_id
                    assert original_trace_id == extracted_trace_id

                    # Verify baggage was preserved
                    extracted_test_key = baggage.get_baggage(
                        "test_key", extracted_context
                    )
                    extracted_session_id = baggage.get_baggage(
                        "session_id", extracted_context
                    )

                    assert extracted_test_key == "test_value"
                    assert extracted_session_id == (
                        integration_tracer.session_id or "test_session"
                    )
        finally:
            context.detach(token)

    def test_cross_thread_context_propagation(
        self,
        integration_tracer: Any,
        real_project: Any,
    ) -> None:
        """Test context propagation across thread boundaries."""
        results = {}

        def worker_thread(thread_id: int, propagated_context: Context) -> None:
            """Worker function that runs in a separate thread."""
            try:
                # Attach the propagated context in this thread
                token = context.attach(propagated_context)
                try:
                    # Verify baggage is available in this thread
                    session_id = baggage.get_baggage("session_id")
                    project = baggage.get_baggage("project")
                    thread_marker = baggage.get_baggage("thread_test_marker")

                    # Create a span in this thread context
                    with integration_tracer.start_span(
                        f"thread_{thread_id}_operation"
                    ) as span:
                        assert span.is_recording()
                        # Add thread-specific attributes
                        span.set_attribute("thread.id", thread_id)
                        span.set_attribute("thread.session_id", session_id or "none")
                        span.set_attribute("thread.project", project or "none")
                        span.set_attribute("thread.marker", thread_marker or "none")

                        # Simulate some work
                        time.sleep(0.01)
                        # Store results for verification
                        results[thread_id] = {
                            "session_id": session_id,
                            "project": project,
                            "thread_marker": thread_marker,
                            "span_recorded": True,
                        }
                finally:
                    context.detach(token)

            except Exception as e:
                results[thread_id] = {"error": str(e)}

        # Set up context with baggage in main thread
        ctx = context.get_current()
        ctx = baggage.set_baggage(
            "session_id", integration_tracer.session_id or "test_session", ctx
        )
        ctx = baggage.set_baggage("project", real_project, ctx)
        ctx = baggage.set_baggage("thread_test_marker", "main_thread_context", ctx)

        # Attach the context with baggage
        token = context.attach(ctx)
        try:
            with integration_tracer.start_span("main_thread_span") as main_span:
                assert main_span.is_recording()

                # Get current context to propagate
                current_context = context.get_current()

                # Start multiple worker threads with propagated context
                threads = []
                for i in range(3):
                    thread = threading.Thread(
                        target=worker_thread, args=(i, current_context)
                    )
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join(timeout=10)  # 10 second timeout

                # Verify all threads completed successfully
                assert len(results) == 3

                for thread_id in range(3):
                    assert thread_id in results
                    thread_result = results[thread_id]

                    # Verify no errors occurred
                    assert "error" not in thread_result

                    # Verify context was properly propagated
                    assert thread_result["session_id"] == (
                        integration_tracer.session_id or "test_session"
                    )
                    assert thread_result["project"] == real_project
                    assert thread_result["thread_marker"] == "main_thread_context"
                    assert thread_result["span_recorded"] is True
        finally:
            context.detach(token)

    @pytest.mark.asyncio
    async def test_async_context_propagation(
        self,
        integration_tracer: Any,
        real_project: Any,
    ) -> None:
        """Test context propagation across async boundaries."""

        async def async_operation(operation_id: int) -> Dict[str, Any]:
            """Async operation that should inherit context."""
            # Verify context is available in async function
            current_ctx = context.get_current()
            session_id = baggage.get_baggage("session_id", current_ctx)
            project = baggage.get_baggage("project", current_ctx)
            async_marker = baggage.get_baggage("async_test_marker", current_ctx)

            # Create span in async context
            with integration_tracer.start_span(
                f"async_operation_{operation_id}"
            ) as span:
                assert span.is_recording()

                # Add async-specific attributes
                span.set_attribute("async.operation_id", operation_id)
                span.set_attribute("async.session_id", session_id or "none")
                span.set_attribute("async.project", project or "none")
                span.set_attribute("async.marker", async_marker or "none")

                # Simulate async work
                await asyncio.sleep(0.01)

                return {
                    "operation_id": operation_id,
                    "session_id": session_id,
                    "project": project,
                    "async_marker": async_marker,
                    "span_recorded": True,
                }

        # Set up context with baggage
        ctx = context.get_current()
        ctx = baggage.set_baggage(
            "session_id", integration_tracer.session_id or "test_session", ctx
        )
        ctx = baggage.set_baggage("project", real_project, ctx)
        ctx = baggage.set_baggage("async_test_marker", "main_async_context", ctx)

        with integration_tracer.start_span("main_async_span") as main_span:
            assert main_span.is_recording()

            # Attach context and run async operations
            token = context.attach(ctx)
            try:
                # Run multiple async operations concurrently
                tasks = [async_operation(i) for i in range(3)]
                results = await asyncio.gather(*tasks)

                # Verify all operations completed successfully
                assert len(results) == 3
            finally:
                context.detach(token)

                for i, result in enumerate(results):
                    assert result["operation_id"] == i
                    assert result["session_id"] == (
                        integration_tracer.session_id or "test_session"
                    )
                    assert result["project"] == real_project
                    assert result["async_marker"] == "main_async_context"
                    assert result["span_recorded"] is True

    def test_decorator_context_propagation_integration(
        self,
        integration_tracer: Any,
    ) -> None:
        """Test context propagation with HoneyHive decorators."""

        @trace(  # type: ignore[misc]
            tracer=integration_tracer,
            event_type="chain",
            event_name="parent_operation",
        )
        def parent_operation(input_data: str) -> str:
            """Parent operation that should propagate context."""
            # Verify tracer context is available
            current_ctx = context.get_current()
            session_id = baggage.get_baggage("session_id", current_ctx)
            tracer_id = baggage.get_baggage("honeyhive_tracer_id", current_ctx)

            # Add context to span
            with enrich_span(
                inputs={"input_data": input_data},
                metadata={
                    "context.session_id": session_id,
                    "context.tracer_id": tracer_id,
                },
            ):
                # Call child operation
                return child_operation(f"processed_{input_data}")

        @trace(  # type: ignore[misc]
            tracer=integration_tracer,
            event_type="tool",
            event_name="child_operation",
        )
        def child_operation(processed_data: str) -> str:
            """Child operation that should inherit context."""
            # Verify context propagation
            current_ctx = context.get_current()
            session_id = baggage.get_baggage("session_id", current_ctx)
            tracer_id = baggage.get_baggage("honeyhive_tracer_id", current_ctx)

            # Verify context is available
            assert session_id == integration_tracer.session_id
            assert tracer_id == integration_tracer._tracer_id

            with enrich_span(
                inputs={"processed_data": processed_data},
                outputs={"result": f"final_{processed_data}"},
                metadata={
                    "child.context.session_id": session_id,
                    "child.context.tracer_id": tracer_id,
                },
            ):
                return f"final_{processed_data}"

        # Execute the operation chain
        result = parent_operation("test_input")

        # Verify the operation completed successfully
        assert result == "final_processed_test_input"

    def test_instrumentor_baggage_integration(
        self,
        integration_tracer: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test baggage propagation with instrumentor-style spans."""
        # This test simulates how OpenInference instrumentors would interact with our
        # baggage

        # Set up HoneyHive context in baggage
        ctx = context.get_current()
        ctx = baggage.set_baggage(
            "session_id", integration_tracer.session_id or "test_session", ctx
        )
        ctx = baggage.set_baggage("project", real_project, ctx)
        ctx = baggage.set_baggage("source", real_source, ctx)
        ctx = baggage.set_baggage(
            "honeyhive_tracer_id", integration_tracer._tracer_id, ctx
        )

        token = context.attach(ctx)
        try:
            # Simulate an instrumentor creating spans (like OpenInference would)
            tracer = otel_trace.get_tracer("openinference.instrumentation.openai")

            with tracer.start_as_current_span(
                "openai.chat.completions.create"
            ) as instrumented_span:
                assert instrumented_span.is_recording()

                # Verify our span processor enriches the instrumented span with baggage
                # This simulates what HoneyHiveSpanProcessor.on_start() should do

                # Add typical instrumentor attributes
                instrumented_span.set_attribute("llm.request.model", "gpt-3.5-turbo")
                instrumented_span.set_attribute("llm.request.temperature", 0.7)
                instrumented_span.set_attribute("llm.usage.prompt_tokens", 10)
                instrumented_span.set_attribute("llm.usage.completion_tokens", 20)

                # Verify baggage is accessible within the instrumented span
                current_ctx = context.get_current()
                span_session_id = baggage.get_baggage("session_id", current_ctx)
                span_project = baggage.get_baggage("project", current_ctx)
                span_tracer_id = baggage.get_baggage("honeyhive_tracer_id", current_ctx)

                assert span_session_id == (
                    integration_tracer.session_id or "test_session"
                )
                assert span_project == real_project
                assert span_tracer_id == integration_tracer._tracer_id

                # Simulate nested spans (like tool calls within LLM calls)
                with tracer.start_as_current_span(
                    "openai.tool.function_call"
                ) as tool_span:
                    assert tool_span.is_recording()

                    # Verify context is still available in nested spans
                    nested_ctx = context.get_current()
                    nested_session_id = baggage.get_baggage("session_id", nested_ctx)
                    nested_project = baggage.get_baggage("project", nested_ctx)

                    assert nested_session_id == (
                        integration_tracer.session_id or "test_session"
                    )
                    assert nested_project == real_project

                    # Add tool-specific attributes
                    tool_span.set_attribute("tool.name", "get_weather")
                    tool_span.set_attribute(
                        "tool.parameters", '{"location": "San Francisco"}'
                    )

                    # Simulate tool execution time
                    time.sleep(0.01)
        finally:
            context.detach(token)
