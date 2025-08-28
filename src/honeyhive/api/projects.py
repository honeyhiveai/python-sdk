"""Projects API module for HoneyHive."""

from typing import List, Optional

from ..models import Project, CreateProjectRequest, UpdateProjectRequest
from .base import BaseAPI


class ProjectsAPI(BaseAPI):
    """API for project operations."""

    def create_project(self, request: CreateProjectRequest) -> Project:
        """Create a new project."""
        response = self.client.request(
            "POST", 
            "/projects", 
            json={"project": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Project(**data)

    async def create_project_async(self, request: CreateProjectRequest) -> Project:
        """Create a new project asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/projects", 
            json={"project": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Project(**data)

    def get_project(self, project_id: str) -> Project:
        """Get a project by ID."""
        response = self.client.request("GET", f"/projects/{project_id}")
        data = response.json()
        return Project(**data)

    async def get_project_async(self, project_id: str) -> Project:
        """Get a project by ID asynchronously."""
        response = await self.client.request_async("GET", f"/projects/{project_id}")
        data = response.json()
        return Project(**data)

    def list_projects(self, limit: int = 100) -> List[Project]:
        """List projects."""
        params = {"limit": limit}
        
        response = self.client.request("GET", "/projects", params=params)
        data = response.json()
        return [Project(**project_data) for project_data in data.get("projects", [])]

    async def list_projects_async(self, limit: int = 100) -> List[Project]:
        """List projects asynchronously."""
        params = {"limit": limit}
        
        response = await self.client.request_async("GET", "/projects", params=params)
        data = response.json()
        return [Project(**project_data) for project_data in data.get("projects", [])]

    def update_project(self, project_id: str, request: UpdateProjectRequest) -> Project:
        """Update a project."""
        response = self.client.request(
            "PUT", 
            f"/projects/{project_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Project(**data)

    async def update_project_async(self, project_id: str, request: UpdateProjectRequest) -> Project:
        """Update a project asynchronously."""
        response = await self.client.request_async(
            "PUT", 
            f"/projects/{project_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Project(**data)

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        response = self.client.request("DELETE", f"/projects/{project_id}")
        return response.status_code == 200

    async def delete_project_async(self, project_id: str) -> bool:
        """Delete a project asynchronously."""
        response = await self.client.request_async("DELETE", f"/projects/{project_id}")
        return response.status_code == 200
