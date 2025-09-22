"""Integration tests for OpenTelemetry TracerProvider integration strategies.

These tests validate that our HoneyHive tracer properly detects and integrates with
different TracerProvider scenarios as required by the OpenTelemetry specification.

NO MOCKING - All tests use real OpenTelemetry components and real API calls.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Integration test file with comprehensive provider strategy testing requiring real API calls

import time
from typing import Any

import pytest

# OpenTelemetry is a hard dependency - no need for try/except
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import NoOpTracerProvider, ProxyTracerProvider

from honeyhive.tracer import set_global_provider, trace
from honeyhive.tracer.integration.detection import IntegrationStrategy, ProviderDetector
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)

OTEL_AVAILABLE = True


@pytest.mark.integration
@pytest.mark.real_api
class TestOTELProviderStrategiesIntegration:
    """Integration tests for TracerProvider detection and integration strategies."""

    def test_main_provider_strategy_with_noop_provider(
        self,
        tracer_factory: Any,
        integration_client: Any,
        real_project: Any,
    ) -> None:
        """Test MAIN_PROVIDER strategy when starting with NoOpTracerProvider."""
        # Reset to NoOp provider (simulates fresh environment)
        noop_provider = NoOpTracerProvider()
        set_global_provider(noop_provider)

        # Verify we start with NoOp provider
        initial_provider = otel_trace.get_tracer_provider()
        assert isinstance(initial_provider, NoOpTracerProvider)

        # Initialize HoneyHive tracer - should detect NoOp and become main provider
        tracer = tracer_factory("tracer")

        # Verify tracer detected the strategy correctly
        assert tracer.is_main_provider is True

        # Verify global provider was replaced
        final_provider = otel_trace.get_tracer_provider()
        assert not isinstance(final_provider, NoOpTracerProvider)
        assert isinstance(final_provider, TracerProvider)
        assert final_provider is tracer.provider

        # Test span creation works with the new provider
        with tracer.start_span("main_provider_test_span") as span:
            assert span.is_recording()
            span.set_attribute("provider.strategy", "main_provider")
            span.set_attribute("provider.replaced", "noop")

            # Verify span processor is working
            assert tracer.span_processor is not None

            # Test that global tracer also works
            global_tracer = otel_trace.get_tracer("test_global")
            with global_tracer.start_as_current_span("global_span") as global_span:
                assert global_span.is_recording()
                global_span.set_attribute("tracer.type", "global")

        # Backend verification: Ensure main provider strategy test events were created
        _, unique_id = generate_test_id("main_provider_noop", "main_provider_noop")

        # Create verification span and verify backend using NEW standardized pattern
        verified_event = verify_tracer_span(
            tracer=tracer,
            client=integration_client,
            project=real_project,
            span_name="main_provider_noop_verification",
            unique_identifier=unique_id,
            span_attributes={
                "test.verification_type": "main_provider_noop_test",
                "provider.strategy": "MAIN_PROVIDER",
                "provider.initial_type": "NoOpTracerProvider",
                "test.type": "provider_strategy_integration",
            },
        )

        print(
            f"✅ Main provider strategy (NoOp) test backend verification "
            f"successful: {verified_event.event_id}"
        )
        # Cleanup handled by tracer_factory fixture

    def test_main_provider_strategy_with_proxy_provider(
        self,
        tracer_factory: Any,
        otel_provider_reset: Any,
    ) -> None:
        """Test MAIN_PROVIDER strategy when starting with ProxyTracerProvider."""
        # Reset to Proxy provider (simulates environment before any real provider
        # is set)
        proxy_provider = ProxyTracerProvider()
        otel_provider_reset(proxy_provider)

        # Verify we start with Proxy provider
        initial_provider = otel_trace.get_tracer_provider()
        assert isinstance(initial_provider, ProxyTracerProvider)

        # Initialize HoneyHive tracer - should detect Proxy and become main provider
        tracer = tracer_factory("tracer")

        # Verify tracer detected the strategy correctly
        assert tracer.is_main_provider is True

        # Verify global provider was replaced
        final_provider = otel_trace.get_tracer_provider()
        assert not isinstance(final_provider, ProxyTracerProvider)
        assert isinstance(final_provider, TracerProvider)
        assert final_provider is tracer.provider

        # Test span creation works with the new provider
        with tracer.start_span("proxy_replacement_test_span") as span:
            assert span.is_recording()
            span.set_attribute("provider.strategy", "main_provider")
            span.set_attribute("provider.replaced", "proxy")

            # Verify span processor is working
            assert tracer.span_processor is not None
        # Cleanup handled by tracer_factory fixture

    def test_independent_provider_strategy_with_existing_provider(
        self,
        tracer_factory: Any,
        otel_provider_reset: Any,
    ) -> None:
        """Test independent provider strategy when real TracerProvider already
        exists (multi-instance architecture)."""
        # Set up a real TracerProvider first (simulates existing instrumentation)
        existing_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        existing_processor = SimpleSpanProcessor(console_exporter)
        otel_provider_reset(existing_provider, [existing_processor])

        # Verify we start with the existing provider
        initial_provider = otel_trace.get_tracer_provider()
        assert initial_provider is existing_provider

        # Initialize HoneyHive tracer - should create independent provider
        # (multi-instance)
        tracer = tracer_factory("tracer")

        # Verify tracer detected the strategy correctly (multi-instance architecture)
        assert tracer.is_main_provider is False
        assert (
            tracer.provider is not existing_provider
        )  # Independent provider for multi-instance

        # Verify global provider was NOT replaced
        final_provider = otel_trace.get_tracer_provider()
        assert final_provider is existing_provider

        # Test span creation works with the independent provider
        with tracer.start_span("independent_provider_test_span") as span:
            assert span.is_recording()
            span.set_attribute("provider.strategy", "independent_provider")
            span.set_attribute("provider.integration", "multi_instance")

            # Verify our span processor exists on the independent provider
            # Multi-instance architecture: each tracer has its own provider and
            # processors
            processors = tracer.provider._active_span_processor._span_processors
            assert len(processors) >= 1  # At least our HoneyHive processor

        # Test that both existing and HoneyHive spans work
        existing_tracer = otel_trace.get_tracer("existing_instrumentation")
        with existing_tracer.start_as_current_span("existing_span") as existing_span:
            assert existing_span.is_recording()
            existing_span.set_attribute("tracer.type", "existing")

            # Create nested HoneyHive span
            with tracer.start_span("nested_honeyhive_span") as nested_span:
                assert nested_span.is_recording()
                nested_span.set_attribute("tracer.type", "honeyhive")

                # Verify trace continuity
                existing_trace_id = existing_span.get_span_context().trace_id
                nested_trace_id = nested_span.get_span_context().trace_id
                assert existing_trace_id == nested_trace_id
        # Cleanup handled by tracer_factory fixture

    def test_multiple_honeyhive_tracers_with_existing_provider(
        self,
        tracer_factory: Any,
        otel_provider_reset: Any,
    ) -> None:
        """Test multiple HoneyHive tracers integrating with existing provider."""
        # Set up existing provider
        existing_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        existing_processor = SimpleSpanProcessor(console_exporter)
        otel_provider_reset(existing_provider, [existing_processor])

        # Create first HoneyHive tracer
        tracer1 = tracer_factory("tracer1")

        # Create second HoneyHive tracer
        tracer2 = tracer_factory("tracer2")

        # Verify both tracers use independent provider strategy (multi-instance
        # architecture)
        assert tracer1.is_main_provider is False
        assert tracer2.is_main_provider is False
        assert tracer1.provider is not existing_provider  # Independent provider
        assert tracer2.provider is not existing_provider  # Independent provider
        assert tracer1.provider is not tracer2.provider  # Each has its own provider

        # Verify both tracers are independent
        assert tracer1 is not tracer2
        assert tracer1.session_name != tracer2.session_name
        assert tracer1._tracer_id != tracer2._tracer_id

        # Test both tracers can create spans independently
        with tracer1.start_span("tracer1_span") as span1:
            assert span1.is_recording()
            span1.set_attribute("tracer.instance", "tracer1")
            span1.set_attribute("session.name", tracer1.session_name)

            with tracer2.start_span("tracer2_span") as span2:
                assert span2.is_recording()
                span2.set_attribute("tracer.instance", "tracer2")
                span2.set_attribute("session.name", tracer2.session_name)

                # Verify spans can be nested across tracers
                with tracer1.start_span("nested_cross_tracer_span") as nested_span:
                    assert nested_span.is_recording()
                    nested_span.set_attribute("tracer.cross_nesting", "true")
        # Cleanup handled by tracer_factory fixture

    def test_provider_detection_accuracy(
        self,
        otel_provider_reset: Any,
    ) -> None:
        """Test that ProviderDetector accurately identifies different provider types."""
        test_cases = [
            {
                "name": "NoOpTracerProvider",
                "provider": NoOpTracerProvider(),
                "expected_strategy": IntegrationStrategy.MAIN_PROVIDER,
            },
            {
                "name": "ProxyTracerProvider",
                "provider": ProxyTracerProvider(),
                "expected_strategy": IntegrationStrategy.MAIN_PROVIDER,
            },
            {
                "name": "Real TracerProvider (bare)",
                "provider": TracerProvider(),
                "expected_strategy": IntegrationStrategy.MAIN_PROVIDER,
                # Bare provider is non-functioning
            },
        ]

        for test_case in test_cases:
            # Set up the provider using the flexible fixture
            otel_provider_reset(test_case["provider"])

            # Test detection
            detector = ProviderDetector()
            provider_info = detector.get_provider_info()

            # Verify detection accuracy
            assert (
                provider_info["integration_strategy"] == test_case["expected_strategy"]
            )
            # Verify provider type (not object identity, since fixture may reset to
            # different instance)
            assert isinstance(
                provider_info["provider_instance"], type(test_case["provider"])
            )

            # Verify class name detection
            expected_class_name = test_case["provider"].__class__.__name__
            assert provider_info["provider_class_name"] == expected_class_name

    def test_provider_transition_scenarios(
        self,
        tracer_factory: Any,
    ) -> None:
        """Test provider transitions: NoOp → Real → HoneyHive integration."""
        # Scenario 1: Start with NoOp
        noop_provider = NoOpTracerProvider()
        set_global_provider(noop_provider)

        # Create first HoneyHive tracer - should become main provider
        tracer1 = tracer_factory("tracer1")

        assert tracer1.is_main_provider is True
        main_provider = otel_trace.get_tracer_provider()
        assert main_provider is tracer1.provider

        # Scenario 2: Another application sets up its own provider
        # (This simulates what happens when other instrumentation is added)
        app_provider = TracerProvider()
        app_exporter = ConsoleSpanExporter()
        app_processor = SimpleSpanProcessor(app_exporter)
        app_provider.add_span_processor(app_processor)
        # Use set_global_provider to override the existing provider (simulates
        # external app with override capability)
        set_global_provider(app_provider)

        # Scenario 3: Create second HoneyHive tracer - should integrate with app
        # provider
        tracer2 = tracer_factory("tracer2")

        assert tracer2.is_main_provider is False
        assert (
            tracer2.provider is not app_provider
        )  # Independent provider for multi-instance

        # Verify both tracers can still create spans
        with tracer1.start_span("tracer1_after_transition") as span1:
            assert span1.is_recording()
            span1.set_attribute("transition.phase", "after_app_provider")

        with tracer2.start_span("tracer2_with_independent_provider") as span2:
            assert span2.is_recording()
            span2.set_attribute("transition.phase", "independent_provider")
        # Cleanup handled by tracer_factory fixture

    def test_span_processor_integration_with_existing_processors(
        self,
        tracer_factory: Any,
    ) -> None:
        """Test that our span processor integrates correctly with existing
        processors."""
        # Set up provider with existing processors
        provider = TracerProvider()

        # Add multiple existing processors
        console_exporter = ConsoleSpanExporter()
        console_processor = SimpleSpanProcessor(console_exporter)
        provider.add_span_processor(console_processor)

        # Add batch processor
        batch_processor = BatchSpanProcessor(console_exporter)
        provider.add_span_processor(batch_processor)

        set_global_provider(provider)

        # Get initial processor count
        initial_processors = provider._active_span_processor._span_processors
        initial_count = len(initial_processors)

        # Initialize HoneyHive tracer
        tracer = tracer_factory("tracer")

        # Verify multi-instance architecture: tracer has its own independent provider
        assert tracer.provider is not provider  # Independent provider
        tracer_processors = tracer.provider._active_span_processor._span_processors
        tracer_count = len(tracer_processors)
        assert tracer_count >= 1  # Tracer has its own processors

        # Original provider should be unchanged
        final_processors = provider._active_span_processor._span_processors
        final_count = len(final_processors)
        assert final_count == initial_count  # Original provider unchanged

        # Test that all processors receive span events
        with tracer.start_span("multi_processor_test_span") as span:
            assert span.is_recording()
            span.set_attribute("processor.test", "multi_processor")
            span.add_event("test_event", {"event.type": "processor_test"})

            # Simulate some work to trigger processors
            time.sleep(0.01)
        # Cleanup handled by tracer_factory fixture

    def test_provider_strategy_with_decorator_integration(
        self,
        tracer_factory: Any,
    ) -> None:
        """Test that decorators work correctly with different provider strategies."""

        @trace(event_type="chain", event_name="provider_strategy_test")  # type: ignore[misc]
        def test_operation(strategy_type: str) -> str:
            """Test operation that uses decorators."""
            with tracer.start_span(f"nested_span_{strategy_type}") as span:
                span.set_attribute("strategy.type", strategy_type)
                span.set_attribute("decorator.integration", "true")
                return f"completed_{strategy_type}"

        # Test with MAIN_PROVIDER strategy
        noop_provider = NoOpTracerProvider()
        set_global_provider(noop_provider)

        tracer = tracer_factory("tracer")

        assert tracer.is_main_provider is True

        # Test decorator with main provider
        result1 = test_operation("main_provider")
        assert result1 == "completed_main_provider"
        # Cleanup handled by tracer_factory fixture
        # Test with independent provider strategy
        existing_provider = TracerProvider()
        # Add a processor to make it a "non-fresh" provider (has existing processors)
        console_exporter = ConsoleSpanExporter()
        existing_processor = SimpleSpanProcessor(console_exporter)
        existing_provider.add_span_processor(existing_processor)
        set_global_provider(existing_provider)

        tracer = tracer_factory("tracer")

        assert tracer.is_main_provider is False

        # Test decorator with independent provider
        result2 = test_operation("independent_provider")
        assert result2 == "completed_independent_provider"
        # Cleanup handled by tracer_factory fixture

    def test_provider_resource_management(
        self,
        tracer_factory: Any,
    ) -> None:
        """Test proper resource management across provider strategies."""
        # Test main provider resource management
        noop_provider = NoOpTracerProvider()
        set_global_provider(noop_provider)

        tracer1 = tracer_factory("tracer1")

        # Verify resources are properly initialized
        assert tracer1.provider is not None
        assert tracer1.tracer is not None
        assert tracer1.span_processor is not None

        # Test span creation and cleanup
        spans_created = []
        for i in range(5):
            with tracer1.start_span(f"resource_test_span_{i}") as span:
                spans_created.append(span)
                span.set_attribute("span.index", i)
                time.sleep(0.001)  # Small delay to simulate work

        # Verify all spans were created successfully
        assert len(spans_created) == 5
        for span in spans_created:
            assert span.is_recording() or span.get_span_context().is_valid

        # Test proper shutdown
        tracer1.shutdown()

        # Test secondary provider resource management
        existing_provider = TracerProvider()
        set_global_provider(existing_provider)

        tracer2 = tracer_factory("tracer2")

        # Verify resources are properly isolated (multi-instance architecture)
        assert tracer2.provider is not existing_provider  # Independent provider
        assert tracer2.tracer is not None

        # Test resource isolation doesn't interfere with functionality
        with tracer2.start_span("independent_resource_test") as span:
            assert span.is_recording()
            span.set_attribute("resource.isolation", "independent_provider")

        tracer2.shutdown()
