"""Unit tests for decorator baggage preservation in distributed tracing.

This module tests that the @trace decorator preserves existing baggage
from distributed tracing instead of overwriting it.
"""

# pylint: disable=C0301,W0613
# Justification: line-too-long: Complex baggage test assertions; unused-argument: Pytest fixtures
from unittest.mock import Mock, patch

import pytest
from opentelemetry import context

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import _setup_decorator_baggage_context


class TestDecoratorBaggagePreservation:
    """Test suite for @trace decorator baggage preservation."""

    @patch("honeyhive.tracer.instrumentation.decorators.baggage.get_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.baggage.set_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.context.get_current")
    @patch("honeyhive.tracer.instrumentation.decorators.context.attach")
    def test_preserves_existing_session_id_from_distributed_trace(
        self,
        _mock_attach: Mock,
        mock_get_current: Mock,
        mock_set_baggage: Mock,
        mock_get_baggage: Mock,
    ) -> None:
        """Test that existing session_id from distributed trace is preserved."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer.session_id = "local-session-123"
        mock_tracer.project = "local-project"
        mock_tracer.source = "local-source"

        mock_span = Mock()
        mock_ctx = Mock()
        mock_get_current.return_value = mock_ctx

        # Simulate distributed trace context with existing session_id
        def mock_get_baggage_side_effect(key: str, _ctx: context.Context = None):
            existing_baggage = {
                "session_id": "distributed-session-456",  # From remote client
                "project": None,  # Not in baggage
                "source": None,  # Not in baggage
            }
            return existing_baggage.get(key)

        mock_get_baggage.side_effect = mock_get_baggage_side_effect
        mock_set_baggage.return_value = mock_ctx

        _setup_decorator_baggage_context(mock_tracer, mock_span)

        # Verify session_id was NOT overwritten (not called with local value)
        session_id_calls = [
            call
            for call in mock_set_baggage.call_args_list
            if len(call[0]) > 0 and call[0][0] == "session_id"
        ]
        # Should not set session_id since it already exists in baggage
        assert not any(
            "local-session-123" in str(call) for call in session_id_calls
        ), "Local session_id should not overwrite distributed session_id"

    @patch("honeyhive.tracer.instrumentation.decorators.baggage.get_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.baggage.set_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.context.get_current")
    @patch("honeyhive.tracer.instrumentation.decorators.context.attach")
    def test_sets_local_session_id_when_not_in_baggage(
        self,
        _mock_attach: Mock,
        mock_get_current: Mock,
        mock_set_baggage: Mock,
        mock_get_baggage: Mock,
    ) -> None:
        """Test that local session_id is set when not present in baggage."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer.session_id = "local-session-123"
        mock_tracer.project = "local-project"
        mock_tracer.source = "local-source"
        mock_tracer._tracer_id = "tracer-789"

        mock_span = Mock()
        mock_ctx = Mock()
        mock_get_current.return_value = mock_ctx

        # Simulate empty baggage (local execution, not distributed)
        mock_get_baggage.return_value = None
        mock_set_baggage.return_value = mock_ctx

        _setup_decorator_baggage_context(mock_tracer, mock_span)

        # Verify local session_id WAS set
        session_id_calls = [
            call
            for call in mock_set_baggage.call_args_list
            if len(call[0]) > 0 and call[0][0] == "session_id"
        ]
        assert any(
            "local-session-123" in str(call) for call in session_id_calls
        ), "Local session_id should be set when not in baggage"

    @patch("honeyhive.tracer.instrumentation.decorators.baggage.get_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.baggage.set_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.context.get_current")
    @patch("honeyhive.tracer.instrumentation.decorators.context.attach")
    def test_preserves_project_and_source_from_distributed_trace(
        self,
        _mock_attach: Mock,
        mock_get_current: Mock,
        mock_set_baggage: Mock,
        mock_get_baggage: Mock,
    ) -> None:
        """Test existing project/source from distributed trace are preserved."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer.session_id = "local-session-123"
        mock_tracer.project = "local-project"
        mock_tracer.source = "local-source"

        mock_span = Mock()
        mock_ctx = Mock()
        mock_get_current.return_value = mock_ctx

        # Simulate distributed trace with all baggage present
        def mock_get_baggage_side_effect(key: str, ctx: context.Context = None):
            existing_baggage = {
                "session_id": "distributed-session-456",
                "project": "distributed-project",
                "source": "distributed-source",
            }
            return existing_baggage.get(key)

        mock_get_baggage.side_effect = mock_get_baggage_side_effect
        mock_set_baggage.return_value = mock_ctx

        _setup_decorator_baggage_context(mock_tracer, mock_span)

        # Verify none of the distributed values were overwritten
        all_calls_str = str(mock_set_baggage.call_args_list)
        assert (
            "local-project" not in all_calls_str
        ), "Local project should not overwrite distributed project"
        assert (
            "local-source" not in all_calls_str
        ), "Local source should not overwrite distributed source"

    @patch("honeyhive.tracer.instrumentation.decorators.baggage.get_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.baggage.set_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.context.get_current")
    @patch("honeyhive.tracer.instrumentation.decorators.context.attach")
    def test_mixed_scenario_some_baggage_exists(
        self,
        _mock_attach: Mock,
        mock_get_current: Mock,
        mock_set_baggage: Mock,
        mock_get_baggage: Mock,
    ) -> None:
        """Test mixed scenario where some baggage exists and some doesn't."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer.session_id = "local-session-123"
        mock_tracer.project = "local-project"
        mock_tracer.source = "local-source"
        mock_tracer._tracer_id = "tracer-789"

        mock_span = Mock()
        mock_ctx = Mock()
        mock_get_current.return_value = mock_ctx

        # Simulate partial baggage (session_id from distributed, but no project/source)
        def mock_get_baggage_side_effect(key: str, ctx: context.Context = None):
            existing_baggage = {
                "session_id": "distributed-session-456",
                "project": None,  # Not in baggage - should use local
                "source": None,  # Not in baggage - should use local
            }
            return existing_baggage.get(key)

        mock_get_baggage.side_effect = mock_get_baggage_side_effect
        mock_set_baggage.return_value = mock_ctx

        _setup_decorator_baggage_context(mock_tracer, mock_span)

        all_calls_str = str(mock_set_baggage.call_args_list)

        # Session ID should NOT be set (already in baggage)
        assert "local-session-123" not in all_calls_str

        # Project and source SHOULD be set (not in baggage)
        project_calls = [
            call
            for call in mock_set_baggage.call_args_list
            if len(call[0]) > 0 and call[0][0] == "project"
        ]
        source_calls = [
            call
            for call in mock_set_baggage.call_args_list
            if len(call[0]) > 0 and call[0][0] == "source"
        ]

        assert any(
            "local-project" in str(call) for call in project_calls
        ), "Local project should be set when not in baggage"
        assert any(
            "local-source" in str(call) for call in source_calls
        ), "Local source should be set when not in baggage"

    @patch("honeyhive.tracer.instrumentation.decorators.baggage.get_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.baggage.set_baggage")
    @patch("honeyhive.tracer.instrumentation.decorators.context.get_current")
    @patch("honeyhive.tracer.instrumentation.decorators.context.attach")
    def test_handles_exception_gracefully(
        self,
        mock_attach: Mock,
        mock_get_current: Mock,
        mock_set_baggage: Mock,
        mock_get_baggage: Mock,
    ) -> None:
        """Test that decorator handles baggage setup exceptions gracefully."""
        mock_tracer = Mock(spec=HoneyHiveTracer)
        mock_tracer.session_id = "local-session-123"

        mock_span = Mock()
        mock_get_current.return_value = Mock()

        # Simulate exception in baggage.get_baggage
        mock_get_baggage.side_effect = Exception("Baggage error")

        # Should not raise - decorator should handle gracefully
        try:
            _setup_decorator_baggage_context(mock_tracer, mock_span)
        except Exception:
            pytest.fail("_setup_decorator_baggage_context should not raise exceptions")
