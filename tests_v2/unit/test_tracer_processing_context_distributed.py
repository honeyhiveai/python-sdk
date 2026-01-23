"""Unit tests for distributed tracing context helper.

This module tests the with_distributed_trace_context() context manager
for server-side distributed tracing.
"""

# pylint: disable=C0301,W0611
# Justification: line-too-long: Complex context propagation assertions; unused-import: Test imports
from typing import Dict
from unittest.mock import Mock, patch

import pytest
from opentelemetry import baggage, context

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.processing.context import with_distributed_trace_context


class TestWithDistributedTraceContext:
    """Test suite for with_distributed_trace_context() helper."""

    def test_extracts_session_id_from_baggage_header(self) -> None:
        """Test that session_id is extracted from baggage header."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier = {
            "baggage": "session_id=test-session-123",
            "traceparent": "00-123456789abcdef0-0123456789abcdef-01",
        }

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            # Mock extracted context
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                with with_distributed_trace_context(carrier, mock_tracer):
                    pass

                # Verify session_id was set in baggage
                calls = [str(call) for call in mock_set_baggage.call_args_list]
                assert any(
                    "session_id" in call and "test-session-123" in call
                    for call in calls
                )

    def test_extracts_project_and_source_from_baggage_header(self) -> None:
        """Test that project and source are extracted from baggage header."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier = {
            "baggage": (
                "session_id=test-session-123," "project=test-project,source=test-source"
            ),
            "traceparent": "00-123456789abcdef0-0123456789abcdef-01",
        }

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                with with_distributed_trace_context(carrier, mock_tracer):
                    pass

                # Verify all three were set
                calls = [str(call) for call in mock_set_baggage.call_args_list]
                assert any(
                    "session_id" in call and "test-session-123" in call
                    for call in calls
                )
                assert any(
                    "project" in call and "test-project" in call for call in calls
                )
                assert any("source" in call and "test-source" in call for call in calls)

    def test_handles_honeyhive_prefix_variants(self) -> None:
        """Test that various baggage key prefixes are handled."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        # Test honeyhive_session_id variant
        carrier = {
            "baggage": (
                "honeyhive_session_id=test-session-123,"
                "honeyhive_project=test-project,"
                "honeyhive_source=test-source"
            ),
        }

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                with with_distributed_trace_context(carrier, mock_tracer):
                    pass

                # Verify extraction worked with prefix
                calls = [str(call) for call in mock_set_baggage.call_args_list]
                assert any(
                    "session_id" in call and "test-session-123" in call
                    for call in calls
                )

    def test_explicit_session_id_overrides_baggage(self) -> None:
        """Test that explicit session_id parameter takes precedence."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier = {
            "baggage": "session_id=baggage-session-123",
        }

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                # Pass explicit session_id
                with with_distributed_trace_context(
                    carrier, mock_tracer, session_id="explicit-session-456"
                ):
                    pass

                # Verify explicit session_id was used
                calls = [str(call) for call in mock_set_baggage.call_args_list]
                assert any(
                    "session_id" in call and "explicit-session-456" in call
                    for call in calls
                )
                assert not any("baggage-session-123" in call for call in calls)

    def test_context_attached_and_detached(self) -> None:
        """Test that context is properly attached and detached."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier = {"baggage": "session_id=test-session-123"}

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                with patch(
                    "honeyhive.tracer.processing.context.context.attach"
                ) as mock_attach:
                    with patch(
                        "honeyhive.tracer.processing.context.context.detach"
                    ) as mock_detach:
                        mock_token = Mock()
                        mock_attach.return_value = mock_token

                        with with_distributed_trace_context(carrier, mock_tracer):
                            # Context should be attached here
                            mock_attach.assert_called_once()

                        # Context should be detached after exiting
                        mock_detach.assert_called_once_with(mock_token)

    def test_context_detached_even_on_exception(self) -> None:
        """Test that context is detached even if exception occurs."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier = {"baggage": "session_id=test-session-123"}

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                with patch(
                    "honeyhive.tracer.processing.context.context.attach"
                ) as mock_attach:
                    with patch(
                        "honeyhive.tracer.processing.context.context.detach"
                    ) as mock_detach:
                        mock_token = Mock()
                        mock_attach.return_value = mock_token

                        with pytest.raises(ValueError):
                            with with_distributed_trace_context(carrier, mock_tracer):
                                raise ValueError("Test exception")

                        # Context should still be detached
                        mock_detach.assert_called_once_with(mock_token)

    def test_empty_carrier_uses_current_context(self) -> None:
        """Test that empty carrier falls back to current context."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier: Dict[str, str] = {}

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            # Return None for empty carrier
            mock_extract.return_value = None

            with patch(
                "honeyhive.tracer.processing.context.context.get_current"
            ) as mock_get_current:
                mock_current_ctx = Mock()
                mock_get_current.return_value = mock_current_ctx

                with patch("honeyhive.tracer.processing.context.context.attach"):
                    with patch("honeyhive.tracer.processing.context.context.detach"):
                        with with_distributed_trace_context(carrier, mock_tracer):
                            pass

                        # Should have called get_current as fallback
                        mock_get_current.assert_called_once()

    def test_returns_context_not_none(self) -> None:
        """Test that context manager always yields a valid Context (never None)."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer._propagator = Mock()

        carrier = {"baggage": "session_id=test-session-123"}

        with patch(
            "honeyhive.tracer.processing.context.extract_context_from_carrier"
        ) as mock_extract:
            mock_ctx = Mock()
            mock_extract.return_value = mock_ctx

            with patch(
                "honeyhive.tracer.processing.context.baggage.set_baggage"
            ) as mock_set_baggage:
                mock_set_baggage.return_value = mock_ctx

                with patch("honeyhive.tracer.processing.context.context.attach"):
                    with patch("honeyhive.tracer.processing.context.context.detach"):
                        with with_distributed_trace_context(
                            carrier, mock_tracer
                        ) as ctx:
                            # Context should not be None
                            assert ctx is not None
                            assert ctx == mock_ctx
