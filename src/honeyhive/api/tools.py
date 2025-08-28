"""Tools API module for HoneyHive."""

from typing import List, Optional

from ..models import Tool, CreateToolRequest, UpdateToolRequest
from .base import BaseAPI


class ToolsAPI(BaseAPI):
    """API for tool operations."""

    def create_tool(self, request: CreateToolRequest) -> Tool:
        """Create a new tool."""
        response = self.client.request(
            "POST", 
            "/tools", 
            json={"tool": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Tool(**data)

    async def create_tool_async(self, request: CreateToolRequest) -> Tool:
        """Create a new tool asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/tools", 
            json={"tool": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Tool(**data)

    def get_tool(self, tool_id: str) -> Tool:
        """Get a tool by ID."""
        response = self.client.request("GET", f"/tools/{tool_id}")
        data = response.json()
        return Tool(**data)

    async def get_tool_async(self, tool_id: str) -> Tool:
        """Get a tool by ID asynchronously."""
        response = await self.client.request_async("GET", f"/tools/{tool_id}")
        data = response.json()
        return Tool(**data)

    def list_tools(self, project: Optional[str] = None, limit: int = 100) -> List[Tool]:
        """List tools with optional filtering."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        
        response = self.client.request("GET", "/tools", params=params)
        data = response.json()
        return [Tool(**tool_data) for tool_data in data.get("tools", [])]

    async def list_tools_async(self, project: Optional[str] = None, limit: int = 100) -> List[Tool]:
        """List tools with optional filtering asynchronously."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        
        response = await self.client.request_async("GET", "/tools", params=params)
        data = response.json()
        return [Tool(**tool_data) for tool_data in data.get("tools", [])]

    def update_tool(self, tool_id: str, request: UpdateToolRequest) -> Tool:
        """Update a tool."""
        response = self.client.request(
            "PUT", 
            f"/tools/{tool_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Tool(**data)

    async def update_tool_async(self, tool_id: str, request: UpdateToolRequest) -> Tool:
        """Update a tool asynchronously."""
        response = await self.client.request_async(
            "PUT", 
            f"/tools/{tool_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Tool(**data)

    def delete_tool(self, tool_id: str) -> bool:
        """Delete a tool."""
        response = self.client.request("DELETE", f"/tools/{tool_id}")
        return response.status_code == 200

    async def delete_tool_async(self, tool_id: str) -> bool:
        """Delete a tool asynchronously."""
        response = await self.client.request_async("DELETE", f"/tools/{tool_id}")
        return response.status_code == 200
