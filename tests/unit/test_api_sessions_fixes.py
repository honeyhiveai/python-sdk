"""Unit tests for session API compatibility fixes."""

import warnings
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from honeyhive.api.client import SessionsAPI
from honeyhive.models import StartSessionRequest


def _make_mock_config() -> MagicMock:
    """Create a minimal API config mock for SessionsAPI tests."""
    mock_config = MagicMock()
    mock_config.base_path = "https://api.honeyhive.ai"
    mock_config.get_access_token.return_value = "test-token"
    mock_config.verify = True
    return mock_config


class TestSessionsAPICompatibility:
    """Tests for session start backwards compatibility."""

    def test_start_wraps_flat_dict_input_for_back_compat(self) -> None:
        """Test that the flat legacy session payload is wrapped for the new model."""
        sessions_api = SessionsAPI(_make_mock_config())
        session_payload: Dict[str, Any] = {
            "session_name": "test-session",
            "source": "test-source",
        }
        expected_response = MagicMock()

        with patch(
            "honeyhive.api.client.sessions_svc.startSession",
            return_value=expected_response,
        ) as mock_start:
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                response = sessions_api.start(session_payload)

        assert response is expected_response
        request = mock_start.call_args.kwargs["data"]
        assert isinstance(request, StartSessionRequest)
        assert request.session.model_dump(exclude_none=True) == session_payload
        assert len(caught_warnings) == 1
        assert issubclass(caught_warnings[0].category, DeprecationWarning)
        assert "flat session payload" in str(caught_warnings[0].message)

    def test_start_accepts_already_wrapped_session_dict(self) -> None:
        """Test that the generated nested request shape is passed through unchanged."""
        sessions_api = SessionsAPI(_make_mock_config())
        wrapped_payload: Dict[str, Any] = {
            "session": {
                "session_name": "test-session",
                "source": "test-source",
            }
        }
        expected_response = MagicMock()

        with patch(
            "honeyhive.api.client.sessions_svc.startSession",
            return_value=expected_response,
        ) as mock_start:
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                response = sessions_api.start(wrapped_payload)

        assert response is expected_response
        request = mock_start.call_args.kwargs["data"]
        assert isinstance(request, StartSessionRequest)
        assert (
            request.session.model_dump(exclude_none=True) == wrapped_payload["session"]
        )
        assert caught_warnings == []

    @pytest.mark.asyncio
    async def test_start_async_wraps_flat_dict_input_for_back_compat(self) -> None:
        """Test that async session start preserves the same legacy dict support."""
        sessions_api = SessionsAPI(_make_mock_config())
        session_payload: Dict[str, Any] = {
            "session_name": "test-session",
            "source": "test-source",
        }
        expected_response = MagicMock()

        with patch(
            "honeyhive.api.client.sessions_svc_async.startSession",
            new=AsyncMock(return_value=expected_response),
        ) as mock_start:
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                response = await sessions_api.start_async(session_payload)

        assert response is expected_response
        request = mock_start.call_args.kwargs["data"]
        assert isinstance(request, StartSessionRequest)
        assert request.session.model_dump(exclude_none=True) == session_payload
        assert len(caught_warnings) == 1
        assert issubclass(caught_warnings[0].category, DeprecationWarning)
        assert "flat session payload" in str(caught_warnings[0].message)
