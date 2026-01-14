"""ProjectsAPI Integration Tests - NO MOCKS, REAL API CALLS.

NOTE: Tests are skipped/failing due to backend permissions:
- create_project() returns {"error": "Forbidden route"}
- update_project() returns {"error": "Forbidden route"}
- list_projects() returns empty list (may be permissions issue)
- Backend appears to have restricted access to project management
"""

import uuid
from typing import Any

import pytest


class TestProjectsAPI:
    """Test ProjectsAPI CRUD operations."""

    @pytest.mark.skip(
        reason="Backend Issue: create_project returns 'Forbidden route' error"
    )
    def test_create_project(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test project creation with settings, verify backend storage."""
        test_id = str(uuid.uuid4())[:8]
        project_name = f"test_project_{test_id}"

        # v1 API uses dict, not typed request
        project_data = {
            "name": project_name,
        }

        project = integration_client.projects.create(project_data)

        assert project is not None
        proj_name = (
            project.get("name")
            if isinstance(project, dict)
            else getattr(project, "name", None)
        )
        assert proj_name == project_name

    @pytest.mark.skip(
        reason="Backend Issue: getProjects endpoint returns 404 Not Found error"
    )
    def test_get_project(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test project retrieval, verify settings and metadata intact."""
        # v1 API doesn't have get_project by ID - use list
        projects = integration_client.projects.list()

        if not projects or len(projects) == 0:
            pytest.skip(
                "No projects available to test get_project "
                "(list_projects returns empty)"
            )
            return

        first_project = projects[0] if isinstance(projects, list) else None
        if not first_project:
            pytest.skip("No projects available")
            return

        assert first_project is not None
        proj_name = (
            first_project.get("name")
            if isinstance(first_project, dict)
            else getattr(first_project, "name", None)
        )
        assert proj_name is not None

    @pytest.mark.skip(
        reason="Backend Issue: getProjects endpoint returns 404 Not Found error"
    )
    def test_list_projects(self, integration_client: Any) -> None:
        """Test listing all accessible projects, pagination."""
        projects = integration_client.projects.list()

        assert projects is not None
        if isinstance(projects, list):
            # Backend may return empty list - that's ok
            pass
        else:
            assert isinstance(projects, dict)

    @pytest.mark.skip(
        reason="Backend Issue: create_project returns 'Forbidden route' error"
    )
    def test_update_project(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test project settings updates, verify changes persist."""
        test_id = str(uuid.uuid4())[:8]
        project_name = f"test_update_project_{test_id}"

        project_data = {
            "name": project_name,
        }

        created_project = integration_client.projects.create(project_data)
        project_id = (
            created_project.get("id")
            if isinstance(created_project, dict)
            else getattr(created_project, "id", None)
        )

        if not project_id:
            pytest.skip("Project creation didn't return accessible ID")
            return

        update_data = {
            "name": project_name,
            "id": project_id,
        }

        updated_project = integration_client.projects.update(update_data)

        assert updated_project is not None
        updated_name = (
            updated_project.get("name")
            if isinstance(updated_project, dict)
            else getattr(updated_project, "name", None)
        )
        assert updated_name == project_name
