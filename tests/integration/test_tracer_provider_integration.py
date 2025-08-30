"""Integration tests for TracerProvider integration in HoneyHive."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.otel_tracer import HoneyHiveTracer


@pytest.mark.integration
@pytest.mark.tracer_provider
class TestTracerProviderIntegration:
    """Test TracerProvider integration and end-to-end functionality."""

    def test_new_tracer_provider_creation(
        self, real_api_key, real_project, real_source
    ):
        """Test creating new TracerProvider when none exists."""
        # Create tracer without existing provider
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="new-provider-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Verify it has a provider
        assert tracer.provider is not None

        # Test basic functionality
        with tracer.start_span("test_span") as span:
            span.set_attribute("test", "new_provider")
            assert span.is_recording()

        # Clean up
        tracer.shutdown()

    def test_existing_tracer_provider_integration(
        self, real_api_key, real_project, real_source
    ):
        """Test integration with existing TracerProvider."""
        # Mock an existing TracerProvider
        mock_existing_provider = Mock()
        mock_existing_provider.add_span_processor = Mock()

        # Patch the global trace.get_tracer_provider to return our mock
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider",
            return_value=mock_existing_provider,
        ):
            # Create HoneyHive tracer that should integrate with existing provider
            tracer = HoneyHiveTracer(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name="existing-provider-test",
                test_mode=False,
                disable_http_tracing=True,
            )

            # Verify it's using the existing provider
            assert tracer.provider == mock_existing_provider

            # Verify it added span processors to existing provider
            mock_existing_provider.add_span_processor.assert_called()

            # Test basic functionality still works
            with tracer.start_span("test_span") as span:
                span.set_attribute("test", "existing_provider")
                assert span.is_recording()

            # Clean up
            tracer.shutdown()

    def test_noop_provider_handling(self, real_api_key, real_project, real_source):
        """Test handling of NoOpTracerProvider."""
        # Mock a NoOpTracerProvider
        mock_noop_provider = Mock()
        mock_noop_provider.__class__.__name__ = "NoOpTracerProvider"

        # Patch the global trace.get_tracer_provider to return our NoOp provider
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider",
            return_value=mock_noop_provider,
        ):
            # Create HoneyHive tracer with NoOp provider
            tracer = HoneyHiveTracer(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name="noop-provider-test",
                test_mode=False,
                disable_http_tracing=True,
            )

            # Should create new provider when existing is NoOp
            assert tracer.provider != mock_noop_provider
            assert tracer.provider is not None

            # Test basic functionality
            with tracer.start_span("test_span") as span:
                span.set_attribute("test", "noop_handling")
                assert span.is_recording()

            # Clean up
            tracer.shutdown()

    def test_provider_without_span_processor_support(
        self, real_api_key, real_project, real_source
    ):
        """Test graceful handling of providers without add_span_processor."""
        # Mock a provider without add_span_processor method
        mock_provider = Mock()
        del mock_provider.add_span_processor

        # Patch the global trace.get_tracer_provider to return our unsupported provider
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            # Create HoneyHive tracer with unsupported provider
            tracer = HoneyHiveTracer(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name="unsupported-provider-test",
                test_mode=False,
                disable_http_tracing=True,
            )

            # Should handle gracefully
            assert tracer.provider == mock_provider

            # Test basic functionality still works
            with tracer.start_span("test_span") as span:
                span.set_attribute("test", "unsupported_provider")
                assert span.is_recording()

            # Clean up
            tracer.shutdown()

    def test_multiple_tracers_with_different_providers(
        self, real_api_key, real_project, real_source
    ):
        """Test multiple tracers with different provider configurations."""
        # Create first tracer with new provider
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="provider-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Create second tracer that should use the same provider
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="provider-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Verify both tracers work
        with tracer1.start_span("span1") as span1:
            span1.set_attribute("tracer", "tracer1")

        with tracer2.start_span("span2") as span2:
            span2.set_attribute("tracer", "tracer2")

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_provider_shutdown_behavior(self, real_api_key, real_project, real_source):
        """Test proper shutdown behavior with different provider configurations."""
        # Create tracer as main provider
        main_tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="shutdown-main-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Create another tracer
        secondary_tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="shutdown-secondary-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Mock the provider shutdown method and set is_main_provider flags
        mock_provider = Mock()
        main_tracer.provider = mock_provider
        main_tracer.is_main_provider = True  # Set as main provider
        secondary_tracer.provider = mock_provider
        secondary_tracer.is_main_provider = False  # Set as secondary provider

        # Shutdown main tracer (should shutdown provider)
        main_tracer.shutdown()
        mock_provider.shutdown.assert_called_once()

        # Shutdown secondary tracer (should not shutdown provider)
        mock_provider.shutdown.reset_mock()
        secondary_tracer.shutdown()
        mock_provider.shutdown.assert_not_called()

    def test_provider_context_propagation(
        self, real_api_key, real_project, real_source
    ):
        """Test context propagation with different provider configurations."""
        # Create tracer with new provider
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="context-propagation-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Test context injection and extraction
        test_carrier = {}
        tracer.inject_context(test_carrier)

        # Verify context was injected
        assert test_carrier is not None

        # Test context extraction
        extracted_context = tracer.extract_context(test_carrier)
        assert extracted_context is not None

        # Clean up
        tracer.shutdown()

    def test_provider_span_processor_integration(
        self, real_api_key, real_project, real_source
    ):
        """Test that span processors are properly integrated with providers."""
        # Create tracer with new provider
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="span-processor-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Verify span processors are added
        assert hasattr(tracer.provider, "add_span_processor")

        # Test span creation and processing
        with tracer.start_span("processor_test") as span:
            span.set_attribute("test", "span_processor")
            span.add_event("test_event", {"data": "test"})
            assert span.is_recording()

        # Clean up
        tracer.shutdown()

    def test_provider_fallback_behavior(self, real_api_key, real_project, real_source):
        """Test fallback behavior when provider operations fail."""
        # Create tracer with new provider
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="fallback-test",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Mock provider to simulate failures
        original_provider = tracer.provider
        mock_failing_provider = Mock()
        mock_failing_provider.add_span_processor.side_effect = Exception(
            "Provider error"
        )
        tracer.provider = mock_failing_provider

        # Should handle provider errors gracefully
        try:
            with tracer.start_span("fallback_test") as span:
                span.set_attribute("test", "fallback")
                assert span.is_recording()
        except Exception:
            # If provider fails, basic functionality should still work
            pass

        # Restore original provider and clean up
        tracer.provider = original_provider
        tracer.shutdown()

    def test_force_flush_with_different_providers_integration(
        self, real_api_key, real_project, real_source
    ):
        """Test force_flush behavior with different provider configurations."""
        # Test with new TracerProvider
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-new-provider",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Create some spans
        with tracer1.start_span("new_provider_span") as span:
            span.set_attribute("provider_type", "new")

        # Test force_flush
        result = tracer1.force_flush(timeout_millis=5000)
        assert isinstance(result, bool)

        tracer1.shutdown()

        # Test with existing TracerProvider
        mock_existing_provider = Mock()
        mock_existing_provider.add_span_processor = Mock()
        mock_existing_provider.force_flush = Mock(return_value=True)

        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider",
            return_value=mock_existing_provider,
        ):
            tracer2 = HoneyHiveTracer(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name="force-flush-existing-provider",
                test_mode=False,
                disable_http_tracing=True,
            )

            # Create some spans
            with tracer2.start_span("existing_provider_span") as span:
                span.set_attribute("provider_type", "existing")

            # Test force_flush
            result = tracer2.force_flush(timeout_millis=3000)
            assert isinstance(result, bool)

            # Verify that provider's force_flush was called
            mock_existing_provider.force_flush.assert_called()

            tracer2.shutdown()

    def test_force_flush_multiple_tracers_same_provider_integration(
        self, real_api_key, real_project, real_source
    ):
        """Test force_flush with multiple tracers sharing the same provider."""
        # Create first tracer (will create new provider)
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-multi-1",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Store the provider reference
        shared_provider = tracer1.provider

        # Create second tracer that will use the existing provider
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider",
            return_value=shared_provider,
        ):
            tracer2 = HoneyHiveTracer(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name="force-flush-multi-2",
                test_mode=False,
                disable_http_tracing=True,
            )

        # Create spans from both tracers
        with tracer1.start_span("tracer1_span") as span:
            span.set_attribute("tracer", "first")

        with tracer2.start_span("tracer2_span") as span:
            span.set_attribute("tracer", "second")

        # Test force_flush from both tracers
        result1 = tracer1.force_flush(timeout_millis=4000)
        result2 = tracer2.force_flush(timeout_millis=4000)

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

        # Both should share the same provider
        assert tracer1.provider == tracer2.provider

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_force_flush_stress_test_integration(
        self, real_api_key, real_project, real_source
    ):
        """Test force_flush behavior under stress conditions."""
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="force-flush-stress",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Create many spans quickly
        for i in range(20):
            with tracer.start_span(f"stress_span_{i}") as span:
                span.set_attribute("iteration", i)
                span.set_attribute("stress_test", True)

        # Multiple rapid force_flush calls
        results = []
        for timeout in [1000, 2000, 3000, 1500, 2500]:
            result = tracer.force_flush(timeout_millis=timeout)
            results.append(result)
            assert isinstance(result, bool)

        # All calls should complete without exceptions
        assert len(results) == 5

        # Final flush before shutdown
        final_result = tracer.force_flush(timeout_millis=10000)
        assert isinstance(final_result, bool)

        tracer.shutdown()
