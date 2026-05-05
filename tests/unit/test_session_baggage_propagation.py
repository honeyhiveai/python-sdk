"""Tests for session_name baggage propagation in create_session(skip_api_call=True).

When skip_backend_session_creation is enabled and callers manage session_ids
per-request via create_session(session_id=..., session_name=..., skip_api_call=True),
session_name must propagate through baggage so per-request names override the
init-time tracer.session_name on emitted spans.
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.core.context import TracerContextMixin


class _FakeTracerContextMixin(TracerContextMixin):
    """Minimal concrete TracerContextMixin for exercising create_session()."""

    def __init__(self) -> None:
        self.client: Any = None
        self.session_api: Any = None
        self._session_id = None
        self._baggage_lock = Mock()
        self._cache_manager = None
        self.propagator = Mock()

    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        return key

    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        return value


@pytest.fixture
def mixin() -> _FakeTracerContextMixin:
    return _FakeTracerContextMixin()


@patch("honeyhive.tracer.core.context.context.attach")
@patch("honeyhive.tracer.core.context.baggage.set_baggage")
@patch("honeyhive.tracer.core.context.context.get_current")
def test_skip_api_call_propagates_session_name_via_baggage(
    mock_get_current: Mock,
    mock_set_baggage: Mock,
    mock_attach: Mock,
    mixin: _FakeTracerContextMixin,
) -> None:
    """skip_api_call=True with a session_name must propagate the name via
    baggage, so per-request session_names don't get masked by the init-time
    tracer.session_name when skip_backend_session_creation is enabled."""
    mock_current_ctx = Mock(name="current_ctx")
    mock_ctx_with_id = Mock(name="ctx_with_id")
    mock_ctx_with_name = Mock(name="ctx_with_name")
    mock_get_current.return_value = mock_current_ctx
    mock_set_baggage.side_effect = [mock_ctx_with_id, mock_ctx_with_name]

    result = mixin.create_session(
        session_id="provided-session-id",
        session_name="per-request-name",
        skip_api_call=True,
    )

    assert result == "provided-session-id"
    assert mock_set_baggage.call_count == 2
    mock_set_baggage.assert_any_call(
        "session_id", "provided-session-id", mock_current_ctx
    )
    mock_set_baggage.assert_any_call(
        "session_name", "per-request-name", mock_ctx_with_id
    )
    mock_attach.assert_called_once_with(mock_ctx_with_name)


@patch("honeyhive.tracer.core.context.context.attach")
@patch("honeyhive.tracer.core.context.baggage.set_baggage")
@patch("honeyhive.tracer.core.context.context.get_current")
def test_skip_api_call_no_session_name_does_not_set_baggage_name(
    mock_get_current: Mock,
    mock_set_baggage: Mock,
    mock_attach: Mock,
    mixin: _FakeTracerContextMixin,
) -> None:
    """When session_name is not passed, the session_name baggage entry must
    not be set so the span processor falls back to tracer.session_name."""
    mock_current_ctx = Mock(name="current_ctx")
    mock_ctx_with_id = Mock(name="ctx_with_id")
    mock_get_current.return_value = mock_current_ctx
    mock_set_baggage.return_value = mock_ctx_with_id

    result = mixin.create_session(
        session_id="provided-session-id",
        skip_api_call=True,
    )

    assert result == "provided-session-id"
    assert mock_set_baggage.call_count == 1
    mock_set_baggage.assert_called_once_with(
        "session_id", "provided-session-id", mock_current_ctx
    )
