"""Unit tests for projects API."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateProjectRequest


class TestProjectsAPI:
    """Test projects API endpoints."""

    @pytest.fixture
    def api_key(self):
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key):
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def mock_project_data(self):
        return {
            "id": "project-123",
            "name": "test-project",
            "description": "Test project",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
        }

    def test_create_project_with_model(self, client, mock_project_data):
        """Test creating project using CreateProjectRequest model."""
        project_request = CreateProjectRequest(
            name="test-project", description="Test project"
        )

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.create_project(project_request)

            assert result.name == "test-project"
            assert result.description == "Test project"
            mock_request.assert_called_once()

    def test_create_project_from_dict(self, client, mock_project_data):
        """Test creating project from dictionary (legacy method)."""
        project_data = {"name": "test-project", "description": "Test project"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.create_project_from_dict(project_data)

            assert result.name == "test-project"
            assert result.description == "Test project"
            mock_request.assert_called_once()

    def test_get_project(self, client, mock_project_data):
        """Test getting project by ID."""
        project_id = "project-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.get_project(project_id)

            assert result.id == project_id
            assert result.name == "test-project"
            mock_request.assert_called_once_with("GET", f"/projects/{project_id}")

    def test_list_projects(self, client):
        """Test listing projects."""
        mock_data = {
            "projects": [
                {"id": "proj-1", "name": "project-1", "description": "Project 1"},
                {"id": "proj-2", "name": "project-2", "description": "Project 2"},
            ]
        }

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_request.return_value = mock_response

            result = client.projects.list_projects()

            assert len(result) == 2
            assert result[0].name == "project-1"
            assert result[1].name == "project-2"
            mock_request.assert_called_once_with(
                "GET", "/projects", params={"limit": 100}
            )

    def test_delete_project_success(self, client):
        """Test successful project deletion."""
        project_id = "project-123"

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            result = client.projects.delete_project(project_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/projects/{project_id}")

    def test_delete_project_failure(self, client):
        """Test failed project deletion."""
        project_id = "project-123"

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                client.projects.delete_project(project_id)

    @pytest.mark.asyncio
    async def test_create_project_async(self, client, mock_project_data):
        """Test creating project asynchronously."""
        project_request = CreateProjectRequest(
            name="test-project", description="Test project", type="test"
        )

        with patch.object(client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = await client.projects.create_project_async(project_request)

            assert result.name == "test-project"
            mock_request.assert_called_once()

    def test_update_project(self, client, mock_project_data):
        """Test updating project using from_dict method."""
        project_id = "project-123"
        update_data = {"description": "Updated description"}

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_project_data
            mock_request.return_value = mock_response

            result = client.projects.update_project_from_dict(project_id, update_data)

            assert result.name == "test-project"
            mock_request.assert_called_once_with(
                "PUT", f"/projects/{project_id}", json=update_data
            )
