"""Events API module for HoneyHive."""

from typing import Any, Dict, List, Optional

from ..models import CreateEventRequest, Event, EventFilter
from .base import BaseAPI


class CreateEventResponse:
    """Response from creating an event.

    Contains the result of an event creation operation including
    the event ID and success status.
    """

    def __init__(self, event_id: str, success: bool):
        """Initialize the response.

        Args:
            event_id: Unique identifier for the created event
            success: Whether the event creation was successful
        """
        self.event_id = event_id
        self.success = success

    @property
    def id(self) -> str:
        """Alias for event_id for compatibility.

        Returns:
            The event ID
        """
        return self.event_id

    @property
    def _id(self) -> str:
        """Alias for event_id for compatibility.

        Returns:
            The event ID
        """
        return self.event_id


class UpdateEventRequest:
    """Request for updating an event.

    Contains the fields that can be updated for an existing event.
    """

    def __init__(
        self,
        event_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None,
    ):
        """Initialize the update request.

        Args:
            event_id: ID of the event to update
            metadata: Additional metadata for the event
            feedback: User feedback for the event
            metrics: Computed metrics for the event
            outputs: Output data for the event
            config: Configuration data for the event
            user_properties: User-defined properties
            duration: Updated duration in milliseconds
        """
        self.event_id = event_id
        self.metadata = metadata
        self.feedback = feedback
        self.metrics = metrics
        self.outputs = outputs
        self.config = config
        self.user_properties = user_properties
        self.duration = duration


class BatchCreateEventRequest:
    """Request for creating multiple events.

    Allows bulk creation of multiple events in a single API call.
    """

    def __init__(self, events: List[CreateEventRequest]):
        """Initialize the batch request.

        Args:
            events: List of events to create
        """
        self.events = events


class BatchCreateEventResponse:
    """Response from creating multiple events.

    Contains the results of a bulk event creation operation.
    """

    def __init__(self, event_ids: List[str], success: bool):
        """Initialize the batch response.

        Args:
            event_ids: List of created event IDs
            success: Whether the batch operation was successful
        """
        self.event_ids = event_ids
        self.success = success


class EventsAPI(BaseAPI):
    """API for event operations."""

    def create_event(self, event: CreateEventRequest) -> CreateEventResponse:
        """Create a new event using CreateEventRequest model."""
        response = self.client.request(
            "POST", "/events", json={"event": event.model_dump(exclude_none=True)}
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    def create_event_from_dict(self, event_data: dict) -> CreateEventResponse:
        """Create a new event from event data dictionary (legacy method)."""
        # Handle both direct event data and nested event data
        if "event" in event_data:
            request_data = event_data
        else:
            request_data = {"event": event_data}

        response = self.client.request("POST", "/events", json=request_data)

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    def create_event_from_request(
        self, event: CreateEventRequest
    ) -> CreateEventResponse:
        """Create a new event from CreateEventRequest object."""
        response = self.client.request(
            "POST", "/events", json={"event": event.model_dump(exclude_none=True)}
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    async def create_event_async(
        self, event: CreateEventRequest
    ) -> CreateEventResponse:
        """Create a new event asynchronously using CreateEventRequest model."""
        response = await self.client.request_async(
            "POST", "/events", json={"event": event.model_dump(exclude_none=True)}
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    async def create_event_from_dict_async(
        self, event_data: dict
    ) -> CreateEventResponse:
        """Create a new event asynchronously from event data dictionary (legacy method)."""
        # Handle both direct event data and nested event data
        if "event" in event_data:
            request_data = event_data
        else:
            request_data = {"event": event_data}

        response = await self.client.request_async("POST", "/events", json=request_data)

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    async def create_event_from_request_async(
        self, event: CreateEventRequest
    ) -> CreateEventResponse:
        """Create a new event asynchronously."""
        response = await self.client.request_async(
            "POST", "/events", json={"event": event.model_dump(exclude_none=True)}
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID."""
        try:
            response = self.client.request("DELETE", f"/events/{event_id}")
            return response.status_code == 200
        except Exception:
            return False

    async def delete_event_async(self, event_id: str) -> bool:
        """Delete an event by ID asynchronously."""
        try:
            response = await self.client.request_async("DELETE", f"/events/{event_id}")
            return response.status_code == 200
        except Exception:
            return False

    def update_event(self, request: UpdateEventRequest) -> None:
        """Update an event."""
        request_data = {
            "event_id": request.event_id,
            "metadata": request.metadata,
            "feedback": request.feedback,
            "metrics": request.metrics,
            "outputs": request.outputs,
            "config": request.config,
            "user_properties": request.user_properties,
            "duration": request.duration,
        }

        # Remove None values
        request_data = {k: v for k, v in request_data.items() if v is not None}

        self.client.request("PUT", "/events", json=request_data)

    async def update_event_async(self, request: UpdateEventRequest) -> None:
        """Update an event asynchronously."""
        request_data = {
            "event_id": request.event_id,
            "metadata": request.metadata,
            "feedback": request.feedback,
            "metrics": request.metrics,
            "outputs": request.outputs,
            "config": request.config,
            "user_properties": request.user_properties,
            "duration": request.duration,
        }

        # Remove None values
        request_data = {k: v for k, v in request_data.items() if v is not None}

        await self.client.request_async("PUT", "/events", json=request_data)

    def create_event_batch(
        self, request: BatchCreateEventRequest
    ) -> BatchCreateEventResponse:
        """Create multiple events using BatchCreateEventRequest model."""
        events_data = [event.model_dump(exclude_none=True) for event in request.events]
        response = self.client.request(
            "POST", "/events/batch", json={"events": events_data}
        )

        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"], success=data["success"]
        )

    def create_event_batch_from_list(
        self, events: List[CreateEventRequest]
    ) -> BatchCreateEventResponse:
        """Create multiple events from a list of CreateEventRequest objects."""
        events_data = [event.model_dump(exclude_none=True) for event in events]
        response = self.client.request(
            "POST", "/events/batch", json={"events": events_data}
        )

        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"], success=data["success"]
        )

    async def create_event_batch_async(
        self, request: BatchCreateEventRequest
    ) -> BatchCreateEventResponse:
        """Create multiple events asynchronously using BatchCreateEventRequest model."""
        events_data = [event.model_dump(exclude_none=True) for event in request.events]
        response = await self.client.request_async(
            "POST", "/events/batch", json={"events": events_data}
        )

        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"], success=data["success"]
        )

    async def create_event_batch_from_list_async(
        self, events: List[CreateEventRequest]
    ) -> BatchCreateEventResponse:
        """Create multiple events asynchronously from a list of CreateEventRequest objects."""
        events_data = [event.model_dump(exclude_none=True) for event in events]
        response = await self.client.request_async(
            "POST", "/events/batch", json={"events": events_data}
        )

        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"], success=data["success"]
        )

    def list_events(self, event_filter: EventFilter, limit: int = 100) -> List[Event]:
        """List events using EventFilter model."""
        # Convert EventFilter to query parameters
        params = {"limit": str(limit)}
        if event_filter.field:
            params["field"] = str(event_filter.field)
        if event_filter.value:
            params["value"] = str(event_filter.value)
        if event_filter.operator:
            params["operator"] = str(event_filter.operator)
        if event_filter.type:
            params["type"] = str(event_filter.type)

        response = self.client.request("GET", "/events", params=params)
        data = response.json()
        return [Event(**event_data) for event_data in data.get("events", [])]

    def list_events_from_dict(
        self, event_filter: dict, limit: int = 100
    ) -> List[Event]:
        """List events from filter dictionary (legacy method)."""
        params = {"limit": limit}
        params.update(event_filter)

        response = self.client.request("GET", "/events", params=params)
        data = response.json()
        return [Event(**event_data) for event_data in data.get("events", [])]

    async def list_events_async(
        self, event_filter: EventFilter, limit: int = 100
    ) -> List[Event]:
        """List events asynchronously using EventFilter model."""
        # Convert EventFilter to query parameters
        params = {"limit": str(limit)}
        if event_filter.field:
            params["field"] = str(event_filter.field)
        if event_filter.value:
            params["value"] = str(event_filter.value)
        if event_filter.operator:
            params["operator"] = str(event_filter.operator)
        if event_filter.type:
            params["type"] = str(event_filter.type)

        response = await self.client.request_async("GET", "/events", params=params)
        data = response.json()
        return [Event(**event_data) for event_data in data.get("events", [])]

    async def list_events_from_dict_async(
        self, event_filter: dict, limit: int = 100
    ) -> List[Event]:
        """List events asynchronously from filter dictionary (legacy method)."""
        params = {"limit": limit}
        params.update(event_filter)

        response = await self.client.request_async("GET", "/events", params=params)
        data = response.json()
        return [Event(**event_data) for event_data in data.get("events", [])]
