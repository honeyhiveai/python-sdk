"""Events API module for HoneyHive."""

from typing import List, Optional, Dict, Any

from ..models import CreateEventRequest, EventFilter
from .base import BaseAPI


class CreateEventResponse:
    """Response from creating an event."""
    
    def __init__(self, event_id: str, success: bool):
        self.event_id = event_id
        self.success = success
    
    @property
    def id(self) -> str:
        """Alias for event_id for compatibility."""
        return self.event_id
    
    @property
    def _id(self) -> str:
        """Alias for event_id for compatibility."""
        return self.event_id


class UpdateEventRequest:
    """Request for updating an event."""
    
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
        self.event_id = event_id
        self.metadata = metadata
        self.feedback = feedback
        self.metrics = metrics
        self.outputs = outputs
        self.config = config
        self.user_properties = user_properties
        self.duration = duration


class BatchCreateEventRequest:
    """Request for creating multiple events."""
    
    def __init__(self, events: List[CreateEventRequest]):
        self.events = events


class BatchCreateEventResponse:
    """Response from creating multiple events."""
    
    def __init__(self, event_ids: List[str], success: bool):
        self.event_ids = event_ids
        self.success = success


class EventsAPI(BaseAPI):
    """API for event operations."""

    def create_event(self, event_data: dict) -> CreateEventResponse:
        """Create a new event from event data dictionary."""
        # Handle both direct event data and nested event data
        if 'event' in event_data:
            request_data = event_data
        else:
            request_data = {"event": event_data}
        
        response = self.client.request(
            "POST", 
            "/events", 
            json=request_data
        )
        
        data = response.json()
        return CreateEventResponse(
            event_id=data["event_id"],
            success=data["success"]
        )

    def create_event_from_request(self, event: CreateEventRequest) -> CreateEventResponse:
        """Create a new event from CreateEventRequest object."""
        response = self.client.request(
            "POST", 
            "/events", 
            json={"event": event.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return CreateEventResponse(
            event_id=data["event_id"],
            success=data["success"]
        )

    async def create_event_async(self, event_data: dict) -> CreateEventResponse:
        """Create a new event asynchronously from event data dictionary."""
        # Handle both direct event data and nested event data
        if 'event' in event_data:
            request_data = event_data
        else:
            request_data = {"event": event_data}
        
        response = await self.client.request_async(
            "POST", 
            "/events", 
            json=request_data
        )
        
        data = response.json()
        return CreateEventResponse(
            event_id=data["event_id"],
            success=data["success"]
        )

    async def create_event_from_request_async(self, event: CreateEventRequest) -> CreateEventResponse:
        """Create a new event asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/events", 
            json={"event": event.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return CreateEventResponse(
            event_id=data["event_id"],
            success=data["success"]
        )

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

    def create_event_batch(self, request: BatchCreateEventRequest) -> BatchCreateEventResponse:
        """Create multiple events."""
        events_data = [event.model_dump(exclude_none=True) for event in request.events]
        response = self.client.request("POST", "/events/batch", json={"events": events_data})
        
        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"],
            success=data["success"]
        )

    async def create_event_batch_async(self, request: BatchCreateEventRequest) -> BatchCreateEventResponse:
        """Create multiple events asynchronously."""
        events_data = [event.model_dump(exclude_none=True) for event in request.events]
        response = await self.client.request_async("POST", "/events/batch", json={"events": events_data})
        
        data = response.json()
        return BatchCreateEventResponse(
            event_ids=data["event_ids"],
            success=data["success"]
        )
