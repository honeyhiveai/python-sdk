"""Tools API module for HoneyHive."""

from typing import List, Optional

from ..models import CreateToolRequest, Tool, UpdateToolRequest
from .base import BaseAPI


class ToolsAPI(BaseAPI):
    """API for tool operations."""

    def create_tool(self, request: CreateToolRequest) -> Tool:
        """Create a new tool using CreateToolRequest model."""
        response = self.client.request(
            "POST", "/tools", json={"tool": request.model_dump(exclude_none=True)}
        )

        data = response.json()
        return Tool(**data)

    def create_tool_from_dict(self, tool_data: dict) -> Tool:
        """Create a new tool from dictionary (legacy method)."""
        response = self.client.request("POST", "/tools", json={"tool": tool_data})

        data = response.json()
        return Tool(**data)

    async def create_tool_async(self, request: CreateToolRequest) -> Tool:
        """Create a new tool asynchronously using CreateToolRequest model."""
        response = await self.client.request_async(
            "POST", "/tools", json={"tool": request.model_dump(exclude_none=True)}
        )

        data = response.json()
        return Tool(**data)

    async def create_tool_from_dict_async(self, tool_data: dict) -> Tool:
        """Create a new tool asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/tools", json={"tool": tool_data}
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
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = self.client.request("GET", "/tools", params=params)
        data = response.json()
        return [Tool(**tool_data) for tool_data in data.get("tools", [])]

    async def list_tools_async(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Tool]:
        """List tools asynchronously with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = await self.client.request_async("GET", "/tools", params=params)
        data = response.json()
        return [Tool(**tool_data) for tool_data in data.get("tools", [])]

    def update_tool(self, tool_id: str, request: UpdateToolRequest) -> Tool:
        """Update a tool using UpdateToolRequest model."""
        response = self.client.request(
            "PUT", f"/tools/{tool_id}", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return Tool(**data)

    def update_tool_from_dict(self, tool_id: str, tool_data: dict) -> Tool:
        """Update a tool from dictionary (legacy method)."""
        response = self.client.request("PUT", f"/tools/{tool_id}", json=tool_data)

        data = response.json()
        return Tool(**data)

    async def update_tool_async(self, tool_id: str, request: UpdateToolRequest) -> Tool:
        """Update a tool asynchronously using UpdateToolRequest model."""
        response = await self.client.request_async(
            "PUT", f"/tools/{tool_id}", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return Tool(**data)

    async def update_tool_from_dict_async(self, tool_id: str, tool_data: dict) -> Tool:
        """Update a tool asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/tools/{tool_id}", json=tool_data
        )

        data = response.json()
        return Tool(**data)

    def delete_tool(self, tool_id: str) -> bool:
        """Delete a tool by ID."""
        try:
            response = self.client.request("DELETE", f"/tools/{tool_id}")
            return response.status_code == 200
        except Exception:
            return False

    async def delete_tool_async(self, tool_id: str) -> bool:
        """Delete a tool by ID asynchronously."""
        try:
            response = await self.client.request_async("DELETE", f"/tools/{tool_id}")
            return response.status_code == 200
        except Exception:
            return False
