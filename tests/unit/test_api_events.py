"""Unit tests for HoneyHive Events API functionality."""

import time
from unittest.mock import Mock, patch

import pytest

from honeyhive.api.events import (
    BatchCreateEventRequest,
    BatchCreateEventResponse,
    CreateEventResponse,
    EventsAPI,
)
from honeyhive.models import CreateEventRequest, EventFilter
from honeyhive.models.generated import EventType1

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestEventsAPI:
    """Test Events API functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.events_api = EventsAPI(self.mock_client)

    def test_events_api_initialization(self) -> None:
        """Test EventsAPI initialization."""
        assert self.events_api.client == self.mock_client

    def test_create_event(self) -> None:
        """Test creating an event."""
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "test-model"},
            inputs={"prompt": "test prompt"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata={},
            feedback={},
            metrics={},
            user_properties={},
        )

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_id": "test-event-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            response = self.events_api.create_event(event_request)

            assert isinstance(response, CreateEventResponse)
            assert response.event_id == "test-event-123"
            assert response.success is True
            mock_request.assert_called_once()

    def test_create_event_batch(self) -> None:
        """Test creating multiple events."""
        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-1",
                event_type=EventType1.model,
                config={"model": "test-model-1"},
                inputs={"prompt": "test prompt 1"},
                duration=100.0,
                event_id="test-event-1-123",
                session_id="test-session-123",
                parent_id=None,
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            ),
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-2",
                event_type=EventType1.tool,
                config={"tool": "test-tool-2"},
                inputs={"input": "test input 2"},
                duration=200.0,
                event_id="test-event-2-123",
                session_id="test-session-123",
                parent_id=None,
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            ),
        ]

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": ["event-1", "event-2"],
                "success": True,
            }
            mock_request.return_value = mock_response

            batch_request = BatchCreateEventRequest(events=events)
            response = self.events_api.create_event_batch(batch_request)

            assert isinstance(response, BatchCreateEventResponse)
            assert len(response.event_ids) == 2
            assert response.success is True

    def test_create_event_batch_from_list(self) -> None:
        """Test creating multiple events from list using new model-based method."""
        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-1",
                event_type=EventType1.model,
                config={"model": "test-model-1"},
                inputs={"prompt": "test prompt 1"},
                duration=100.0,
                event_id="test-event-1-123",
                session_id="test-session-123",
                parent_id=None,
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            ),
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test-event-2",
                event_type=EventType1.chain,
                config={"chain": "test-chain-2"},
                inputs={"input": "test input 2"},
                duration=200.0,
                event_id="test-event-2-123",
                session_id="test-session-123",
                parent_id=None,
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            ),
        ]

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": ["event-1", "event-2"],
                "success": True,
            }
            mock_request.return_value = mock_response

            response = self.events_api.create_event_batch_from_list(events)

            assert isinstance(response, BatchCreateEventResponse)
            assert len(response.event_ids) == 2
            assert response.success is True

    def test_list_events_with_filter_model(self) -> None:
        """Test listing events with model filter."""
        event_filter = EventFilter(
            field="metadata.demo_type",
            value="api_client_models",
            operator=None,
            type=None,
        )

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "events": [
                    {"event_id": "event-1", "event_type": "model"},
                    {"event_id": "event-2", "event_type": "model"},
                ]
            }
            mock_request.return_value = mock_response

            events = self.events_api.list_events(event_filter, limit=50)

            assert len(events) == 2
            mock_request.assert_called_once()

    def test_events_api_error_handling(self) -> None:
        """Test Events API error handling."""
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "test-model"},
            inputs={"prompt": "test prompt"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata={},
            feedback={},
            metrics={},
            user_properties={},
        )

        with patch.object(self.mock_client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                self.events_api.create_event(event_request)

    def test_events_api_invalid_response(self) -> None:
        """Test Events API invalid response handling."""
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.tool,
            config={"tool": "test-tool"},
            inputs={"input": "test input"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata={},
            feedback={},
            metrics={},
            user_properties={},
        )

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_request.return_value = mock_response

            with pytest.raises(Exception, match="Invalid JSON"):
                self.events_api.create_event(event_request)

    def test_events_api_performance(self) -> None:
        """Test Events API performance characteristics."""
        # Create many events
        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name=f"test-event-{i}",
                event_type=EventType1.model,
                config={"model": f"test-model-{i}"},
                inputs={"prompt": f"test prompt {i}"},
                duration=100.0,
                event_id=f"test-event-{i}-123",
                session_id="test-session-123",
                parent_id=None,
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            )
            for i in range(100)
        ]

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": [f"event-{i}" for i in range(100)],
                "success": True,
            }
            mock_request.return_value = mock_response

            start_time = time.time()

            batch_request = BatchCreateEventRequest(events=events)
            response = self.events_api.create_event_batch(batch_request)

            end_time = time.time()
            duration = end_time - start_time

            # Should complete in reasonable time
            assert duration < 1.0
            assert response.success is True
            assert len(response.event_ids) == 100

    def test_events_api_memory_usage(self) -> None:
        """Test Events API memory usage characteristics."""
        import gc
        import sys

        # Get initial memory usage
        gc.collect()
        initial_memory = sys.getsizeof(self.events_api)

        # Create many events
        events = [
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name=f"test-event-{i}",
                event_type=EventType1.chain,
                config={"chain": f"test-chain-{i}"},
                inputs={"input": f"test input {i}"},
                duration=100.0,
                event_id=f"test-event-{i}-123",
                session_id="test-session-123",
                parent_id=None,
                children_ids=[],
                outputs={},
                error=None,
                start_time=None,
                end_time=None,
                metadata={},
                feedback={},
                metrics={},
                user_properties={},
            )
            for i in range(100)
        ]

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_ids": [f"event-{i}" for i in range(100)],
                "success": True,
            }
            mock_request.return_value = mock_response

            batch_request = BatchCreateEventRequest(events=events)
            response = self.events_api.create_event_batch(batch_request)

            # Force garbage collection
            gc.collect()

            # Check memory usage hasn't grown significantly
            final_memory = sys.getsizeof(self.events_api)
            memory_growth = final_memory - initial_memory

            # Memory growth should be minimal
            assert memory_growth < 1000  # Less than 1KB growth
            assert response.success is True

    def test_events_api_concurrent_access(self) -> None:
        """Test Events API concurrent access."""
        import threading

        errors = []

        def create_event(thread_id: int) -> None:
            try:
                event_request = CreateEventRequest(
                    project="test-project",
                    source="test",
                    event_name=f"test-event-{thread_id}",
                    event_type=EventType1.model,
                    config={"model": f"test-model-{thread_id}"},
                    inputs={"prompt": f"test prompt {thread_id}"},
                    duration=100.0,
                    event_id=f"test-event-{thread_id}-123",
                    session_id="test-session-123",
                    parent_id=None,
                    children_ids=[],
                    outputs={},
                    error=None,
                    start_time=None,
                    end_time=None,
                    metadata={},
                    feedback={},
                    metrics={},
                    user_properties={},
                )

                with patch.object(self.mock_client, "request") as mock_request:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "event_id": f"event-{thread_id}",
                        "success": True,
                    }
                    mock_request.return_value = mock_response

                    response = self.events_api.create_event(event_request)
                    assert response.success is True

            except Exception as e:
                errors.append(e)

        # Create threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_event, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0

    def test_events_api_edge_cases(self) -> None:
        """Test Events API edge cases."""
        # Test with empty metadata
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.tool,
            config={"tool": "test-tool"},
            inputs={"input": "test input"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata={},
            feedback={},
            metrics={},
            user_properties={},
        )

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_id": "test-event-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            response = self.events_api.create_event(event_request)
            assert response.success is True

        # Test with very long metadata
        long_metadata = {"key": "x" * 10000}
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.chain,
            config={"chain": "test-chain"},
            inputs={"input": "test input"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata=long_metadata,
            feedback={},
            metrics={},
            user_properties={},
        )

        with patch.object(self.mock_client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_id": "test-event-123",
                "success": True,
            }
            mock_request.return_value = mock_response

            response = self.events_api.create_event(event_request)
            assert response.success is True

    def test_events_api_validation(self) -> None:
        """Test Events API validation."""
        # Test with required fields
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "test-model"},
            inputs={"prompt": "test prompt"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata={},
            feedback={},
            metrics={},
            user_properties={},
        )

        # Should not raise validation errors
        assert event_request.project == "test-project"
        assert event_request.source == "test"
        assert event_request.event_name == "test-event"
        assert event_request.event_type == EventType1.model

        # Test with optional fields
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.tool,
            config={"tool": "test-tool"},
            inputs={"input": "test input"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=time.time() * 1000,  # Convert to milliseconds
            end_time=None,
            metadata={"key": "value"},
            feedback={},
            metrics={},
            user_properties={},
        )

        assert event_request.metadata == {"key": "value"}
        assert event_request.start_time is not None

    def test_events_api_serialization(self) -> None:
        """Test Events API serialization."""
        # Test that models can be serialized
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.chain,
            config={"chain": "test-chain"},
            inputs={"input": "test input"},
            duration=100.0,
            event_id="test-event-123",
            session_id="test-session-123",
            parent_id=None,
            children_ids=[],
            outputs={},
            error=None,
            start_time=None,
            end_time=None,
            metadata={},
            feedback={},
            metrics={},
            user_properties={},
        )

        # Should be able to convert to dict
        event_dict = event_request.model_dump()
        assert "project" in event_dict
        assert "source" in event_dict
        assert "event_name" in event_dict
        assert "event_type" in event_dict
        assert "config" in event_dict
        assert "inputs" in event_dict
        assert "duration" in event_dict

        # Should be able to create from dict
        new_event = CreateEventRequest(**event_dict)
        assert new_event.project == event_request.project
        assert new_event.source == event_request.source
        assert new_event.event_name == event_request.event_name
        assert new_event.event_type == event_request.event_type


class TestEventsAPIClient:
    """Test events API client methods."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        from honeyhive.api.client import HoneyHive

        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_event_response(self):
        return {"event_id": "event-123", "success": True}

    def test_create_event_with_model(self, client, mock_event_response):
        """Test creating event using CreateEventRequest model."""
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"model": "gpt-4"},
            inputs={"prompt": "test prompt"},
            duration=100.0,
            metadata={"version": "1.0"},
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_event_response
            mock_request.return_value = mock_response

            result = client.events.create_event(event_request)

            assert result.event_id == "event-123"
            assert result.success is True
            mock_request.assert_called_once()

    def test_create_event_from_dict(self, client, mock_event_response):
        """Test creating event from dictionary (legacy method)."""
        event_data = {
            "project": "test-project",
            "source": "test",
            "event_name": "test-event",
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_event_response
            mock_request.return_value = mock_response

            result = client.events.create_event_from_dict(event_data)

            assert result.event_id == "event-123"
            assert result.success is True
            mock_request.assert_called_once()

    def test_delete_event_success(self, client):
        """Test successful event deletion."""
        event_id = "event-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.events.delete_event(event_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/events/{event_id}")

    def test_delete_event_failure(self, client):
        """Test failed event deletion."""
        event_id = "event-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.events.delete_event(event_id)

    def test_list_events_with_filter(self, client):
        """Test listing events with EventFilter."""
        mock_data = {
            "events": [
                {"project_id": "proj-1", "event_name": "event1"},
                {"project_id": "proj-2", "event_name": "event2"},
            ]
        }

        event_filter = EventFilter(field="project", value="test-project")

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.events.list_events(event_filter, limit=50)

            assert len(result) == 2
            assert result[0].project_id == "proj-1"
            assert result[1].project_id == "proj-2"
            mock_request.assert_called_once()

    def test_list_events_from_dict(self, client):
        """Test listing events from filter dictionary."""
        mock_data = {"events": [{"project_id": "test-project", "event_name": "event1"}]}

        event_filter = {"project": "test-project"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.events.list_events_from_dict(event_filter, limit=100)

            assert len(result) == 1
            assert result[0].project_id == "test-project"
            mock_request.assert_called_once()
