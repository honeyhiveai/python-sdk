"""Unit tests for honeyhive.api.events.

This module contains comprehensive unit tests for the EventsAPI class and related
response/request classes, covering all event operations including creation, deletion,
updating, batch operations, and event listing with proper error handling.
"""

# pylint: disable=too-many-lines,duplicate-code
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from honeyhive.api.events import (
    BatchCreateEventRequest,
    BatchCreateEventResponse,
    CreateEventResponse,
    EventsAPI,
    UpdateEventRequest,
)
from honeyhive.models import CreateEventRequest, Event, EventFilter
from honeyhive.models.generated import EventType1, Operator, Type
from honeyhive.utils.error_handler import ErrorContext


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock HoneyHive client for testing.

    Returns:
        Mock client with necessary attributes configured
    """
    client = Mock()
    client.server_url = "https://api.honeyhive.ai"
    client.request = Mock()
    client.request_async = AsyncMock()
    client._log = Mock()
    return client


@pytest.fixture
def events_api(mock_client: Mock) -> EventsAPI:
    """Create EventsAPI instance with mock client.

    Args:
        mock_client: Mock HoneyHive client

    Returns:
        EventsAPI instance for testing
    """
    with patch("honeyhive.api.base.get_error_handler"):
        return EventsAPI(mock_client)


@pytest.fixture
def sample_create_event_request() -> CreateEventRequest:
    """Create sample CreateEventRequest for testing.

    Returns:
        CreateEventRequest with test data
    """
    return CreateEventRequest(
        project="test-project",
        source="test-source",
        event_name="test-event",
        event_type=EventType1.model,
        config={"model": "gpt-4", "temperature": 0.7},
        inputs={"prompt": "test prompt"},
        duration=1500.0,
        outputs={"response": "test response"},
        metadata={"user_id": "test-user"},
    )


@pytest.fixture
def sample_event_filter() -> EventFilter:
    """Create sample EventFilter for testing.

    Returns:
        EventFilter with test criteria
    """
    return EventFilter(
        field="metadata.user_id",
        value="test-user",
        operator=Operator.is_,
        type=Type.string,
    )


class TestCreateEventResponse:
    """Test suite for CreateEventResponse class."""

    def test_initialization_success(self) -> None:
        """Test successful CreateEventResponse initialization.

        Verifies that CreateEventResponse initializes correctly with
        event_id and success parameters.
        """
        # Arrange
        event_id = "event-123"
        success = True

        # Act
        response = CreateEventResponse(event_id=event_id, success=success)

        # Assert
        assert response.event_id == event_id
        assert response.success == success

    def test_id_property_alias(self) -> None:
        """Test id property returns event_id.

        Verifies that the id property correctly returns the event_id
        for compatibility purposes.
        """
        # Arrange
        event_id = "event-456"
        response = CreateEventResponse(event_id=event_id, success=True)

        # Act
        result_id = response.id

        # Assert
        assert result_id == event_id
        assert result_id == response.event_id

    def test_underscore_id_property_alias(self) -> None:
        """Test _id property returns event_id.

        Verifies that the _id property correctly returns the event_id
        for compatibility purposes.
        """
        # Arrange
        event_id = "event-789"
        response = CreateEventResponse(event_id=event_id, success=False)

        # Act
        result_id = response._id

        # Assert
        assert result_id == event_id
        assert result_id == response.event_id

    def test_initialization_with_failure(self) -> None:
        """Test CreateEventResponse initialization with failure status.

        Verifies that CreateEventResponse handles failure status correctly.
        """
        # Arrange
        event_id = "failed-event-123"
        success = False

        # Act
        response = CreateEventResponse(event_id=event_id, success=success)

        # Assert
        assert response.event_id == event_id
        assert response.success == success
        assert response.id == event_id
        assert response._id == event_id


class TestUpdateEventRequest:
    """Test suite for UpdateEventRequest class."""

    def test_initialization_with_all_parameters(self) -> None:
        """Test UpdateEventRequest initialization with all parameters.

        Verifies that UpdateEventRequest initializes correctly when all
        optional parameters are provided.
        """
        # Arrange
        event_id = "event-123"
        metadata = {"updated": True}
        feedback = {"rating": 5}
        metrics = {"accuracy": 0.95}
        outputs = {"result": "updated"}
        config = {"version": "2.0"}
        user_properties = {"preference": "fast"}
        duration = 2000.0

        # Act
        request = UpdateEventRequest(
            event_id=event_id,
            metadata=metadata,
            feedback=feedback,
            metrics=metrics,
            outputs=outputs,
            config=config,
            user_properties=user_properties,
            duration=duration,
        )

        # Assert
        assert request.event_id == event_id
        assert request.metadata == metadata
        assert request.feedback == feedback
        assert request.metrics == metrics
        assert request.outputs == outputs
        assert request.config == config
        assert request.user_properties == user_properties
        assert request.duration == duration

    def test_initialization_with_minimal_parameters(self) -> None:
        """Test UpdateEventRequest initialization with minimal parameters.

        Verifies that UpdateEventRequest initializes correctly with only
        the required event_id parameter.
        """
        # Arrange
        event_id = "event-456"

        # Act
        request = UpdateEventRequest(event_id=event_id)

        # Assert
        assert request.event_id == event_id
        assert request.metadata is None
        assert request.feedback is None
        assert request.metrics is None
        assert request.outputs is None
        assert request.config is None
        assert request.user_properties is None
        assert request.duration is None

    def test_initialization_with_partial_parameters(self) -> None:
        """Test UpdateEventRequest initialization with partial parameters.

        Verifies that UpdateEventRequest handles partial parameter sets correctly.
        """
        # Arrange
        event_id = "event-789"
        metadata = {"partial": True}
        duration = 1800.0

        # Act
        request = UpdateEventRequest(
            event_id=event_id, metadata=metadata, duration=duration
        )

        # Assert
        assert request.event_id == event_id
        assert request.metadata == metadata
        assert request.duration == duration
        assert request.feedback is None
        assert request.metrics is None
        assert request.outputs is None
        assert request.config is None
        assert request.user_properties is None


class TestBatchCreateEventRequest:
    """Test suite for BatchCreateEventRequest class."""

    def test_initialization_with_event_list(
        self, sample_create_event_request: CreateEventRequest
    ) -> None:
        """Test BatchCreateEventRequest initialization with event list.

        Args:
            sample_create_event_request: Sample CreateEventRequest fixture

        Verifies that BatchCreateEventRequest initializes correctly with
        a list of CreateEventRequest objects.
        """
        # Arrange
        events = [sample_create_event_request]

        # Act
        batch_request = BatchCreateEventRequest(events=events)

        # Assert
        assert batch_request.events == events
        assert len(batch_request.events) == 1
        assert batch_request.events[0] == sample_create_event_request

    def test_initialization_with_multiple_events(
        self, sample_create_event_request: CreateEventRequest
    ) -> None:
        """Test BatchCreateEventRequest initialization with multiple events.

        Args:
            sample_create_event_request: Sample CreateEventRequest fixture

        Verifies that BatchCreateEventRequest handles multiple events correctly.
        """
        # Arrange
        event_2 = CreateEventRequest(
            project="test-project-2",
            source="test-source-2",
            event_name="test-event-2",
            event_type=EventType1.tool,
            config={"tool": "calculator"},
            inputs={"operation": "add"},
            duration=800.0,
        )
        events = [sample_create_event_request, event_2]

        # Act
        batch_request = BatchCreateEventRequest(events=events)

        # Assert
        assert batch_request.events == events
        assert len(batch_request.events) == 2
        assert batch_request.events[0] == sample_create_event_request
        assert batch_request.events[1] == event_2

    def test_initialization_with_empty_list(self) -> None:
        """Test BatchCreateEventRequest initialization with empty list.

        Verifies that BatchCreateEventRequest handles empty event lists.
        """
        # Arrange
        events: List[CreateEventRequest] = []

        # Act
        batch_request = BatchCreateEventRequest(events=events)

        # Assert
        assert batch_request.events == events
        assert len(batch_request.events) == 0


class TestBatchCreateEventResponse:
    """Test suite for BatchCreateEventResponse class."""

    def test_initialization_success(self) -> None:
        """Test successful BatchCreateEventResponse initialization.

        Verifies that BatchCreateEventResponse initializes correctly with
        event_ids list and success status.
        """
        # Arrange
        event_ids = ["event-1", "event-2", "event-3"]
        success = True

        # Act
        response = BatchCreateEventResponse(event_ids=event_ids, success=success)

        # Assert
        assert response.event_ids == event_ids
        assert response.success == success
        assert len(response.event_ids) == 3

    def test_initialization_with_failure(self) -> None:
        """Test BatchCreateEventResponse initialization with failure status.

        Verifies that BatchCreateEventResponse handles failure status correctly.
        """
        # Arrange
        event_ids = ["partial-event-1"]
        success = False

        # Act
        response = BatchCreateEventResponse(event_ids=event_ids, success=success)

        # Assert
        assert response.event_ids == event_ids
        assert response.success == success
        assert len(response.event_ids) == 1

    def test_initialization_with_empty_list(self) -> None:
        """Test BatchCreateEventResponse initialization with empty event_ids.

        Verifies that BatchCreateEventResponse handles empty event_ids lists.
        """
        # Arrange
        event_ids: List[str] = []
        success = False

        # Act
        response = BatchCreateEventResponse(event_ids=event_ids, success=success)

        # Assert
        assert response.event_ids == event_ids
        assert response.success == success
        assert len(response.event_ids) == 0


class TestEventsAPICreateEvent:
    """Test suite for EventsAPI create_event methods."""

    def test_create_event_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test successful event creation.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event successfully creates an event and returns
        the correct response.
        """
        # Arrange
        expected_response_data = {"event_id": "created-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event(sample_create_event_request)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "created-event-123"
        assert result.success is True

        # Verify client.request was called correctly
        mock_client.request.assert_called_once_with(
            "POST",
            "/events",
            json={
                "event": sample_create_event_request.model_dump(
                    mode="json", exclude_none=True
                )
            },
        )

    def test_create_event_from_dict_with_nested_event(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test create_event_from_dict with nested event data.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that create_event_from_dict handles nested event data correctly.
        """
        # Arrange
        event_data = {
            "event": {
                "project": "test-project",
                "source": "test-source",
                "event_name": "test-event",
                "event_type": "model",
                "config": {"model": "gpt-4"},
                "inputs": {"prompt": "test"},
                "duration": 1000.0,
            }
        }
        expected_response_data = {"event_id": "dict-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event_from_dict(event_data)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "dict-event-123"
        assert result.success is True

        # Verify client.request was called with nested data
        mock_client.request.assert_called_once_with("POST", "/events", json=event_data)

    def test_create_event_from_dict_with_direct_event(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test create_event_from_dict with direct event data.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that create_event_from_dict wraps direct event data correctly.
        """
        # Arrange
        event_data = {
            "project": "test-project",
            "source": "test-source",
            "event_name": "test-event",
            "event_type": "model",
            "config": {"model": "gpt-4"},
            "inputs": {"prompt": "test"},
            "duration": 1000.0,
        }
        expected_response_data = {"event_id": "direct-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event_from_dict(event_data)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "direct-event-123"
        assert result.success is True

        # Verify client.request was called with wrapped data
        mock_client.request.assert_called_once_with(
            "POST", "/events", json={"event": event_data}
        )

    def test_create_event_from_request(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test create_event_from_request method.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_from_request works identically to create_event.
        """
        # Arrange
        expected_response_data = {"event_id": "request-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event_from_request(sample_create_event_request)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "request-event-123"
        assert result.success is True

        # Verify client.request was called correctly
        mock_client.request.assert_called_once_with(
            "POST",
            "/events",
            json={
                "event": sample_create_event_request.model_dump(
                    mode="json", exclude_none=True
                )
            },
        )


class TestEventsAPICreateEventAsync:
    """Test suite for EventsAPI async create_event methods."""

    @pytest.mark.asyncio
    async def test_create_event_async_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test successful async event creation.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_async successfully creates an event.
        """
        # Arrange
        expected_response_data = {"event_id": "async-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        # Act
        result = await events_api.create_event_async(sample_create_event_request)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "async-event-123"
        assert result.success is True

        # Verify client.request_async was called correctly
        mock_client.request_async.assert_called_once_with(
            "POST",
            "/events",
            json={
                "event": sample_create_event_request.model_dump(
                    mode="json", exclude_none=True
                )
            },
        )

    @pytest.mark.asyncio
    async def test_create_event_from_dict_async_with_nested_event(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test async create_event_from_dict with nested event data.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that create_event_from_dict_async handles nested event data.
        """
        # Arrange
        event_data = {
            "event": {
                "project": "async-project",
                "source": "async-source",
                "event_name": "async-event",
                "event_type": "tool",
                "config": {"tool": "async-tool"},
                "inputs": {"input": "async-input"},
                "duration": 2000.0,
            }
        }
        expected_response_data = {"event_id": "async-dict-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        # Act
        result = await events_api.create_event_from_dict_async(event_data)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "async-dict-event-123"
        assert result.success is True

        # Verify client.request_async was called with nested data
        mock_client.request_async.assert_called_once_with(
            "POST", "/events", json=event_data
        )

    @pytest.mark.asyncio
    async def test_create_event_from_dict_async_with_direct_event(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test async create_event_from_dict with direct event data.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that create_event_from_dict_async wraps direct event data.
        """
        # Arrange
        event_data = {
            "project": "async-direct-project",
            "source": "async-direct-source",
            "event_name": "async-direct-event",
            "event_type": "chain",
            "config": {"chain": "async-chain"},
            "inputs": {"input": "async-direct-input"},
            "duration": 1500.0,
        }
        expected_response_data = {"event_id": "async-direct-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        # Act
        result = await events_api.create_event_from_dict_async(event_data)

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "async-direct-event-123"
        assert result.success is True

        # Verify client.request_async was called with wrapped data
        mock_client.request_async.assert_called_once_with(
            "POST", "/events", json={"event": event_data}
        )

    @pytest.mark.asyncio
    async def test_create_event_from_request_async(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test async create_event_from_request method.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_from_request_async works correctly.
        """
        # Arrange
        expected_response_data = {
            "event_id": "async-request-event-123",
            "success": True,
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        # Act
        result = await events_api.create_event_from_request_async(
            sample_create_event_request
        )

        # Assert
        assert isinstance(result, CreateEventResponse)
        assert result.event_id == "async-request-event-123"
        assert result.success is True

        # Verify client.request_async was called correctly
        mock_client.request_async.assert_called_once_with(
            "POST",
            "/events",
            json={
                "event": sample_create_event_request.model_dump(
                    mode="json", exclude_none=True
                )
            },
        )


class TestEventsAPIDeleteEvent:
    """Test suite for EventsAPI delete_event methods."""

    def test_delete_event_success(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test successful event deletion.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that delete_event successfully deletes an event.
        """
        # Arrange
        event_id = "event-to-delete-123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        with patch.object(events_api.error_handler, "handle_operation") as mock_handle:
            mock_handle.return_value.__enter__ = Mock()
            mock_handle.return_value.__exit__ = Mock(return_value=None)

            # Act
            result = events_api.delete_event(event_id)

            # Assert
            assert result is True

            # Verify client.request was called correctly
            mock_client.request.assert_called_once_with("DELETE", f"/events/{event_id}")

            # Verify error context was created
            mock_handle.assert_called_once()
            context_arg = mock_handle.call_args[0][0]
            assert isinstance(context_arg, ErrorContext)
            assert context_arg.operation == "delete_event"
            assert context_arg.method == "DELETE"
            assert context_arg.url == f"https://api.honeyhive.ai/events/{event_id}"

    def test_delete_event_failure(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test event deletion failure.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that delete_event returns False when deletion fails.
        """
        # Arrange
        event_id = "event-not-found-123"
        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.request.return_value = mock_response

        with patch.object(events_api.error_handler, "handle_operation") as mock_handle:
            mock_handle.return_value.__enter__ = Mock()
            mock_handle.return_value.__exit__ = Mock(return_value=None)

            # Act
            result = events_api.delete_event(event_id)

            # Assert
            assert result is False

            # Verify client.request was called correctly
            mock_client.request.assert_called_once_with("DELETE", f"/events/{event_id}")

    @pytest.mark.asyncio
    async def test_delete_event_async_success(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test successful async event deletion.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that delete_event_async successfully deletes an event.
        """
        # Arrange
        event_id = "async-event-to-delete-123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request_async.return_value = mock_response

        with patch.object(events_api.error_handler, "handle_operation") as mock_handle:
            mock_handle.return_value.__enter__ = Mock()
            mock_handle.return_value.__exit__ = Mock(return_value=None)

            # Act
            result = await events_api.delete_event_async(event_id)

            # Assert
            assert result is True

            # Verify client.request_async was called correctly
            mock_client.request_async.assert_called_once_with(
                "DELETE", f"/events/{event_id}"
            )

    @pytest.mark.asyncio
    async def test_delete_event_async_failure(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test async event deletion failure.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that delete_event_async returns False when deletion fails.
        """
        # Arrange
        event_id = "async-event-not-found-123"
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.request_async.return_value = mock_response

        with patch.object(events_api.error_handler, "handle_operation") as mock_handle:
            mock_handle.return_value.__enter__ = Mock()
            mock_handle.return_value.__exit__ = Mock(return_value=None)

            # Act
            result = await events_api.delete_event_async(event_id)

            # Assert
            assert result is False

            # Verify client.request_async was called correctly
            mock_client.request_async.assert_called_once_with(
                "DELETE", f"/events/{event_id}"
            )


class TestEventsAPIUpdateEvent:
    """Test suite for EventsAPI update_event methods."""

    def test_update_event_success(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test successful event update.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that update_event successfully updates an event.
        """
        # Arrange
        update_request = UpdateEventRequest(
            event_id="event-to-update-123",
            metadata={"updated": True},
            feedback={"rating": 5},
            metrics={"accuracy": 0.95},
            outputs={"result": "updated"},
            config={"version": "2.0"},
            user_properties={"preference": "fast"},
            duration=2500.0,
        )
        mock_response = Mock()
        mock_client.request.return_value = mock_response

        # Act
        events_api.update_event(update_request)

        # Assert
        # Verify client.request was called correctly
        expected_data = {
            "event_id": "event-to-update-123",
            "metadata": {"updated": True},
            "feedback": {"rating": 5},
            "metrics": {"accuracy": 0.95},
            "outputs": {"result": "updated"},
            "config": {"version": "2.0"},
            "user_properties": {"preference": "fast"},
            "duration": 2500.0,
        }
        mock_client.request.assert_called_once_with(
            "PUT", "/events", json=expected_data
        )

    def test_update_event_with_none_values_filtered(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test event update with None values filtered out.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that update_event filters out None values from request data.
        """
        # Arrange
        update_request = UpdateEventRequest(
            event_id="event-partial-update-123",
            metadata={"partial": True},
            feedback=None,
            metrics=None,
            outputs={"result": "partial"},
            config=None,
            user_properties=None,
            duration=1800.0,
        )
        mock_response = Mock()
        mock_client.request.return_value = mock_response

        # Act
        events_api.update_event(update_request)

        # Assert
        # Verify client.request was called with filtered data
        expected_data = {
            "event_id": "event-partial-update-123",
            "metadata": {"partial": True},
            "outputs": {"result": "partial"},
            "duration": 1800.0,
        }
        mock_client.request.assert_called_once_with(
            "PUT", "/events", json=expected_data
        )

    @pytest.mark.asyncio
    async def test_update_event_async_success(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test successful async event update.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that update_event_async successfully updates an event.
        """
        # Arrange
        update_request = UpdateEventRequest(
            event_id="async-event-to-update-123",
            metadata={"async_updated": True},
            duration=3000.0,
        )
        mock_response = Mock()
        mock_client.request_async.return_value = mock_response

        # Act
        await events_api.update_event_async(update_request)

        # Assert
        # Verify client.request_async was called correctly
        expected_data = {
            "event_id": "async-event-to-update-123",
            "metadata": {"async_updated": True},
            "duration": 3000.0,
        }
        mock_client.request_async.assert_called_once_with(
            "PUT", "/events", json=expected_data
        )

    @pytest.mark.asyncio
    async def test_update_event_async_with_none_values_filtered(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test async event update with None values filtered out.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that update_event_async filters out None values.
        """
        # Arrange
        update_request = UpdateEventRequest(
            event_id="async-event-partial-update-123",
            metadata=None,
            feedback={"async_rating": 4},
            metrics=None,
            outputs=None,
            config={"async_version": "3.0"},
            user_properties=None,
            duration=None,
        )
        mock_response = Mock()
        mock_client.request_async.return_value = mock_response

        # Act
        await events_api.update_event_async(update_request)

        # Assert
        # Verify client.request_async was called with filtered data
        expected_data = {
            "event_id": "async-event-partial-update-123",
            "feedback": {"async_rating": 4},
            "config": {"async_version": "3.0"},
        }
        mock_client.request_async.assert_called_once_with(
            "PUT", "/events", json=expected_data
        )


class TestEventsAPIBatchCreateEvent:
    """Test suite for EventsAPI batch create_event methods."""

    def test_create_event_batch_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test successful batch event creation.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_batch successfully creates multiple events.
        """
        # Arrange
        batch_request = BatchCreateEventRequest(events=[sample_create_event_request])
        expected_response_data = {
            "event_ids": ["batch-event-1", "batch-event-2"],
            "success": True,
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event_batch(batch_request)

        # Assert
        assert isinstance(result, BatchCreateEventResponse)
        assert result.event_ids == ["batch-event-1", "batch-event-2"]
        assert result.success is True

        # Verify client.request was called correctly
        expected_events_data = [
            sample_create_event_request.model_dump(mode="json", exclude_none=True)
        ]
        mock_client.request.assert_called_once_with(
            "POST", "/events/batch", json={"events": expected_events_data}
        )

    def test_create_event_batch_from_list_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test successful batch event creation from list.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_batch_from_list successfully creates events.
        """
        # Arrange
        events = [sample_create_event_request]
        expected_response_data = {
            "event_ids": ["list-batch-event-1"],
            "success": True,
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event_batch_from_list(events)

        # Assert
        assert isinstance(result, BatchCreateEventResponse)
        assert result.event_ids == ["list-batch-event-1"]
        assert result.success is True

        # Verify client.request was called correctly
        expected_events_data = [
            sample_create_event_request.model_dump(mode="json", exclude_none=True)
        ]
        mock_client.request.assert_called_once_with(
            "POST", "/events/batch", json={"events": expected_events_data}
        )

    @pytest.mark.asyncio
    async def test_create_event_batch_async_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test successful async batch event creation.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_batch_async successfully creates events.
        """
        # Arrange
        batch_request = BatchCreateEventRequest(events=[sample_create_event_request])
        expected_response_data = {
            "event_ids": ["async-batch-event-1", "async-batch-event-2"],
            "success": True,
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        # Act
        result = await events_api.create_event_batch_async(batch_request)

        # Assert
        assert isinstance(result, BatchCreateEventResponse)
        assert result.event_ids == ["async-batch-event-1", "async-batch-event-2"]
        assert result.success is True

        # Verify client.request_async was called correctly
        expected_events_data = [
            sample_create_event_request.model_dump(mode="json", exclude_none=True)
        ]
        mock_client.request_async.assert_called_once_with(
            "POST", "/events/batch", json={"events": expected_events_data}
        )

    @pytest.mark.asyncio
    async def test_create_event_batch_from_list_async_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test successful async batch event creation from list.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that create_event_batch_from_list_async creates events.
        """
        # Arrange
        events = [sample_create_event_request]
        expected_response_data = {
            "event_ids": ["async-list-batch-event-1"],
            "success": True,
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        # Act
        result = await events_api.create_event_batch_from_list_async(events)

        # Assert
        assert isinstance(result, BatchCreateEventResponse)
        assert result.event_ids == ["async-list-batch-event-1"]
        assert result.success is True

        # Verify client.request_async was called correctly
        expected_events_data = [
            sample_create_event_request.model_dump(mode="json", exclude_none=True)
        ]
        mock_client.request_async.assert_called_once_with(
            "POST", "/events/batch", json={"events": expected_events_data}
        )


class TestEventsAPIListEvents:
    """Test suite for EventsAPI list_events methods."""

    def test_list_events_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_event_filter: EventFilter,
    ) -> None:
        """Test successful event listing.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_event_filter: Sample EventFilter

        Verifies that list_events successfully retrieves events.
        """
        # Arrange
        project = "test-project"
        limit = 50
        expected_response_data = {
            "events": [
                {
                    "event_id": "list-event-1",
                    "project_id": project,
                    "event_name": "test-event-1",
                },
                {
                    "event_id": "list-event-2",
                    "project_id": project,
                    "event_name": "test-event-2",
                },
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        with patch.object(events_api, "_process_data_dynamically") as mock_process:
            mock_process.return_value = [Mock(), Mock()]

            # Act
            result = events_api.list_events(
                sample_event_filter, limit=limit, project=project
            )

            # Assert
            assert len(result) == 2

            # Verify client.request was called correctly
            expected_body = {
                "project": project,
                "filters": [
                    {
                        "field": "metadata.user_id",
                        "value": "test-user",
                        "operator": "is",
                        "type": "string",
                    }
                ],
                "limit": limit,
                "page": 1,
            }
            mock_client.request.assert_called_once_with(
                "POST", "/events/export", json=expected_body
            )

            # Verify _process_data_dynamically was called
            mock_process.assert_called_once_with(
                expected_response_data["events"], Event, "events"
            )

    def test_list_events_without_project_raises_error(
        self,
        events_api: EventsAPI,
        sample_event_filter: EventFilter,
    ) -> None:
        """Test list_events raises ValueError without project.

        Args:
            events_api: EventsAPI instance
            sample_event_filter: Sample EventFilter

        Verifies that list_events raises ValueError when project is not provided.
        """
        # Act & Assert
        with pytest.raises(ValueError, match="project parameter is required"):
            events_api.list_events(sample_event_filter)

    def test_list_events_with_empty_filter(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test list_events with empty filter.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that list_events handles empty filters correctly.
        """
        # Arrange
        empty_filter = EventFilter()
        project = "test-project"
        expected_response_data: Dict[str, Any] = {"events": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        with patch.object(events_api, "_process_data_dynamically") as mock_process:
            mock_process.return_value = []

            # Act
            result = events_api.list_events(empty_filter, project=project)

            # Assert
            assert len(result) == 0

            # Verify client.request was called with empty filters
            expected_body = {
                "project": project,
                "filters": [],
                "limit": 100,
                "page": 1,
            }
            mock_client.request.assert_called_once_with(
                "POST", "/events/export", json=expected_body
            )

    def test_list_events_from_dict_success(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test successful event listing from dict filter.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that list_events_from_dict successfully retrieves events.
        """
        # Arrange
        event_filter = {"field": "metadata.user_id", "value": "test-user"}
        limit = 25
        expected_response_data = {
            "events": [
                {"event_id": "dict-list-event-1", "event_name": "dict-test-event-1"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        with patch.object(events_api, "_process_data_dynamically") as mock_process:
            mock_process.return_value = [Mock()]

            # Act
            result = events_api.list_events_from_dict(event_filter, limit=limit)

            # Assert
            assert len(result) == 1

            # Verify client.request was called correctly
            expected_params = {
                "limit": limit,
                "field": "metadata.user_id",
                "value": "test-user",
            }
            mock_client.request.assert_called_once_with(
                "GET", "/events", params=expected_params
            )

    def test_get_events_success(self, events_api: EventsAPI, mock_client: Mock) -> None:
        """Test successful get_events with filters.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that get_events successfully retrieves events with filtering.
        """
        # Arrange
        project = "test-project"
        filters = [
            EventFilter(
                field="metadata.user_id",
                value="test-user",
                operator=Operator.is_,
                type=Type.string,
            )
        ]
        date_range = {"$gte": "2023-01-01", "$lte": "2023-12-31"}
        limit = 500
        page = 2

        expected_response_data = {
            "events": [
                {"event_id": "get-event-1", "project_id": project},
                {"event_id": "get-event-2", "project_id": project},
            ],
            "totalEvents": 150,
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.get_events(
            project=project,
            filters=filters,
            date_range=date_range,
            limit=limit,
            page=page,
        )

        # Assert
        assert "events" in result
        assert "totalEvents" in result
        assert len(result["events"]) == 2
        assert result["totalEvents"] == 150
        assert all(isinstance(event, Event) for event in result["events"])

        # Verify client.request was called correctly
        expected_body = {
            "project": project,
            "filters": [
                {
                    "field": "metadata.user_id",
                    "value": "test-user",
                    "operator": "is",
                    "type": "string",
                }
            ],
            "limit": limit,
            "page": page,
            "dateRange": date_range,
        }
        mock_client.request.assert_called_once_with(
            "POST", "/events/export", json=expected_body
        )

    @pytest.mark.asyncio
    async def test_list_events_async_success(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_event_filter: EventFilter,
    ) -> None:
        """Test successful async event listing.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_event_filter: Sample EventFilter

        Verifies that list_events_async successfully retrieves events.
        """
        # Arrange
        project = "async-test-project"
        limit = 75
        expected_response_data = {
            "events": [{"event_id": "async-list-event-1", "project_id": project}]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        with patch.object(events_api, "_process_data_dynamically") as mock_process:
            mock_process.return_value = [Mock()]

            # Act
            result = await events_api.list_events_async(
                sample_event_filter, limit=limit, project=project
            )

            # Assert
            assert len(result) == 1

            # Verify client.request_async was called correctly
            expected_body = {
                "project": project,
                "filters": [
                    {
                        "field": "metadata.user_id",
                        "value": "test-user",
                        "operator": "is",
                        "type": "string",
                    }
                ],
                "limit": limit,
                "page": 1,
            }
            mock_client.request_async.assert_called_once_with(
                "POST", "/events/export", json=expected_body
            )

    @pytest.mark.asyncio
    async def test_list_events_async_without_project_raises_error(
        self,
        events_api: EventsAPI,
        sample_event_filter: EventFilter,
    ) -> None:
        """Test async list_events raises ValueError without project.

        Args:
            events_api: EventsAPI instance
            sample_event_filter: Sample EventFilter

        Verifies that list_events_async raises ValueError when project is missing.
        """
        # Act & Assert
        with pytest.raises(ValueError, match="project parameter is required"):
            await events_api.list_events_async(sample_event_filter)

    @pytest.mark.asyncio
    async def test_list_events_from_dict_async_success(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test successful async event listing from dict filter.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that list_events_from_dict_async successfully retrieves events.
        """
        # Arrange
        event_filter = {"field": "metadata.session_id", "value": "async-session"}
        limit = 10
        expected_response_data = {
            "events": [
                {"event_id": "async-dict-list-event-1", "session_id": "async-session"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request_async.return_value = mock_response

        with patch.object(events_api, "_process_data_dynamically") as mock_process:
            mock_process.return_value = [Mock()]

            # Act
            result = await events_api.list_events_from_dict_async(
                event_filter, limit=limit
            )

            # Assert
            assert len(result) == 1

            # Verify client.request_async was called correctly
            expected_params = {
                "limit": limit,
                "field": "metadata.session_id",
                "value": "async-session",
            }
            mock_client.request_async.assert_called_once_with(
                "GET", "/events", params=expected_params
            )


class TestEventsAPIIntegration:
    """Test suite for EventsAPI integration scenarios."""

    def test_events_api_inheritance_from_base_api(self, events_api: EventsAPI) -> None:
        """Test that EventsAPI properly inherits from BaseAPI.

        Args:
            events_api: EventsAPI instance

        Verifies that EventsAPI has all BaseAPI functionality.
        """
        # Assert
        assert hasattr(events_api, "client")
        assert hasattr(events_api, "error_handler")
        assert hasattr(events_api, "_client_name")
        assert hasattr(events_api, "_create_error_context")
        assert hasattr(events_api, "_process_data_dynamically")
        assert events_api._client_name == "EventsAPI"

    def test_error_context_creation_integration(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test error context creation integration in delete operations.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that error context is properly created and used.
        """
        # Arrange
        event_id = "integration-test-event-123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        with patch.object(events_api, "_create_error_context") as mock_create_context:
            mock_context = Mock()
            mock_create_context.return_value = mock_context

            with patch.object(
                events_api.error_handler, "handle_operation"
            ) as mock_handle:
                mock_handle.return_value.__enter__ = Mock()
                mock_handle.return_value.__exit__ = Mock(return_value=None)

                # Act
                result = events_api.delete_event(event_id)

                # Assert
                assert result is True

                # Verify error context was created correctly
                mock_create_context.assert_called_once_with(
                    operation="delete_event",
                    method="DELETE",
                    path=f"/events/{event_id}",
                    additional_context={"event_id": event_id},
                )

                # Verify error handler was used
                mock_handle.assert_called_once_with(mock_context)

    def test_dynamic_data_processing_integration(
        self, events_api: EventsAPI, mock_client: Mock
    ) -> None:
        """Test dynamic data processing integration in list operations.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client

        Verifies that _process_data_dynamically is properly integrated.
        """
        # Arrange
        event_filter = {"field": "test_field", "value": "test_value"}
        expected_response_data = {
            "events": [
                {"event_id": "integration-event-1"},
                {"event_id": "integration-event-2"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        with patch.object(events_api, "_process_data_dynamically") as mock_process:
            mock_events = [Mock(), Mock()]
            mock_process.return_value = mock_events

            # Act
            result = events_api.list_events_from_dict(event_filter)

            # Assert
            assert result == mock_events

            # Verify _process_data_dynamically was called correctly
            mock_process.assert_called_once_with(
                expected_response_data["events"], Event, "events"
            )

    def test_model_dump_integration_with_exclude_none(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test model_dump integration with exclude_none parameter.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that model_dump(mode="json", exclude_none=True) is used correctly.
        """
        # Arrange
        expected_response_data = {"event_id": "model-dump-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response

        # Act
        result = events_api.create_event(sample_create_event_request)

        # Assert
        assert result.event_id == "model-dump-event-123"

        # Verify model_dump was called with correct parameters
        call_args = mock_client.request.call_args
        json_data = call_args[1]["json"]
        assert "event" in json_data
        # The actual model_dump call is handled by the CreateEventRequest object
        # We verify the structure is correct
        assert isinstance(json_data["event"], dict)

    def test_async_and_sync_method_consistency(
        self,
        events_api: EventsAPI,
        mock_client: Mock,
        sample_create_event_request: CreateEventRequest,
    ) -> None:
        """Test consistency between async and sync methods.

        Args:
            events_api: EventsAPI instance
            mock_client: Mock HoneyHive client
            sample_create_event_request: Sample CreateEventRequest

        Verifies that async and sync methods produce consistent results.
        """
        # Arrange
        expected_response_data = {"event_id": "consistency-event-123", "success": True}
        mock_response = Mock()
        mock_response.json.return_value = expected_response_data
        mock_client.request.return_value = mock_response
        mock_client.request_async.return_value = mock_response

        # Act - Sync
        sync_result = events_api.create_event(sample_create_event_request)

        # Act - Async
        async def run_async_test() -> CreateEventResponse:
            return await events_api.create_event_async(sample_create_event_request)

        async_result = asyncio.run(run_async_test())

        # Assert
        assert sync_result.event_id == async_result.event_id
        assert sync_result.success == async_result.success

        # Verify both methods called their respective client methods
        mock_client.request.assert_called_once()
        mock_client.request_async.assert_called_once()

        # Verify both used the same JSON structure
        sync_call_args = mock_client.request.call_args
        async_call_args = mock_client.request_async.call_args
        assert sync_call_args[0] == async_call_args[0]  # Same method and path
        assert sync_call_args[1]["json"] == async_call_args[1]["json"]  # Same JSON data
