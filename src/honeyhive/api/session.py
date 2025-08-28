"""Session API module for HoneyHive."""

from typing import Optional

from ..models import SessionStartRequest, Event
from .base import BaseAPI


class SessionStartResponse:
    """Response from starting a session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
    
    @property
    def id(self) -> str:
        """Alias for session_id for compatibility."""
        return self.session_id
    
    @property
    def _id(self) -> str:
        """Alias for session_id for compatibility."""
        return self.session_id


class SessionResponse:
    """Response from getting a session."""
    
    def __init__(self, event: Event):
        self.event = event


class SessionAPI(BaseAPI):
    """API for session operations."""

    def create_session(self, session_data: dict) -> SessionStartResponse:
        """Create a new session from session data dictionary."""
        # Handle both direct session data and nested session data
        if 'session' in session_data:
            request_data = session_data
        else:
            request_data = {"session": session_data}
        
        response = self.client.request(
            "POST", 
            "/session/start", 
            json=request_data
        )
        
        data = response.json()
        return SessionStartResponse(session_id=data["session_id"])

    def start_session(
        self, 
        project: str, 
        session_name: str, 
        source: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> SessionStartResponse:
        """Start a new session."""
        request_data = SessionStartRequest(
            project=project,
            session_name=session_name,
            source=source,
            session_id=session_id,
            **kwargs
        )
        
        response = self.client.request(
            "POST", 
            "/session/start", 
            json={"session": request_data.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        print(f"🔍 Session API response: {data}")
        
        # Check if session_id exists in the response
        if "session_id" in data:
            return SessionStartResponse(session_id=data["session_id"])
        elif "session" in data and "session_id" in data["session"]:
            return SessionStartResponse(session_id=data["session"]["session_id"])
        else:
            print(f"⚠️  Unexpected session response structure: {data}")
            # Try to find session_id in nested structures
            if "session" in data:
                session_data = data["session"]
                if isinstance(session_data, dict) and "session_id" in session_data:
                    return SessionStartResponse(session_id=session_data["session_id"])
            
            # If we still can't find it, raise an error with the full response
            raise ValueError(f"Session ID not found in response: {data}")

    async def start_session_async(
        self, 
        project: str, 
        session_name: str, 
        source: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> SessionStartResponse:
        """Start a new session asynchronously."""
        request_data = SessionStartRequest(
            project=project,
            session_name=session_name,
            source=source,
            session_id=session_id,
            **kwargs
        )
        
        response = await self.client.request_async(
            "POST", 
            "/session/start", 
            json={"session": request_data.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return SessionStartResponse(session_id=data["session_id"])

    def get_session(self, session_id: str) -> SessionResponse:
        """Get a session by ID."""
        response = self.client.request("GET", f"/session/{session_id}")
        data = response.json()
        return SessionResponse(event=Event(**data))

    async def get_session_async(self, session_id: str) -> SessionResponse:
        """Get a session by ID asynchronously."""
        response = await self.client.request_async("GET", f"/session/{session_id}")
        data = response.json()
        return SessionResponse(event=Event(**data))

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        try:
            response = self.client.request("DELETE", f"/session/{session_id}")
            return response.status_code == 200
        except Exception:
            return False

    async def delete_session_async(self, session_id: str) -> bool:
        """Delete a session by ID asynchronously."""
        try:
            response = await self.client.request_async("DELETE", f"/session/{session_id}")
            return response.status_code == 200
        except Exception:
            return False
