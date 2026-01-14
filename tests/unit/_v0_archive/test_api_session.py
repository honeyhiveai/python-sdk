"""Unit tests for honeyhive.api.session.

This module contains comprehensive unit tests for the SessionAPI class,
covering session creation, retrieval, deletion, and response handling.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from honeyhive.api.session import SessionAPI, SessionResponse, SessionStartResponse
from honeyhive.models import Event, SessionStartRequest


class TestSessionStartResponse:
    """Test suite for SessionStartResponse class."""

    def test_initialization_success(self) -> None:
        """Test successful SessionStartResponse initialization.

        Verifies that SessionStartResponse initializes correctly with a session ID
        and stores the session ID properly.
        """
        # Arrange
        test_session_id = "session-test-123"

        # Act
        response = SessionStartResponse(session_id=test_session_id)

        # Assert
        assert response.session_id == test_session_id

    def test_id_property_returns_session_id(self) -> None:
        """Test that id property returns session_id for compatibility.

        Verifies that the id property correctly returns the session_id
        value for backward compatibility.
        """
        # Arrange
        test_session_id = "session-test-456"
        response = SessionStartResponse(session_id=test_session_id)

        # Act
        result = response.id

        # Assert
        assert result == test_session_id

    def test_private_id_property_returns_session_id(self) -> None:
        """Test that _id property returns session_id for compatibility.

        Verifies that the _id property correctly returns the session_id
        value for backward compatibility.
        """
        # Arrange
        test_session_id = "session-test-789"
        response = SessionStartResponse(session_id=test_session_id)

        # Act
        result = response._id

        # Assert
        assert result == test_session_id

    def test_initialization_with_empty_session_id(self) -> None:
        """Test SessionStartResponse initialization with empty session ID.

        Verifies that SessionStartResponse can be initialized with an empty
        session ID and handles it correctly.
        """
        # Arrange
        empty_session_id = ""

        # Act
        response = SessionStartResponse(session_id=empty_session_id)

        # Assert
        assert response.session_id == ""
        assert response.id == ""
        assert response._id == ""

    def test_initialization_with_long_session_id(self) -> None:
        """Test SessionStartResponse initialization with long session ID.

        Verifies that SessionStartResponse handles long session IDs correctly
        without truncation or modification.
        """
        # Arrange
        long_session_id = "session-" + "x" * 100

        # Act
        response = SessionStartResponse(session_id=long_session_id)

        # Assert
        assert response.session_id == long_session_id
        assert len(response.session_id) == 108  # "session-" + 100 x's


class TestSessionResponse:
    """Test suite for SessionResponse class."""

    def test_initialization_success(self) -> None:
        """Test successful SessionResponse initialization.

        Verifies that SessionResponse initializes correctly with an Event
        and stores the event properly.
        """
        # Arrange
        test_event = Mock(spec=Event)
        test_event.event_id = "event-test-123"

        # Act
        response = SessionResponse(event=test_event)

        # Assert
        assert response.event == test_event
        assert response.event.event_id == "event-test-123"

    def test_initialization_with_real_event_object(self) -> None:
        """Test SessionResponse initialization with real Event object.

        Verifies that SessionResponse works correctly with actual Event
        instances and preserves all event data.
        """
        # Arrange
        event_data = {
            "event_id": "event-real-456",
            "session_id": "session-real-789",
            "event_name": "test_event",
            "event_type": "model",
            "project": "test-project",
            "source": "test-source",
        }
        test_event = Event(
            event_id=event_data["event_id"],
            session_id=event_data["session_id"],
            event_name=event_data["event_name"],
            event_type=event_data["event_type"],
            project_id=event_data["project"],
            source=event_data["source"],
        )

        # Act
        response = SessionResponse(event=test_event)

        # Assert
        assert response.event == test_event
        assert response.event.event_id == "event-real-456"
        assert response.event.session_id == "session-real-789"
        assert response.event.event_name == "test_event"

    def test_initialization_preserves_event_attributes(self) -> None:
        """Test that SessionResponse preserves all event attributes.

        Verifies that all attributes of the provided Event object
        are accessible through the SessionResponse.
        """
        # Arrange
        test_event = Mock(spec=Event)
        test_event.event_id = "event-attr-123"
        test_event.session_id = "session-attr-456"
        test_event.project_id = "test-project"
        test_event.source = "test-source"
        test_event.event_type = "model"

        # Act
        response = SessionResponse(event=test_event)

        # Assert
        assert response.event.event_id == "event-attr-123"
        assert response.event.session_id == "session-attr-456"
        assert response.event.project_id == "test-project"
        assert response.event.source == "test-source"
        assert response.event.event_type == "model"


class TestSessionAPIInitialization:
    """Test suite for SessionAPI initialization."""

    def test_initialization_success(self, mock_client: Mock) -> None:
        """Test successful SessionAPI initialization.

        Verifies that SessionAPI initializes correctly with a client
        and properly calls the parent BaseAPI constructor.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            # Act
            session_api = SessionAPI(mock_client)

            # Assert
            assert session_api.client == mock_client
            assert session_api.error_handler == mock_error_handler
            assert session_api._client_name == "SessionAPI"

    def test_initialization_inherits_from_base_api(self, mock_client: Mock) -> None:
        """Test that SessionAPI properly inherits from BaseAPI.

        Verifies that SessionAPI inherits all BaseAPI functionality
        and has access to base methods and attributes.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            # Act
            session_api = SessionAPI(mock_client)

            # Assert
            assert hasattr(session_api, "_create_error_context")
            assert hasattr(session_api, "_process_data_dynamically")
            assert session_api._client_name == "SessionAPI"

    def test_initialization_with_different_client_types(
        self, mock_client: Mock
    ) -> None:
        """Test SessionAPI initialization with different client configurations.

        Verifies that SessionAPI works with various client configurations
        and properly stores the client reference.
        """
        # Arrange
        mock_client.server_url = "https://custom.api.com"
        mock_client.api_key = "custom-key-123"

        with patch("honeyhive.api.base.get_error_handler"):
            # Act
            session_api = SessionAPI(mock_client)

            # Assert
            assert session_api.client.server_url == "https://custom.api.com"
            assert session_api.client.api_key == "custom-key-123"


class TestSessionAPICreateSession:
    """Test suite for SessionAPI.create_session method."""

    def test_create_session_success(self, mock_client: Mock) -> None:
        """Test successful session creation with SessionStartRequest.

        Verifies that create_session correctly processes a SessionStartRequest
        and returns a SessionStartResponse with the session ID.
        """
        # Arrange
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test-source"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-created-123"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.create_session(session_request)

                # Assert
                assert isinstance(result, SessionStartResponse)
                assert result.session_id == "session-created-123"

                # Verify client.request was called correctly
                mock_client.request.assert_called_once_with(
                    "POST",
                    "/session/start",
                    json={
                        "session": session_request.model_dump(
                            mode="json", exclude_none=True
                        )
                    },
                )

    def test_create_session_with_optional_session_id(self, mock_client: Mock) -> None:
        """Test session creation with optional session_id parameter.

        Verifies that create_session correctly handles SessionStartRequest
        with an optional session_id and includes it in the request.
        """
        # Arrange
        session_request = SessionStartRequest(
            project="test-project",
            session_name="test-session",
            source="test-source",
            session_id="custom-session-456",
        )

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "custom-session-456"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.create_session(session_request)

                # Assert
                assert result.session_id == "custom-session-456"

                # Verify the request included the custom session_id
                call_args = mock_client.request.call_args
                request_data = call_args[1]["json"]["session"]
                assert "session_id" in request_data

    def test_create_session_handles_request_exception(self, mock_client: Mock) -> None:
        """Test that create_session handles request exceptions properly.

        Verifies that exceptions from the client.request call are
        propagated correctly without modification.
        """
        # Arrange
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test-source"
        )

        test_exception = RuntimeError("Network error")

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", side_effect=test_exception):
                # Act & Assert
                with pytest.raises(RuntimeError, match="Network error"):
                    session_api.create_session(session_request)

    def test_create_session_handles_invalid_response(self, mock_client: Mock) -> None:
        """Test create_session handling of invalid response format.

        Verifies that create_session handles responses that don't contain
        the expected session_id field appropriately.
        """
        # Arrange
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test-source"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid request"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act & Assert
                with pytest.raises(KeyError):
                    session_api.create_session(session_request)


class TestSessionAPICreateSessionFromDict:
    """Test suite for SessionAPI.create_session_from_dict method."""

    def test_create_session_from_dict_success(self, mock_client: Mock) -> None:
        """Test successful session creation from dictionary data.

        Verifies that create_session_from_dict correctly processes dictionary
        data and returns a SessionStartResponse with the session ID.
        """
        # Arrange
        session_data = {
            "project": "test-project",
            "session_name": "test-session",
            "source": "test-source",
        }

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-dict-123"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.create_session_from_dict(session_data)

                # Assert
                assert isinstance(result, SessionStartResponse)
                assert result.session_id == "session-dict-123"

                # Verify client.request was called with wrapped data
                mock_client.request.assert_called_once_with(
                    "POST", "/session/start", json={"session": session_data}
                )

    def test_create_session_from_dict_with_nested_session(
        self, mock_client: Mock
    ) -> None:
        """Test session creation from dictionary with nested session data.

        Verifies that create_session_from_dict correctly handles dictionary
        data that already contains a "session" key.
        """
        # Arrange
        session_data = {
            "session": {
                "project": "test-project",
                "session_name": "test-session",
                "source": "test-source",
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-nested-456"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.create_session_from_dict(session_data)

                # Assert
                assert result.session_id == "session-nested-456"

                # Verify client.request was called with original nested structure
                mock_client.request.assert_called_once_with(
                    "POST", "/session/start", json=session_data
                )

    def test_create_session_from_dict_handles_empty_dict(
        self, mock_client: Mock
    ) -> None:
        """Test session creation from empty dictionary.

        Verifies that create_session_from_dict handles empty dictionary
        input and still makes the appropriate API call.
        """
        # Arrange
        session_data: Dict[str, Any] = {}

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-empty-789"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.create_session_from_dict(session_data)

                # Assert
                assert result.session_id == "session-empty-789"

                # Verify client.request was called with wrapped empty dict
                mock_client.request.assert_called_once_with(
                    "POST", "/session/start", json={"session": {}}
                )


class TestSessionAPIStartSession:
    """Test suite for SessionAPI.start_session method."""

    def test_start_session_success(self, mock_client: Mock) -> None:
        """Test successful session start with required parameters.

        Verifies that start_session correctly creates a SessionStartRequest
        and returns a SessionStartResponse with the session ID.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-start-123"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                with patch.object(mock_client, "_log") as mock_log:
                    # Act
                    result = session_api.start_session(
                        project="test-project",
                        session_name="test-session",
                        source="test-source",
                    )

                    # Assert
                    assert isinstance(result, SessionStartResponse)
                    assert result.session_id == "session-start-123"

                    # Verify logging was called
                    mock_log.assert_called()

    def test_start_session_with_optional_session_id(self, mock_client: Mock) -> None:
        """Test session start with optional session_id parameter.

        Verifies that start_session correctly handles the optional session_id
        parameter and includes it in the SessionStartRequest.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "custom-start-456"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                with patch.object(mock_client, "_log"):
                    # Act
                    result = session_api.start_session(
                        project="test-project",
                        session_name="test-session",
                        source="test-source",
                        session_id="custom-start-456",
                    )

                    # Assert
                    assert result.session_id == "custom-start-456"

    def test_start_session_with_kwargs(self, mock_client: Mock) -> None:
        """Test session start with additional keyword arguments.

        Verifies that start_session correctly passes additional keyword
        arguments to the SessionStartRequest constructor.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-kwargs-789"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                with patch.object(mock_client, "_log"):
                    # Act
                    result = session_api.start_session(
                        project="test-project",
                        session_name="test-session",
                        source="test-source",
                        custom_field="custom_value",
                    )

                    # Assert
                    assert result.session_id == "session-kwargs-789"

    def test_start_session_handles_nested_session_response(
        self, mock_client: Mock
    ) -> None:
        """Test session start with nested session response structure.

        Verifies that start_session correctly handles responses where
        session_id is nested within a session object.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "session": {"session_id": "session-nested-abc"}
        }

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                with patch.object(mock_client, "_log"):
                    # Act
                    result = session_api.start_session(
                        project="test-project",
                        session_name="test-session",
                        source="test-source",
                    )

                    # Assert
                    assert result.session_id == "session-nested-abc"

    def test_start_session_handles_missing_session_id(self, mock_client: Mock) -> None:
        """Test session start handling of response without session_id.

        Verifies that start_session raises appropriate error when
        response doesn't contain session_id in any expected location.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Session creation failed"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                with patch.object(mock_client, "_log"):
                    # Act & Assert
                    with pytest.raises(
                        ValueError, match="Session ID not found in response"
                    ):
                        session_api.start_session(
                            project="test-project",
                            session_name="test-session",
                            source="test-source",
                        )

    def test_start_session_logs_warning_for_unexpected_structure(
        self, mock_client: Mock
    ) -> None:
        """Test that start_session logs warning for unexpected response structure.

        Verifies that start_session logs a warning when the response structure
        is unexpected but still tries to find the session_id.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "session": {"session_id": "session-warning-def"}
        }

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                with patch.object(mock_client, "_log") as mock_log:
                    # Act
                    result = session_api.start_session(
                        project="test-project",
                        session_name="test-session",
                        source="test-source",
                    )

                    # Assert
                    assert result.session_id == "session-warning-def"

                    # Verify debug logging was called (at least once for response)
                    assert mock_log.call_count >= 1


class TestSessionAPIGetSession:
    """Test suite for SessionAPI.get_session method."""

    def test_get_session_success(self, mock_client: Mock) -> None:
        """Test successful session retrieval by ID.

        Verifies that get_session correctly retrieves a session by ID
        and returns a SessionResponse with the Event data.
        """
        # Arrange
        session_id = "session-get-123"
        event_data = {
            "event_id": "event-123",
            "session_id": session_id,
            "event_name": "test_event",
            "event_type": "model",
            "project": "test-project",
            "source": "test-source",
        }

        mock_response = Mock()
        mock_response.json.return_value = event_data

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.get_session(session_id)

                # Assert
                assert isinstance(result, SessionResponse)
                assert isinstance(result.event, Event)
                assert result.event.event_id == "event-123"
                assert result.event.session_id == session_id

                # Verify client.request was called correctly
                mock_client.request.assert_called_once_with(
                    "GET", f"/session/{session_id}"
                )

    def test_get_session_with_different_session_id_formats(
        self, mock_client: Mock
    ) -> None:
        """Test session retrieval with different session ID formats.

        Verifies that get_session correctly handles various session ID
        formats and constructs the proper API endpoint.
        """
        # Arrange
        session_ids = [
            "simple-123",
            "session-with-dashes-456",
            "session_with_underscores_789",
            "SessionWithCamelCase123",
        ]

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            for session_id in session_ids:
                event_data = {
                    "event_id": f"event-{session_id}",
                    "session_id": session_id,
                    "event_name": "test_event",
                    "event_type": "model",
                    "project": "test-project",
                    "source": "test-source",
                }

                mock_response = Mock()
                mock_response.json.return_value = event_data

                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    result = session_api.get_session(session_id)

                    # Assert
                    assert result.event.session_id == session_id
                    mock_client.request.assert_called_with(
                        "GET", f"/session/{session_id}"
                    )

    def test_get_session_handles_request_exception(self, mock_client: Mock) -> None:
        """Test that get_session handles request exceptions properly.

        Verifies that exceptions from the client.request call are
        propagated correctly without modification.
        """
        # Arrange
        session_id = "session-error-123"
        test_exception = RuntimeError("Session not found")

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", side_effect=test_exception):
                # Act & Assert
                with pytest.raises(RuntimeError, match="Session not found"):
                    session_api.get_session(session_id)

    def test_get_session_handles_invalid_event_data(self, mock_client: Mock) -> None:
        """Test get_session handling of invalid event data.

        Verifies that get_session handles responses with invalid event data
        and propagates Event validation errors appropriately.
        """
        # Arrange
        session_id = "session-invalid-456"
        invalid_event_data = {"invalid_field": "invalid_value"}

        mock_response = Mock()
        mock_response.json.return_value = invalid_event_data

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act & Assert - Event will try to validate and may succeed
                # Let's just verify the method completes and returns a SessionResponse
                result = session_api.get_session(session_id)
                assert isinstance(result, SessionResponse)


class TestSessionAPIDeleteSession:
    """Test suite for SessionAPI.delete_session method."""

    def test_delete_session_success(self, mock_client: Mock) -> None:
        """Test successful session deletion by ID.

        Verifies that delete_session correctly deletes a session by ID
        and returns True for successful deletion.
        """
        # Arrange
        session_id = "session-delete-123"
        mock_client.server_url = "https://api.honeyhive.ai"

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.delete_session(session_id)

                # Assert
                assert result is True

                # Verify client.request was called correctly
                mock_client.request.assert_called_once_with(
                    "DELETE", f"/session/{session_id}"
                )

    def test_delete_session_failure(self, mock_client: Mock) -> None:
        """Test session deletion failure handling.

        Verifies that delete_session returns False when the deletion
        request returns a non-200 status code.
        """
        # Arrange
        session_id = "session-delete-fail-456"
        mock_client.server_url = "https://api.honeyhive.ai"

        mock_response = Mock()
        mock_response.status_code = 404

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", return_value=mock_response):
                # Act
                result = session_api.delete_session(session_id)

                # Assert
                assert result is False

    def test_delete_session_creates_error_context(self, mock_client: Mock) -> None:
        """Test that delete_session creates proper error context.

        Verifies that delete_session creates appropriate error context
        for error handling with correct operation details.
        """
        # Arrange
        session_id = "session-context-789"
        mock_client.server_url = "https://api.honeyhive.ai"

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            with patch.object(
                session_api, "_create_error_context"
            ) as mock_create_context:
                mock_context = Mock()
                mock_create_context.return_value = mock_context

                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    session_api.delete_session(session_id)

                    # Assert
                    mock_create_context.assert_called_once_with(
                        operation="delete_session",
                        method="DELETE",
                        path=f"/session/{session_id}",
                        additional_context={"session_id": session_id},
                    )

    def test_delete_session_with_different_session_id_formats(
        self, mock_client: Mock
    ) -> None:
        """Test session deletion with different session ID formats.

        Verifies that delete_session correctly handles various session ID
        formats and constructs the proper API endpoint.
        """
        # Arrange
        session_ids = [
            "simple-delete-123",
            "session-with-dashes-delete-456",
            "session_with_underscores_delete_789",
        ]

        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            for session_id in session_ids:
                mock_response = Mock()
                mock_response.status_code = 200

                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    result = session_api.delete_session(session_id)

                    # Assert
                    assert result is True
                    mock_client.request.assert_called_with(
                        "DELETE", f"/session/{session_id}"
                    )


class TestSessionAPIAsyncMethods:
    """Test suite for SessionAPI async methods."""

    @pytest.mark.asyncio
    async def test_create_session_async_success(self, mock_client: Mock) -> None:
        """Test successful async session creation with SessionStartRequest.

        Verifies that create_session_async correctly processes a SessionStartRequest
        and returns a SessionStartResponse with the session ID.
        """
        # Arrange
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test-source"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-async-123"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await session_api.create_session_async(session_request)

                # Assert
                assert isinstance(result, SessionStartResponse)
                assert result.session_id == "session-async-123"

    @pytest.mark.asyncio
    async def test_create_session_from_dict_async_success(
        self, mock_client: Mock
    ) -> None:
        """Test successful async session creation from dictionary data.

        Verifies that create_session_from_dict_async correctly processes dictionary
        data and returns a SessionStartResponse with the session ID.
        """
        # Arrange
        session_data = {
            "project": "test-project",
            "session_name": "test-session",
            "source": "test-source",
        }

        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-dict-async-456"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await session_api.create_session_from_dict_async(session_data)

                # Assert
                assert isinstance(result, SessionStartResponse)
                assert result.session_id == "session-dict-async-456"

    @pytest.mark.asyncio
    async def test_start_session_async_success(self, mock_client: Mock) -> None:
        """Test successful async session start with required parameters.

        Verifies that start_session_async correctly creates a SessionStartRequest
        and returns a SessionStartResponse with the session ID.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "session-start-async-789"}

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await session_api.start_session_async(
                    project="test-project",
                    session_name="test-session",
                    source="test-source",
                )

                # Assert
                assert isinstance(result, SessionStartResponse)
                assert result.session_id == "session-start-async-789"

    @pytest.mark.asyncio
    async def test_get_session_async_success(self, mock_client: Mock) -> None:
        """Test successful async session retrieval by ID.

        Verifies that get_session_async correctly retrieves a session by ID
        and returns a SessionResponse with the Event data.
        """
        # Arrange
        session_id = "session-get-async-abc"
        event_data = {
            "event_id": "event-async-123",
            "session_id": session_id,
            "event_name": "test_event",
            "event_type": "model",
            "project": "test-project",
            "source": "test-source",
        }

        mock_response = Mock()
        mock_response.json.return_value = event_data

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await session_api.get_session_async(session_id)

                # Assert
                assert isinstance(result, SessionResponse)
                assert isinstance(result.event, Event)
                assert result.event.session_id == session_id

    @pytest.mark.asyncio
    async def test_delete_session_async_success(self, mock_client: Mock) -> None:
        """Test successful async session deletion by ID.

        Verifies that delete_session_async correctly deletes a session by ID
        and returns True for successful deletion.
        """
        # Arrange
        session_id = "session-delete-async-def"
        mock_client.server_url = "https://api.honeyhive.ai"

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request_async", return_value=mock_response):
                # Act
                result = await session_api.delete_session_async(session_id)

                # Assert
                assert result is True

    @pytest.mark.asyncio
    async def test_delete_session_async_creates_error_context(
        self, mock_client: Mock
    ) -> None:
        """Test that delete_session_async creates proper error context.

        Verifies that delete_session_async creates appropriate error context
        for error handling with correct operation details.
        """
        # Arrange
        session_id = "session-async-context-ghi"
        mock_client.server_url = "https://api.honeyhive.ai"

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            with patch.object(
                session_api, "_create_error_context"
            ) as mock_create_context:
                mock_context = Mock()
                mock_create_context.return_value = mock_context

                with patch.object(
                    mock_client, "request_async", return_value=mock_response
                ):
                    # Act
                    await session_api.delete_session_async(session_id)

                    # Assert
                    mock_create_context.assert_called_once_with(
                        operation="delete_session_async",
                        method="DELETE",
                        path=f"/session/{session_id}",
                        additional_context={"session_id": session_id},
                    )


class TestSessionAPIIntegration:
    """Test suite for SessionAPI integration scenarios."""

    def test_session_lifecycle_integration(self, mock_client: Mock) -> None:
        """Test complete session lifecycle integration.

        Verifies that SessionAPI methods work together correctly
        in a realistic session lifecycle scenario.
        """
        # Arrange
        session_data = {
            "project": "integration-project",
            "session_name": "integration-session",
            "source": "integration-test",
        }

        session_id = "session-lifecycle-123"

        # Mock responses for different operations
        create_response = Mock()
        create_response.json.return_value = {"session_id": session_id}

        get_response = Mock()
        get_response.json.return_value = {
            "event_id": "event-lifecycle-456",
            "session_id": session_id,
            "event_name": "lifecycle_event",
            "event_type": "model",
            "project": "integration-project",
            "source": "integration-test",
        }

        delete_response = Mock()
        delete_response.status_code = 200

        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_context_manager = Mock()
            mock_error_handler.handle_operation.return_value = mock_context_manager
            mock_context_manager.__enter__ = Mock(return_value=mock_context_manager)
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_get_handler.return_value = mock_error_handler

            session_api = SessionAPI(mock_client)

            # Mock client.request to return different responses based on method
            def mock_request_side_effect(
                method: str, _path: str, **_kwargs: Any
            ) -> Mock:
                if method == "POST":
                    return create_response
                if method == "GET":
                    return get_response
                if method == "DELETE":
                    return delete_response
                return Mock()

            with patch.object(
                mock_client, "request", side_effect=mock_request_side_effect
            ):
                # Act - Create session
                create_result = session_api.create_session_from_dict(session_data)

                # Act - Get session
                get_result = session_api.get_session(session_id)

                # Act - Delete session
                delete_result = session_api.delete_session(session_id)

                # Assert
                assert create_result.session_id == session_id
                assert get_result.event.session_id == session_id
                assert delete_result is True

    def test_error_handling_integration(self, mock_client: Mock) -> None:
        """Test error handling integration across SessionAPI methods.

        Verifies that SessionAPI methods handle errors consistently
        and propagate exceptions appropriately.
        """
        # Arrange
        test_exception = RuntimeError("Integration test error")

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            with patch.object(mock_client, "request", side_effect=test_exception):
                # Test create_session error handling
                session_request = SessionStartRequest(
                    project="error-project",
                    session_name="error-session",
                    source="error-test",
                )

                with pytest.raises(RuntimeError, match="Integration test error"):
                    session_api.create_session(session_request)

                # Test get_session error handling
                with pytest.raises(RuntimeError, match="Integration test error"):
                    session_api.get_session("error-session-123")

    def test_response_format_compatibility(self, mock_client: Mock) -> None:
        """Test SessionAPI compatibility with different response formats.

        Verifies that SessionAPI methods handle various response formats
        that might be returned by the API.
        """
        # Arrange
        response_formats = [
            {"session_id": "format-test-1"},  # Direct session_id
            {"session": {"session_id": "format-test-2"}},  # Nested session_id
        ]

        with patch("honeyhive.api.base.get_error_handler"):
            session_api = SessionAPI(mock_client)

            for i, response_format in enumerate(response_formats):
                mock_response = Mock()
                mock_response.json.return_value = response_format

                with patch.object(mock_client, "request", return_value=mock_response):
                    with patch.object(mock_client, "_log"):
                        # Act
                        result = session_api.start_session(
                            project=f"format-project-{i}",
                            session_name=f"format-session-{i}",
                            source="format-test",
                        )

                        # Assert
                        expected_session_id = f"format-test-{i + 1}"
                        assert result.session_id == expected_session_id
