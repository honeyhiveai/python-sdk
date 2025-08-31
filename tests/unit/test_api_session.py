"""Unit tests for session API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import SessionStartRequest


class TestSessionAPI:
    """Test session API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_session_data(self):
        return {
            "session_id": "session-123",
            "project": "test-project",
            "session_name": "test-session",
            "source": "test",
            "created_at": "2024-01-15T10:00:00Z",
        }

    def test_create_session_with_model(self, client, mock_session_data):
        """Test creating session using SessionStartRequest model."""
        session_request = SessionStartRequest(
            project="test-project",
            session_name="test-session",
            source="test",
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_session_data
            mock_request.return_value = mock_response

            result = client.sessions.create_session(session_request)

            assert result.session_id == "session-123"
            mock_request.assert_called_once()

    def test_create_session_from_dict(self, client, mock_session_data):
        """Test creating session from dictionary (legacy method)."""
        session_data = {
            "project": "test-project",
            "session_name": "test-session",
            "source": "test",
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_session_data
            mock_request.return_value = mock_response

            result = client.sessions.create_session_from_dict(session_data)

            assert result.session_id == "session-123"
            mock_request.assert_called_once()

    def test_get_session(self, client, mock_session_data):
        """Test getting session by ID."""
        session_id = "session-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_session_data
            mock_request.return_value = mock_response

            result = client.sessions.get_session(session_id)

            assert result.event is not None
            mock_request.assert_called_once_with("GET", f"/session/{session_id}")

    def test_session_api_methods_exist(self, client):
        """Test that session API methods exist."""
        # Test that the methods exist - sessions API doesn't have list method
        assert hasattr(client.sessions, "create_session")
        assert hasattr(client.sessions, "get_session")
        assert hasattr(client.sessions, "delete_session")
        assert callable(client.sessions.create_session)
        assert callable(client.sessions.get_session)
        assert callable(client.sessions.delete_session)

    def test_delete_session_success(self, client):
        """Test successful session deletion."""
        session_id = "session-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.sessions.delete_session(session_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/session/{session_id}")

    def test_delete_session_failure(self, client):
        """Test failed session deletion."""
        session_id = "session-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.sessions.delete_session(session_id)
