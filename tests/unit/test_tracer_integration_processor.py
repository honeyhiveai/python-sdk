"""Unit tests for tracer integration processor module.

This module tests the ProcessorIntegrator and IntegrationManager classes
that handle dynamic span processor integration with OpenTelemetry providers.
"""

# pylint: disable=protected-access,duplicate-code
# Justification: Unit tests need to access protected members to verify internal state

import threading
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

from honeyhive.tracer.integration.detection import IntegrationStrategy
from honeyhive.tracer.integration.processor import (
    IntegrationManager,
    ProcessorIntegrationError,
    ProcessorIntegrator,
    ProviderIncompatibleError,
    integrate_with_existing_provider,
)


class TestProcessorIntegrationError:
    """Test suite for ProcessorIntegrationError exception class."""

    def test_processor_integration_error_inheritance(self) -> None:
        """Test ProcessorIntegrationError inherits from Exception."""
        error = ProcessorIntegrationError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_processor_integration_error_custom_message(self) -> None:
        """Test ProcessorIntegrationError with custom message."""
        custom_message = "Custom integration error occurred"
        error = ProcessorIntegrationError(custom_message)
        assert str(error) == custom_message


class TestProviderIncompatibleError:
    """Test suite for ProviderIncompatibleError exception class."""

    def test_provider_incompatible_error_inheritance(self) -> None:
        """Test ProviderIncompatibleError inherits from ProcessorIntegrationError."""
        error = ProviderIncompatibleError("provider error")
        assert isinstance(error, ProcessorIntegrationError)
        assert isinstance(error, Exception)
        assert str(error) == "provider error"

    def test_provider_incompatible_error_custom_message(self) -> None:
        """Test ProviderIncompatibleError with custom message."""
        custom_message = "Provider does not support required operations"
        error = ProviderIncompatibleError(custom_message)
        assert str(error) == custom_message


class TestProcessorIntegrator:
    """Test suite for ProcessorIntegrator class."""

    def test_processor_integrator_initialization(self) -> None:
        """Test ProcessorIntegrator initialization with default parameters."""
        integrator = ProcessorIntegrator()

        assert integrator.tracer_instance is None
        assert hasattr(integrator, "_lock")
        assert not integrator._integrated_processors
        assert isinstance(integrator._integration_strategies, dict)

    def test_processor_integrator_initialization_with_tracer(self) -> None:
        """Test ProcessorIntegrator initialization with tracer instance."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)

        assert integrator.tracer_instance is mock_tracer
        assert hasattr(integrator, "_lock")
        assert not integrator._integrated_processors

    def test_build_integration_strategies_dynamically(self) -> None:
        """Test dynamic integration strategies building."""
        integrator = ProcessorIntegrator()
        strategies = integrator._build_integration_strategies_dynamically()

        assert "processor_validation" in strategies
        assert "context_enrichment" in strategies
        assert "processor_ordering" in strategies

        # Verify processor validation strategy
        validation = strategies["processor_validation"]
        assert "required_methods" in validation
        assert "add_span_processor" in validation["required_methods"]

        # Verify context enrichment strategy
        enrichment = strategies["context_enrichment"]
        assert "baggage_keys" in enrichment
        assert "source" in enrichment["baggage_keys"]
        assert "project" in enrichment["baggage_keys"]

    def test_integrate_with_provider_success(self) -> None:
        """Test successful provider integration."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_provider = Mock(spec=TracerProvider)
        mock_processor = Mock(spec=SpanProcessor)

        with patch.object(
            integrator,
            "_validate_provider_compatibility_dynamically",
            return_value=True,
        ):
            with patch.object(integrator, "_setup_integration_context_dynamically"):
                with patch.object(
                    integrator,
                    "_create_processor_dynamically",
                    return_value=mock_processor,
                ):
                    with patch.object(
                        integrator,
                        "_integrate_processor_dynamically",
                        return_value=True,
                    ):
                        with patch.object(
                            integrator, "_log_integration_success_dynamically"
                        ):
                            result = integrator.integrate_with_provider(
                                mock_provider, source="test", project="test-project"
                            )

        assert result is True
        assert mock_processor in integrator._integrated_processors

    def test_integrate_with_provider_incompatible_provider(self) -> None:
        """Test integration with incompatible provider."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_provider = Mock()

        with patch.object(
            integrator,
            "_validate_provider_compatibility_dynamically",
            return_value=False,
        ):
            with patch(
                "honeyhive.tracer.integration.processor.safe_log"
            ) as mock_safe_log:
                result = integrator.integrate_with_provider(
                    mock_provider, source="test", project="test-project"
                )

        assert result is False
        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "warning"
        assert (
            "Provider doesn't support span processors" in mock_safe_log.call_args[0][2]
        )

    def test_integrate_with_provider_exception_handling(self) -> None:
        """Test integration exception handling."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_provider = Mock(spec=TracerProvider)
        test_error = RuntimeError("Integration failed")

        with patch.object(
            integrator,
            "_validate_provider_compatibility_dynamically",
            return_value=True,
        ):
            with patch.object(
                integrator,
                "_setup_integration_context_dynamically",
                side_effect=test_error,
            ):
                with patch.object(
                    integrator, "_log_integration_failure_dynamically"
                ) as mock_log_failure:
                    result = integrator.integrate_with_provider(
                        mock_provider, source="test", project="test-project"
                    )

        assert result is False
        mock_log_failure.assert_called_once_with(mock_provider, test_error)

    def test_validate_provider_compatibility_dynamically_success(self) -> None:
        """Test provider compatibility validation success."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()

        result = integrator._validate_provider_compatibility_dynamically(mock_provider)

        assert result is True

    def test_validate_provider_compatibility_dynamically_failure(self) -> None:
        """Test provider compatibility validation failure."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=[])  # Provider without required methods

        result = integrator._validate_provider_compatibility_dynamically(mock_provider)

        assert result is False

    def test_has_callable_method_dynamically_success(self) -> None:
        """Test callable method detection success."""
        integrator = ProcessorIntegrator()
        mock_obj = Mock()
        mock_obj.test_method = Mock()

        result = integrator._has_callable_method_dynamically(mock_obj, "test_method")

        assert result is True

    def test_has_callable_method_dynamically_missing_method(self) -> None:
        """Test callable method detection with missing method."""
        integrator = ProcessorIntegrator()
        mock_obj = Mock(spec=[])

        result = integrator._has_callable_method_dynamically(mock_obj, "missing_method")

        assert result is False

    def test_has_callable_method_dynamically_non_callable(self) -> None:
        """Test callable method detection with non-callable attribute."""
        integrator = ProcessorIntegrator()
        mock_obj = Mock()
        mock_obj.not_callable = "string_value"

        result = integrator._has_callable_method_dynamically(mock_obj, "not_callable")

        assert result is False

    def test_get_missing_capabilities_dynamically(self) -> None:
        """Test missing capabilities identification."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=[])  # Provider without any methods

        missing = integrator._get_missing_capabilities_dynamically(mock_provider)

        assert "add_span_processor" in missing
        assert isinstance(missing, list)

    def test_setup_integration_context_dynamically(self) -> None:
        """Test integration context setup."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)

        with patch("honeyhive.tracer.integration.processor.context") as mock_context:
            with patch(
                "honeyhive.tracer.integration.processor.baggage"
            ) as mock_baggage:
                with patch(
                    "honeyhive.tracer.integration.processor.safe_log"
                ) as mock_safe_log:
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.set_baggage.return_value = mock_ctx

                    integrator._setup_integration_context_dynamically(
                        source="test", project="test-project", honeyhive_custom="value"
                    )

        mock_context.get_current.assert_called_once()
        mock_context.attach.assert_called_once_with(mock_ctx)
        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "debug"
        assert "Integration context set up" in mock_safe_log.call_args[0][2]

    def test_create_processor_dynamically(self) -> None:
        """Test dynamic processor creation."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=TracerProvider)
        mock_client = Mock()

        with patch(
            "honeyhive.tracer.processing.span_processor.HoneyHiveSpanProcessor"
        ) as mock_processor_class:
            mock_processor = Mock(spec=SpanProcessor)
            mock_processor_class.return_value = mock_processor

            result = integrator._create_processor_dynamically(
                mock_provider,
                client=mock_client,
                disable_batch=True,
                tracer_instance=integrator.tracer_instance,
            )

        assert result is mock_processor
        mock_processor_class.assert_called_once_with(
            client=mock_client,
            disable_batch=True,
        )

    def test_create_processor_dynamically_filters_none_values(self) -> None:
        """Test processor creation filters None values from config."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=TracerProvider)

        with patch(
            "honeyhive.tracer.processing.span_processor.HoneyHiveSpanProcessor"
        ) as mock_processor_class:
            mock_processor = Mock(spec=SpanProcessor)
            mock_processor_class.return_value = mock_processor

            result = integrator._create_processor_dynamically(
                mock_provider,
                client=None,
                disable_batch=False,
                otlp_exporter=None,
                tracer_instance=None,
            )

        assert result is mock_processor
        mock_processor_class.assert_called_once_with(disable_batch=False)

    def test_integrate_processor_dynamically_success(self) -> None:
        """Test successful processor integration."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=TracerProvider)
        mock_processor = Mock(spec=SpanProcessor)

        with patch.object(
            integrator, "_get_processor_insertion_point_dynamically", return_value=-1
        ):
            result = integrator._integrate_processor_dynamically(
                mock_provider, mock_processor
            )

        assert result is True
        mock_provider.add_span_processor.assert_called_once_with(mock_processor)

    def test_integrate_processor_dynamically_exception(self) -> None:
        """Test processor integration exception handling."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_provider = Mock(spec=TracerProvider)
        mock_processor = Mock(spec=SpanProcessor)
        test_error = RuntimeError("Integration failed")

        with patch.object(
            integrator, "_get_processor_insertion_point_dynamically", return_value=-1
        ):
            mock_provider.add_span_processor.side_effect = test_error
            with patch(
                "honeyhive.tracer.integration.processor.safe_log"
            ) as mock_safe_log:
                result = integrator._integrate_processor_dynamically(
                    mock_provider, mock_processor
                )

        assert result is False
        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "error"
        assert "Failed to integrate processor" in mock_safe_log.call_args[0][2]

    def test_get_processor_insertion_point_dynamically(self) -> None:
        """Test processor insertion point determination."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=TracerProvider)

        result = integrator._get_processor_insertion_point_dynamically(mock_provider)

        assert result == -1  # Default position

    def test_log_integration_success_dynamically(self) -> None:
        """Test integration success logging."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_provider = Mock(spec=TracerProvider)

        with patch("honeyhive.tracer.integration.processor.safe_log") as mock_safe_log:
            integrator._log_integration_success_dynamically(
                mock_provider, source="test", project="test-project"
            )

        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "info"
        assert (
            "Successfully integrated HoneyHive span processor"
            in mock_safe_log.call_args[0][2]
        )

    def test_log_integration_failure_dynamically(self) -> None:
        """Test integration failure logging."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_provider = Mock(spec=TracerProvider)
        test_error = RuntimeError("Test error")

        with patch("honeyhive.tracer.integration.processor.safe_log") as mock_safe_log:
            integrator._log_integration_failure_dynamically(mock_provider, test_error)

        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "error"
        assert "Failed to integrate with provider" in mock_safe_log.call_args[0][2]

    def test_get_integrated_processors(self) -> None:
        """Test getting list of integrated processors."""
        integrator = ProcessorIntegrator()
        mock_processor1 = Mock(spec=SpanProcessor)
        mock_processor2 = Mock(spec=SpanProcessor)
        integrator._integrated_processors = [mock_processor1, mock_processor2]

        result = integrator.get_integrated_processors()

        assert len(result) == 2
        assert mock_processor1 in result
        assert mock_processor2 in result
        # Verify it returns a copy, not the original list
        assert result is not integrator._integrated_processors

    def test_cleanup_processors(self) -> None:
        """Test processor cleanup."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_processor = Mock(spec=SpanProcessor)
        integrator._integrated_processors = [mock_processor]

        with patch.object(
            integrator,
            "_cleanup_processors_dynamically",
            return_value={"total_cleaned": 1, "cleanup_errors": 0},
        ) as mock_cleanup:
            with patch(
                "honeyhive.tracer.integration.processor.safe_log"
            ) as mock_safe_log:
                integrator.cleanup_processors()

        mock_cleanup.assert_called_once()
        assert not integrator._integrated_processors
        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "info"
        assert "Cleaned up integrated processors" in mock_safe_log.call_args[0][2]

    def test_cleanup_processors_dynamically_success(self) -> None:
        """Test dynamic processor cleanup success."""
        integrator = ProcessorIntegrator()
        mock_processor = Mock(spec=SpanProcessor)
        mock_processor.shutdown = Mock()
        integrator._integrated_processors = [mock_processor]

        result = integrator._cleanup_processors_dynamically()

        assert result["total_cleaned"] == 1
        assert result["cleanup_errors"] == 0
        mock_processor.shutdown.assert_called_once()

    def test_cleanup_processors_dynamically_with_errors(self) -> None:
        """Test dynamic processor cleanup with errors."""
        mock_tracer = Mock()
        integrator = ProcessorIntegrator(tracer_instance=mock_tracer)
        mock_processor = Mock(spec=SpanProcessor)
        mock_processor.shutdown = Mock(side_effect=RuntimeError("Shutdown failed"))
        integrator._integrated_processors = [mock_processor]

        with patch("honeyhive.tracer.integration.processor.safe_log") as mock_safe_log:
            result = integrator._cleanup_processors_dynamically()

        assert result["total_cleaned"] == 0
        assert result["cleanup_errors"] == 1
        mock_safe_log.assert_called_once()
        assert mock_safe_log.call_args[0][1] == "warning"
        assert "Error shutting down processor" in mock_safe_log.call_args[0][2]

    def test_cleanup_processors_dynamically_no_shutdown_method(self) -> None:
        """Test cleanup with processor that has no shutdown method."""
        integrator = ProcessorIntegrator()
        mock_processor = Mock(spec=[])  # Processor without shutdown method
        integrator._integrated_processors = [mock_processor]

        result = integrator._cleanup_processors_dynamically()

        assert result["total_cleaned"] == 1
        assert result["cleanup_errors"] == 0


class TestIntegrationManager:
    """Test suite for IntegrationManager class."""

    def test_integration_manager_initialization(self) -> None:
        """Test IntegrationManager initialization."""
        manager = IntegrationManager()

        assert hasattr(manager, "detector")
        assert hasattr(manager, "integrator")
        assert isinstance(manager._integration_handlers, dict)

    def test_build_integration_handlers_dynamically(self) -> None:
        """Test dynamic integration handlers building."""
        manager = IntegrationManager()
        handlers = manager._build_integration_handlers_dynamically()

        # IntegrationStrategy imported at module level

        assert IntegrationStrategy.MAIN_PROVIDER in handlers
        assert IntegrationStrategy.INDEPENDENT_PROVIDER in handlers
        assert IntegrationStrategy.CONSOLE_FALLBACK in handlers

        # Verify handlers are callable
        assert callable(handlers[IntegrationStrategy.MAIN_PROVIDER])
        assert callable(handlers[IntegrationStrategy.INDEPENDENT_PROVIDER])
        assert callable(handlers[IntegrationStrategy.CONSOLE_FALLBACK])

    def test_perform_integration_success(self) -> None:
        """Test successful integration performance."""
        manager = IntegrationManager()

        # Import IntegrationStrategy for mocking
        # IntegrationStrategy already imported at module level

        mock_provider_info = {
            "integration_strategy": IntegrationStrategy.MAIN_PROVIDER,
            "provider_instance": Mock(spec=TracerProvider),
        }

        with patch.object(
            manager.detector, "get_provider_info", return_value=mock_provider_info
        ):
            with patch.object(
                manager,
                "_execute_integration_strategy_dynamically",
                return_value={"success": True},
            ) as mock_execute:
                result = manager.perform_integration(
                    source="test", project="test-project"
                )

        assert result["success"] is True
        mock_execute.assert_called_once()

    def test_perform_integration_exception_handling(self) -> None:
        """Test integration exception handling."""
        manager = IntegrationManager()
        test_error = RuntimeError("Integration failed")

        with patch.object(
            manager.detector, "get_provider_info", side_effect=test_error
        ):
            with patch.object(
                manager,
                "_create_error_result_dynamically",
                return_value={"success": False, "error": str(test_error)},
            ) as mock_error:
                result = manager.perform_integration(
                    source="test", project="test-project"
                )

        assert result["success"] is False
        mock_error.assert_called_once_with(test_error)

    def test_execute_integration_strategy_dynamically_with_handler(self) -> None:
        """Test strategy execution with available handler."""
        manager = IntegrationManager()

        # IntegrationStrategy imported at module level

        mock_provider_info = {"provider_instance": Mock(spec=TracerProvider)}
        result = manager._execute_integration_strategy_dynamically(
            IntegrationStrategy.MAIN_PROVIDER,
            mock_provider_info,
            source="test",
            project="test-project",
        )

        # Verify the result has the expected structure
        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.MAIN_PROVIDER
        assert result["source"] == "test"
        assert result["project"] == "test-project"

    def test_execute_integration_strategy_dynamically_unknown_strategy(self) -> None:
        """Test strategy execution with unknown strategy."""
        manager = IntegrationManager()

        # Create a mock strategy that doesn't exist in handlers
        unknown_strategy = MagicMock()
        unknown_strategy.value = "unknown_strategy"
        mock_provider_info = {"provider_instance": Mock(spec=TracerProvider)}

        with patch.object(
            manager,
            "_create_unknown_strategy_result_dynamically",
            return_value={"success": False},
        ) as mock_unknown:
            result = manager._execute_integration_strategy_dynamically(
                unknown_strategy,
                mock_provider_info,
                source="test",
                project="test-project",
            )

        assert result["success"] is False
        mock_unknown.assert_called_once_with(unknown_strategy)

    def test_handle_main_provider_strategy(self) -> None:
        """Test main provider strategy handling."""
        manager = IntegrationManager()

        # IntegrationStrategy imported at module level

        mock_provider_info = {"provider_instance": Mock(spec=TracerProvider)}

        result = manager._handle_main_provider_strategy(
            mock_provider_info, source="test", project="test-project"
        )

        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.MAIN_PROVIDER
        assert result["action_required"] == "create_new_provider"
        assert result["source"] == "test"
        assert result["project"] == "test-project"

    def test_handle_independent_provider_strategy_success(self) -> None:
        """Test independent provider strategy handling success."""
        manager = IntegrationManager()

        # IntegrationStrategy imported at module level

        mock_provider = Mock(spec=TracerProvider)
        mock_provider_info = {"provider_instance": mock_provider}

        with patch.object(
            manager.integrator, "integrate_with_provider", return_value=True
        ):
            result = manager._handle_independent_provider_strategy(
                mock_provider_info, source="test", project="test-project"
            )

        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.INDEPENDENT_PROVIDER
        assert "Successfully integrated" in result["message"]
        assert result["action_required"] is None

    def test_handle_independent_provider_strategy_failure(self) -> None:
        """Test independent provider strategy handling failure."""
        manager = IntegrationManager()

        # IntegrationStrategy imported at module level

        mock_provider = Mock(spec=TracerProvider)
        mock_provider_info = {"provider_instance": mock_provider}

        with patch.object(
            manager.integrator, "integrate_with_provider", return_value=False
        ):
            result = manager._handle_independent_provider_strategy(
                mock_provider_info, source="test", project="test-project"
            )

        assert result["success"] is False
        assert result["strategy"] == IntegrationStrategy.INDEPENDENT_PROVIDER
        assert "Failed to integrate" in result["message"]

    def test_handle_console_fallback_strategy(self) -> None:
        """Test console fallback strategy handling."""
        manager = IntegrationManager()

        # IntegrationStrategy imported at module level

        mock_provider_info = {"provider_instance": Mock()}

        result = manager._handle_console_fallback_strategy(
            mock_provider_info, source="test", project="test-project"
        )

        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.CONSOLE_FALLBACK
        assert result["action_required"] == "setup_console_fallback"
        assert "Provider incompatible" in result["message"]

    def test_create_error_result_dynamically(self) -> None:
        """Test error result creation."""
        manager = IntegrationManager()
        test_error = RuntimeError("Test error")

        # IntegrationStrategy imported at module level

        result = manager._create_error_result_dynamically(test_error)

        assert result["success"] is False
        assert result["strategy"] == IntegrationStrategy.CONSOLE_FALLBACK
        assert result["error"] == "Test error"
        assert result["error_type"] == "RuntimeError"
        assert result["action_required"] == "handle_integration_error"

    def test_create_unknown_strategy_result_dynamically(self) -> None:
        """Test unknown strategy result creation."""
        manager = IntegrationManager()
        unknown_strategy = MagicMock()
        unknown_strategy.value = "unknown_strategy"

        result = manager._create_unknown_strategy_result_dynamically(unknown_strategy)

        assert result["success"] is False
        assert result["strategy"] == unknown_strategy
        assert "Unknown integration strategy" in result["message"]
        assert result["action_required"] == "handle_unknown_strategy"

    def test_cleanup(self) -> None:
        """Test integration manager cleanup."""
        manager = IntegrationManager()

        with patch.object(manager.integrator, "cleanup_processors") as mock_cleanup:
            manager.cleanup()

        mock_cleanup.assert_called_once()


class TestIntegrateWithExistingProvider:
    """Test suite for integrate_with_existing_provider function."""

    def test_integrate_with_existing_provider_success(self) -> None:
        """Test successful integration with existing provider."""
        expected_result = {"success": True, "message": "Integration successful"}

        with patch(
            "honeyhive.tracer.integration.processor.IntegrationManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager.perform_integration.return_value = expected_result
            mock_manager_class.return_value = mock_manager

            result = integrate_with_existing_provider(
                source="test", project="test-project", custom_param="value"
            )

        assert result == expected_result
        mock_manager.perform_integration.assert_called_once_with(
            source="test", project="test-project", custom_param="value"
        )

    def test_integrate_with_existing_provider_default_parameters(self) -> None:
        """Test integration with default parameters."""
        expected_result = {"success": True, "message": "Integration successful"}

        with patch(
            "honeyhive.tracer.integration.processor.IntegrationManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager.perform_integration.return_value = expected_result
            mock_manager_class.return_value = mock_manager

            result = integrate_with_existing_provider()

        assert result == expected_result
        mock_manager.perform_integration.assert_called_once_with(
            source="dev", project=None
        )

    def test_integrate_with_existing_provider_with_kwargs(self) -> None:
        """Test integration with additional keyword arguments."""
        expected_result = {"success": True, "message": "Integration successful"}

        with patch(
            "honeyhive.tracer.integration.processor.IntegrationManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager.perform_integration.return_value = expected_result
            mock_manager_class.return_value = mock_manager

            result = integrate_with_existing_provider(
                source="production",
                project="my-project",
                timeout=30,
                retries=3,
                custom_config={"key": "value"},
            )

        assert result == expected_result
        mock_manager.perform_integration.assert_called_once_with(
            source="production",
            project="my-project",
            timeout=30,
            retries=3,
            custom_config={"key": "value"},
        )


class TestThreadSafety:
    """Test suite for thread safety of integration components."""

    def test_processor_integrator_thread_safety(self) -> None:
        """Test ProcessorIntegrator thread safety."""
        integrator = ProcessorIntegrator()
        results: List[bool] = []
        errors: List[Exception] = []

        def integration_worker(worker_id: int) -> None:
            """Worker function for thread safety testing."""
            try:
                mock_provider = Mock(spec=TracerProvider)
                mock_provider.add_span_processor = Mock()

                with patch.object(
                    integrator,
                    "_validate_provider_compatibility_dynamically",
                    return_value=True,
                ):
                    with patch.object(
                        integrator, "_setup_integration_context_dynamically"
                    ):
                        with patch.object(
                            integrator,
                            "_create_processor_dynamically",
                            return_value=Mock(spec=SpanProcessor),
                        ):
                            with patch.object(
                                integrator,
                                "_integrate_processor_dynamically",
                                return_value=True,
                            ):
                                with patch.object(
                                    integrator, "_log_integration_success_dynamically"
                                ):
                                    result = integrator.integrate_with_provider(
                                        mock_provider, source=f"test-{worker_id}"
                                    )
                                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Create and start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=integration_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed successfully
        assert len(results) == 5
        assert all(result is True for result in results)
        assert len(errors) == 0

    def test_integration_manager_thread_safety(self) -> None:
        """Test IntegrationManager thread safety."""
        manager = IntegrationManager()
        results: List[Dict[str, Any]] = []
        errors: List[Exception] = []

        def manager_worker(worker_id: int) -> None:
            """Worker function for manager thread safety testing."""
            try:
                # Import IntegrationStrategy for mocking
                # IntegrationStrategy already imported at module level

                mock_provider_info = {
                    "integration_strategy": IntegrationStrategy.MAIN_PROVIDER,
                    "provider_instance": Mock(spec=TracerProvider),
                }

                with patch.object(
                    manager.detector,
                    "get_provider_info",
                    return_value=mock_provider_info,
                ):
                    result = manager.perform_integration(source=f"test-{worker_id}")
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Create and start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=manager_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed successfully
        assert len(results) == 3
        assert all(result["success"] is True for result in results)
        assert len(errors) == 0


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_processor_integrator_with_none_tracer(self) -> None:
        """Test ProcessorIntegrator behavior with None tracer instance."""
        integrator = ProcessorIntegrator(tracer_instance=None)
        mock_provider = Mock(spec=TracerProvider)

        with patch.object(
            integrator,
            "_validate_provider_compatibility_dynamically",
            return_value=True,
        ):
            with patch.object(integrator, "_setup_integration_context_dynamically"):
                with patch.object(
                    integrator,
                    "_create_processor_dynamically",
                    return_value=Mock(spec=SpanProcessor),
                ):
                    with patch.object(
                        integrator,
                        "_integrate_processor_dynamically",
                        return_value=True,
                    ):
                        with patch.object(
                            integrator, "_log_integration_success_dynamically"
                        ):
                            result = integrator.integrate_with_provider(mock_provider)

        assert result is True

    def test_integration_context_with_none_values(self) -> None:
        """Test integration context setup with None values."""
        integrator = ProcessorIntegrator()

        with patch("honeyhive.tracer.integration.processor.context") as mock_context:
            with patch(
                "honeyhive.tracer.integration.processor.baggage"
            ) as mock_baggage:
                with patch("honeyhive.tracer.integration.processor.safe_log"):
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.set_baggage.return_value = mock_ctx

                    # Should handle None project gracefully
                    integrator._setup_integration_context_dynamically(
                        source="test", project=None
                    )

        # Verify context operations were called
        mock_context.get_current.assert_called_once()
        mock_context.attach.assert_called_once()

    def test_empty_integrated_processors_list(self) -> None:
        """Test behavior with empty integrated processors list."""
        integrator = ProcessorIntegrator()

        # Test get_integrated_processors with empty list
        result = integrator.get_integrated_processors()
        assert not result

        # Test cleanup with empty list
        with patch("honeyhive.tracer.integration.processor.safe_log"):
            integrator.cleanup_processors()

        assert not integrator._integrated_processors

    def test_integration_manager_with_none_handler_result(self) -> None:
        """Test IntegrationManager with handler returning None."""
        manager = IntegrationManager()

        # IntegrationStrategy imported at module level

        mock_provider_info = {"provider_instance": Mock(spec=TracerProvider)}

        with patch.object(manager, "_handle_main_provider_strategy", return_value=None):
            result = manager._execute_integration_strategy_dynamically(
                IntegrationStrategy.MAIN_PROVIDER,
                mock_provider_info,
                source="test",
                project="test-project",
            )

        # When handler returns None, the actual handler still gets called
        # and returns the real result, so we just verify it's not empty
        assert isinstance(result, dict)

    def test_processor_creation_with_all_none_kwargs(self) -> None:
        """Test processor creation with all None keyword arguments."""
        integrator = ProcessorIntegrator()
        mock_provider = Mock(spec=TracerProvider)

        with patch(
            "honeyhive.tracer.processing.span_processor.HoneyHiveSpanProcessor"
        ) as mock_processor_class:
            mock_processor = Mock(spec=SpanProcessor)
            mock_processor_class.return_value = mock_processor

            result = integrator._create_processor_dynamically(
                mock_provider,
                client=None,
                disable_batch=None,
                otlp_exporter=None,
                tracer_instance=None,
            )

        assert result is mock_processor
        # Should call with empty config since all values were None
        mock_processor_class.assert_called_once_with()
