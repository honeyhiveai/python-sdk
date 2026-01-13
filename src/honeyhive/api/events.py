"""Events API module for HoneyHive."""

from typing import Any, Dict, List, Optional, Union

from ..models import CreateEventRequest, Event, EventFilter
from .base import BaseAPI


class CreateEventResponse:  # pylint: disable=too-few-public-methods
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


class UpdateEventRequest:  # pylint: disable=too-few-public-methods
    """Request for updating an event.

    Contains the fields that can be updated for an existing event.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        event_id: str,
        *,
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


class BatchCreateEventRequest:  # pylint: disable=too-few-public-methods
    """Request for creating multiple events.

    Allows bulk creation of multiple events in a single API call.
    """

    def __init__(self, events: List[CreateEventRequest]):
        """Initialize the batch request.

        Args:
            events: List of events to create
        """
        self.events = events


class BatchCreateEventResponse:  # pylint: disable=too-few-public-methods
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
            "POST",
            "/events",
            json={"event": event.model_dump(mode="json", exclude_none=True)},
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
            "POST",
            "/events",
            json={"event": event.model_dump(mode="json", exclude_none=True)},
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    async def create_event_async(
        self, event: CreateEventRequest
    ) -> CreateEventResponse:
        """Create a new event asynchronously using CreateEventRequest model."""
        response = await self.client.request_async(
            "POST",
            "/events",
            json={"event": event.model_dump(mode="json", exclude_none=True)},
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    async def create_event_from_dict_async(
        self, event_data: dict
    ) -> CreateEventResponse:
        """Create a new event asynchronously from event data dictionary \
        (legacy method)."""
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
            "POST",
            "/events",
            json={"event": event.model_dump(mode="json", exclude_none=True)},
        )

        data = response.json()
        return CreateEventResponse(event_id=data["event_id"], success=data["success"])

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID."""
        context = self._create_error_context(
            operation="delete_event",
            method="DELETE",
            path=f"/events/{event_id}",
            additional_context={"event_id": event_id},
        )

        with self.error_handler.handle_operation(context):
            response = self.client.request("DELETE", f"/events/{event_id}")
            return response.status_code == 200

    async def delete_event_async(self, event_id: str) -> bool:
        """Delete an event by ID asynchronously."""
        context = self._create_error_context(
            operation="delete_event_async",
            method="DELETE",
            path=f"/events/{event_id}",
            additional_context={"event_id": event_id},
        )

        with self.error_handler.handle_operation(context):
            response = await self.client.request_async("DELETE", f"/events/{event_id}")
            return response.status_code == 200

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
        events_data = [
            event.model_dump(mode="json", exclude_none=True) for event in request.events
        ]
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
        events_data = [
            event.model_dump(mode="json", exclude_none=True) for event in events
        ]
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
        events_data = [
            event.model_dump(mode="json", exclude_none=True) for event in request.events
        ]
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
        """Create multiple events asynchronously from a list of \
        CreateEventRequest objects."""
        events_data = [
            event.model_dump(mode="json", exclude_none=True) for event in events
        ]
        response = await self.client.request_async(
            "POST", "/events/batch", json={"events": events_data}
        )

        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"], success=data["success"]
        )

    def list_events(
        self,
        event_filters: Union[EventFilter, List[EventFilter]],
        limit: int = 100,
        project: Optional[str] = None,
        page: int = 1,
    ) -> List[Event]:
        """List events using EventFilter model with dynamic processing optimization.

        Uses the proper /events/export POST endpoint as specified in OpenAPI spec.

        Args:
            event_filters: EventFilter or list of EventFilter objects with
                filtering criteria
            limit: Maximum number of events to return (default: 100)
            project: Project name to filter by (required by API)
            page: Page number for pagination (default: 1)

        Returns:
            List of Event objects matching the filters

        Examples:
            Filter events by type and status::

                filters = [
                    EventFilter(
                        field="event_type",
                        operator="is",
                        value="model",
                        type="string",
                    ),
                    EventFilter(
                        field="error",
                        operator="is not",
                        value=None,
                        type="string",
                    ),
                ]
                events = client.events.list_events(
                    event_filters=filters,
                    project="My Project",
                    limit=50
                )
        """
        if not project:
            raise ValueError("project parameter is required for listing events")

        # Auto-convert single EventFilter to list
        if isinstance(event_filters, EventFilter):
            event_filters = [event_filters]

        # Build filters array as expected by /events/export endpoint
        filters = []
        for event_filter in event_filters:
            if (
                event_filter.field
                and event_filter.value is not None
                and event_filter.operator
                and event_filter.type
            ):
                filter_dict = {
                    "field": str(event_filter.field),
                    "value": str(event_filter.value),
                    "operator": event_filter.operator.value,
                    "type": event_filter.type.value,
                }
                filters.append(filter_dict)

        # Build request body according to OpenAPI spec
        request_body = {
            "project": project,
            "filters": filters,
            "limit": limit,
            "page": page,
        }

        response = self.client.request("POST", "/events/export", json=request_body)
        data = response.json()

        # Dynamic processing: Use universal dynamic processor
        return self._process_data_dynamically(data.get("events", []), Event, "events")

    def list_events_from_dict(
        self, event_filter: dict, limit: int = 100
    ) -> List[Event]:
        """List events from filter dictionary (legacy method)."""
        params = {"limit": limit}
        params.update(event_filter)

        response = self.client.request("GET", "/events", params=params)
        data = response.json()

        # Dynamic processing: Use universal dynamic processor
        return self._process_data_dynamically(data.get("events", []), Event, "events")

    def get_events(  # pylint: disable=too-many-arguments
        self,
        project: str,
        filters: List[EventFilter],
        *,
        date_range: Optional[Dict[str, str]] = None,
        limit: int = 1000,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Get events using filters via /events/export endpoint.

        This is the proper way to filter events by session_id and other criteria.

        Args:
            project: Name of the project associated with the event
            filters: List of EventFilter objects to apply
            date_range: Optional date range filter with $gte and $lte ISO strings
            limit: Limit number of results (default 1000, max 7500)
            page: Page number of results (default 1)

        Returns:
            Dict containing 'events' list and 'totalEvents' count
        """
        # Convert filters to proper format for API
        filters_data = []
        for filter_obj in filters:
            filter_dict = filter_obj.model_dump(mode="json", exclude_none=True)
            # Convert enum values to strings for JSON serialization
            if "operator" in filter_dict and hasattr(filter_dict["operator"], "value"):
                filter_dict["operator"] = filter_dict["operator"].value
            if "type" in filter_dict and hasattr(filter_dict["type"], "value"):
                filter_dict["type"] = filter_dict["type"].value
            filters_data.append(filter_dict)

        request_data = {
            "project": project,
            "filters": filters_data,
            "limit": limit,
            "page": page,
        }

        if date_range:
            request_data["dateRange"] = date_range

        response = self.client.request("POST", "/events/export", json=request_data)
        data = response.json()

        # Parse events into Event objects
        events = [Event(**event_data) for event_data in data.get("events", [])]

        return {"events": events, "totalEvents": data.get("totalEvents", 0)}

    async def list_events_async(
        self,
        event_filters: Union[EventFilter, List[EventFilter]],
        limit: int = 100,
        project: Optional[str] = None,
        page: int = 1,
    ) -> List[Event]:
        """List events asynchronously using EventFilter model.

        Uses the proper /events/export POST endpoint as specified in OpenAPI spec.

        Args:
            event_filters: EventFilter or list of EventFilter objects with
                filtering criteria
            limit: Maximum number of events to return (default: 100)
            project: Project name to filter by (required by API)
            page: Page number for pagination (default: 1)

        Returns:
            List of Event objects matching the filters

        Examples:
            Filter events by type and status::

                filters = [
                    EventFilter(
                        field="event_type",
                        operator="is",
                        value="model",
                        type="string",
                    ),
                    EventFilter(
                        field="error",
                        operator="is not",
                        value=None,
                        type="string",
                    ),
                ]
                events = await client.events.list_events_async(
                    event_filters=filters,
                    project="My Project",
                    limit=50
                )
        """
        if not project:
            raise ValueError("project parameter is required for listing events")

        # Auto-convert single EventFilter to list
        if isinstance(event_filters, EventFilter):
            event_filters = [event_filters]

        # Build filters array as expected by /events/export endpoint
        filters = []
        for event_filter in event_filters:
            if (
                event_filter.field
                and event_filter.value is not None
                and event_filter.operator
                and event_filter.type
            ):
                filter_dict = {
                    "field": str(event_filter.field),
                    "value": str(event_filter.value),
                    "operator": event_filter.operator.value,
                    "type": event_filter.type.value,
                }
                filters.append(filter_dict)

        # Build request body according to OpenAPI spec
        request_body = {
            "project": project,
            "filters": filters,
            "limit": limit,
            "page": page,
        }

        response = await self.client.request_async(
            "POST", "/events/export", json=request_body
        )
        data = response.json()
        return self._process_data_dynamically(data.get("events", []), Event, "events")

    async def list_events_from_dict_async(
        self, event_filter: dict, limit: int = 100
    ) -> List[Event]:
        """List events asynchronously from filter dictionary (legacy method)."""
        params = {"limit": limit}
        params.update(event_filter)

        response = await self.client.request_async("GET", "/events", params=params)
        data = response.json()
        return self._process_data_dynamically(data.get("events", []), Event, "events")
