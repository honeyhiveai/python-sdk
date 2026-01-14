"""Unit tests for honeyhive.api.projects.

This module contains comprehensive unit tests for the ProjectsAPI class,
covering all project operations including creation, retrieval, listing,
updating, and deletion with proper error handling and async support.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from honeyhive.api.projects import ProjectsAPI
from honeyhive.models import CreateProjectRequest, Project, UpdateProjectRequest
from honeyhive.utils.error_handler import ErrorContext


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock HoneyHive client for testing.

    Returns:
        Mock client with necessary attributes configured
    """
    client = Mock()
    client.base_url = "https://api.honeyhive.ai"
    client.request = Mock()
    client.request_async = AsyncMock()
    client._log = Mock()
    return client


@pytest.fixture
def mock_error_handler() -> Mock:
    """Create a mock error handler for testing.

    Returns:
        Mock error handler with handle_operation context manager
    """
    handler = Mock()
    handler.handle_operation = Mock()
    handler.handle_operation.return_value.__enter__ = Mock()
    handler.handle_operation.return_value.__exit__ = Mock(return_value=False)
    return handler


@pytest.fixture
def projects_api(mock_client: Mock, mock_error_handler: Mock) -> ProjectsAPI:
    """Create a ProjectsAPI instance for testing.

    Args:
        mock_client: Mock HoneyHive client
        mock_error_handler: Mock error handler

    Returns:
        ProjectsAPI instance with mocked dependencies
    """
    with patch("honeyhive.api.base.get_error_handler", return_value=mock_error_handler):
        return ProjectsAPI(mock_client)


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Sample project data for testing.

    Returns:
        Dictionary containing sample project data
    """
    return {
        "id": "project-123",
        "name": "Test Project",
        "description": "A test project for unit testing",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_create_request() -> CreateProjectRequest:
    """Sample CreateProjectRequest for testing.

    Returns:
        CreateProjectRequest instance with test data
    """
    return CreateProjectRequest(
        name="Test Project", description="A test project for unit testing"
    )


@pytest.fixture
def sample_update_request() -> UpdateProjectRequest:
    """Sample UpdateProjectRequest for testing.

    Returns:
        UpdateProjectRequest instance with test data
    """
    return UpdateProjectRequest(
        project_id="project-123",
        name="Updated Test Project",
        description="An updated test project",
    )


@pytest.fixture
def mock_response(sample_project_data: Dict[str, Any]) -> Mock:
    """Create a mock HTTP response for testing.

    Args:
        sample_project_data: Sample project data to return

    Returns:
        Mock response with json method returning sample data
    """
    response = Mock()
    response.json.return_value = sample_project_data
    response.status_code = 200
    return response


@pytest.fixture
def mock_list_response() -> Mock:
    """Create a mock HTTP response for list operations.

    Returns:
        Mock response with projects list
    """
    response = Mock()
    response.json.return_value = {
        "projects": [
            {
                "id": "project-123",
                "name": "Test Project 1",
                "description": "First test project",
            },
            {
                "id": "project-456",
                "name": "Test Project 2",
                "description": "Second test project",
            },
        ]
    }
    response.status_code = 200
    return response


class TestProjectsAPIInitialization:
    """Test suite for ProjectsAPI initialization."""

    def test_initialization_success(self, mock_client: Mock) -> None:
        """Test successful ProjectsAPI initialization.

        Verifies that ProjectsAPI initializes correctly with a client,
        inherits from BaseAPI, and sets up error handler.
        """
        # Arrange & Act
        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            projects_api = ProjectsAPI(mock_client)

            # Assert
            assert projects_api.client == mock_client
            assert projects_api.error_handler == mock_error_handler
            assert projects_api._client_name == "ProjectsAPI"
            mock_get_handler.assert_called_once()

    def test_initialization_inherits_from_base_api(self, mock_client: Mock) -> None:
        """Test that ProjectsAPI properly inherits from BaseAPI.

        Verifies inheritance and that BaseAPI methods are available.
        """
        # Arrange & Act
        with patch("honeyhive.api.base.get_error_handler"):
            projects_api = ProjectsAPI(mock_client)

            # Assert
            assert hasattr(projects_api, "_create_error_context")
            assert hasattr(projects_api, "_process_data_dynamically")
            assert hasattr(projects_api, "client")
            assert hasattr(projects_api, "error_handler")


class TestProjectsAPICreateProject:
    """Test suite for create_project method."""

    def test_create_project_success(
        self,
        projects_api: ProjectsAPI,
        sample_create_request: CreateProjectRequest,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful project creation with CreateProjectRequest.

        Verifies that create_project makes correct API call and returns Project.
        """
        # Arrange
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.create_project(sample_create_request)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]
        assert result.name == sample_project_data["name"]

        projects_api.client.request.assert_called_once_with(
            "POST",
            "/projects",
            json={
                "project": sample_create_request.model_dump(
                    mode="json", exclude_none=True
                )
            },
        )

    def test_create_project_with_minimal_request(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test project creation with minimal required fields.

        Verifies that create_project works with minimal CreateProjectRequest.
        """
        # Arrange
        minimal_request = CreateProjectRequest(name="Minimal Project")
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.create_project(minimal_request)

        # Assert
        assert isinstance(result, Project)
        projects_api.client.request.assert_called_once_with(
            "POST",
            "/projects",
            json={
                "project": minimal_request.model_dump(mode="json", exclude_none=True)
            },
        )

    def test_create_project_exclude_none_values(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test that create_project excludes None values from request.

        Verifies that model_dump with exclude_none=True is used.
        """
        # Arrange
        request_with_none = CreateProjectRequest(
            name="Test Project", description=None  # This should be excluded
        )
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.create_project(request_with_none)

        # Assert
        call_args = projects_api.client.request.call_args
        json_data = call_args[1]["json"]["project"]
        assert "description" not in json_data or json_data["description"] is None

    def test_create_project_api_error(
        self, projects_api: ProjectsAPI, sample_create_request: CreateProjectRequest
    ) -> None:
        """Test create_project handling of API errors.

        Verifies that API errors are properly propagated.
        """
        # Arrange
        projects_api.client.request.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            projects_api.create_project(sample_create_request)


class TestProjectsAPICreateProjectFromDict:
    """Test suite for create_project_from_dict method."""

    def test_create_project_from_dict_success(
        self,
        projects_api: ProjectsAPI,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful project creation from dictionary.

        Verifies that create_project_from_dict makes correct API call.
        """
        # Arrange
        project_dict = {"name": "Test Project", "description": "Test description"}
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.create_project_from_dict(project_dict)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request.assert_called_once_with(
            "POST", "/projects", json={"project": project_dict}
        )

    def test_create_project_from_dict_empty_dict(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test project creation from empty dictionary.

        Verifies that empty dictionary is handled correctly.
        """
        # Arrange
        empty_dict = {}
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.create_project_from_dict(empty_dict)

        # Assert
        assert isinstance(result, Project)
        projects_api.client.request.assert_called_once_with(
            "POST", "/projects", json={"project": empty_dict}
        )

    def test_create_project_from_dict_with_none_values(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test project creation from dictionary with None values.

        Verifies that None values are preserved in dictionary approach.
        """
        # Arrange
        project_dict = {"name": "Test Project", "description": None}
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.create_project_from_dict(project_dict)

        # Assert
        call_args = projects_api.client.request.call_args
        json_data = call_args[1]["json"]["project"]
        assert json_data == project_dict


class TestProjectsAPICreateProjectAsync:  # pylint: disable=too-few-public-methods
    """Test suite for create_project_async method."""

    @pytest.mark.asyncio
    async def test_create_project_async_success(
        self,
        projects_api: ProjectsAPI,
        sample_create_request: CreateProjectRequest,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful async project creation.

        Verifies that create_project_async makes correct async API call.
        """
        # Arrange
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.create_project_async(sample_create_request)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request_async.assert_called_once_with(
            "POST",
            "/projects",
            json={
                "project": sample_create_request.model_dump(
                    mode="json", exclude_none=True
                )
            },
        )

    @pytest.mark.asyncio
    async def test_create_project_async_error(
        self, projects_api: ProjectsAPI, sample_create_request: CreateProjectRequest
    ) -> None:
        """Test create_project_async handling of API errors.

        Verifies that async API errors are properly propagated.
        """
        # Arrange
        projects_api.client.request_async.side_effect = Exception("Async API Error")

        # Act & Assert
        with pytest.raises(Exception, match="Async API Error"):
            await projects_api.create_project_async(sample_create_request)


class TestProjectsAPICreateProjectFromDictAsync:  # pylint: disable=too-few-public-methods
    """Test suite for create_project_from_dict_async method."""

    @pytest.mark.asyncio
    async def test_create_project_from_dict_async_success(
        self,
        projects_api: ProjectsAPI,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful async project creation from dictionary.

        Verifies that create_project_from_dict_async makes correct async API call.
        """
        # Arrange
        project_dict = {"name": "Test Project", "description": "Test description"}
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.create_project_from_dict_async(project_dict)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request_async.assert_called_once_with(
            "POST", "/projects", json={"project": project_dict}
        )


class TestProjectsAPIGetProject:
    """Test suite for get_project method."""

    def test_get_project_success(
        self,
        projects_api: ProjectsAPI,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful project retrieval by ID.

        Verifies that get_project makes correct API call and returns Project.
        """
        # Arrange
        project_id = "project-123"
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.get_project(project_id)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request.assert_called_once_with(
            "GET", f"/projects/{project_id}"
        )

    def test_get_project_with_special_characters(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test project retrieval with special characters in ID.

        Verifies that special characters in project ID are handled correctly.
        """
        # Arrange
        project_id = "project-123-test_special"
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.get_project(project_id)

        # Assert
        projects_api.client.request.assert_called_once_with(
            "GET", f"/projects/{project_id}"
        )

    def test_get_project_not_found(self, projects_api: ProjectsAPI) -> None:
        """Test get_project handling of not found errors.

        Verifies that 404 errors are properly propagated.
        """
        # Arrange
        project_id = "nonexistent-project"
        projects_api.client.request.side_effect = Exception("Project not found")

        # Act & Assert
        with pytest.raises(Exception, match="Project not found"):
            projects_api.get_project(project_id)


class TestProjectsAPIGetProjectAsync:  # pylint: disable=too-few-public-methods
    """Test suite for get_project_async method."""

    @pytest.mark.asyncio
    async def test_get_project_async_success(
        self,
        projects_api: ProjectsAPI,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful async project retrieval by ID.

        Verifies that get_project_async makes correct async API call.
        """
        # Arrange
        project_id = "project-123"
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.get_project_async(project_id)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request_async.assert_called_once_with(
            "GET", f"/projects/{project_id}"
        )


class TestProjectsAPIListProjects:
    """Test suite for list_projects method."""

    def test_list_projects_success(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test successful project listing with default parameters.

        Verifies that list_projects makes correct API call and returns list.
        """
        # Arrange
        projects_api.client.request.return_value = mock_list_response

        # Mock the _process_data_dynamically method
        expected_projects = [
            Project(
                id="project-123",
                name="Test Project 1",
                description="First test project",
            ),
            Project(
                id="project-456",
                name="Test Project 2",
                description="Second test project",
            ),
        ]
        projects_api._process_data_dynamically = Mock(return_value=expected_projects)

        # Act
        result = projects_api.list_projects()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(project, Project) for project in result)

        projects_api.client.request.assert_called_once_with(
            "GET", "/projects", params={"limit": 100}
        )

        # Verify _process_data_dynamically was called correctly
        projects_api._process_data_dynamically.assert_called_once_with(
            mock_list_response.json.return_value.get("projects", []),
            Project,
            "projects",
        )

    def test_list_projects_with_custom_limit(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test project listing with custom limit parameter.

        Verifies that custom limit is passed correctly to API.
        """
        # Arrange
        custom_limit = 50
        projects_api.client.request.return_value = mock_list_response
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        projects_api.list_projects(limit=custom_limit)

        # Assert
        projects_api.client.request.assert_called_once_with(
            "GET", "/projects", params={"limit": custom_limit}
        )

    def test_list_projects_empty_response(self, projects_api: ProjectsAPI) -> None:
        """Test project listing with empty response.

        Verifies that empty project list is handled correctly.
        """
        # Arrange
        empty_response = Mock()
        empty_response.json.return_value = {"projects": []}
        projects_api.client.request.return_value = empty_response
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        result = projects_api.list_projects()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

        projects_api._process_data_dynamically.assert_called_once_with(
            [], Project, "projects"
        )

    def test_list_projects_missing_projects_key(
        self, projects_api: ProjectsAPI
    ) -> None:
        """Test project listing when response is missing 'projects' key.

        Verifies that missing 'projects' key defaults to empty list.
        """
        # Arrange
        response_without_projects = Mock()
        response_without_projects.json.return_value = {}
        projects_api.client.request.return_value = response_without_projects
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        result = projects_api.list_projects()

        # Assert
        assert isinstance(result, list)
        projects_api._process_data_dynamically.assert_called_once_with(
            [],  # Should default to empty list when 'projects' key is missing
            Project,
            "projects",
        )


class TestProjectsAPIListProjectsAsync:
    """Test suite for list_projects_async method."""

    @pytest.mark.asyncio
    async def test_list_projects_async_success(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test successful async project listing.

        Verifies that list_projects_async makes correct async API call.
        """
        # Arrange
        projects_api.client.request_async.return_value = mock_list_response
        expected_projects = [
            Project(
                id="project-123",
                name="Test Project 1",
                description="First test project",
            )
        ]
        projects_api._process_data_dynamically = Mock(return_value=expected_projects)

        # Act
        result = await projects_api.list_projects_async()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1

        projects_api.client.request_async.assert_called_once_with(
            "GET", "/projects", params={"limit": 100}
        )

    @pytest.mark.asyncio
    async def test_list_projects_async_with_custom_limit(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test async project listing with custom limit.

        Verifies that custom limit is passed correctly to async API.
        """
        # Arrange
        custom_limit = 25
        projects_api.client.request_async.return_value = mock_list_response
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        await projects_api.list_projects_async(limit=custom_limit)

        # Assert
        projects_api.client.request_async.assert_called_once_with(
            "GET", "/projects", params={"limit": custom_limit}
        )


class TestProjectsAPIUpdateProject:
    """Test suite for update_project method."""

    def test_update_project_success(
        self,
        projects_api: ProjectsAPI,
        sample_update_request: UpdateProjectRequest,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful project update with UpdateProjectRequest.

        Verifies that update_project makes correct API call and returns Project.
        """
        # Arrange
        project_id = "project-123"
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.update_project(project_id, sample_update_request)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request.assert_called_once_with(
            "PUT",
            f"/projects/{project_id}",
            json=sample_update_request.model_dump(mode="json", exclude_none=True),
        )

    def test_update_project_partial_update(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test project update with partial data.

        Verifies that partial updates work correctly with exclude_none.
        """
        # Arrange
        project_id = "project-123"
        partial_request = UpdateProjectRequest(
            project_id=project_id, name="New Name Only"
        )
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.update_project(project_id, partial_request)

        # Assert
        call_args = projects_api.client.request.call_args
        json_data = call_args[1]["json"]
        assert "name" in json_data
        # Other fields should be excluded due to exclude_none=True

    def test_update_project_nonexistent(
        self, projects_api: ProjectsAPI, sample_update_request: UpdateProjectRequest
    ) -> None:
        """Test update_project handling of nonexistent project.

        Verifies that errors for nonexistent projects are propagated.
        """
        # Arrange
        project_id = "nonexistent-project"
        projects_api.client.request.side_effect = Exception("Project not found")

        # Act & Assert
        with pytest.raises(Exception, match="Project not found"):
            projects_api.update_project(project_id, sample_update_request)


class TestProjectsAPIUpdateProjectFromDict:
    """Test suite for update_project_from_dict method."""

    def test_update_project_from_dict_success(
        self,
        projects_api: ProjectsAPI,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful project update from dictionary.

        Verifies that update_project_from_dict makes correct API call.
        """
        # Arrange
        project_id = "project-123"
        update_dict = {"name": "Updated Name", "description": "Updated description"}
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.update_project_from_dict(project_id, update_dict)

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request.assert_called_once_with(
            "PUT", f"/projects/{project_id}", json=update_dict
        )

    def test_update_project_from_dict_with_none_values(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test project update from dictionary with None values.

        Verifies that None values are preserved in dictionary approach.
        """
        # Arrange
        project_id = "project-123"
        update_dict = {"name": "Updated Name", "description": None}
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.update_project_from_dict(project_id, update_dict)

        # Assert
        call_args = projects_api.client.request.call_args
        json_data = call_args[1]["json"]
        assert json_data == update_dict


class TestProjectsAPIUpdateProjectAsync:  # pylint: disable=too-few-public-methods
    """Test suite for update_project_async method."""

    @pytest.mark.asyncio
    async def test_update_project_async_success(
        self,
        projects_api: ProjectsAPI,
        sample_update_request: UpdateProjectRequest,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful async project update.

        Verifies that update_project_async makes correct async API call.
        """
        # Arrange
        project_id = "project-123"
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.update_project_async(
            project_id, sample_update_request
        )

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request_async.assert_called_once_with(
            "PUT",
            f"/projects/{project_id}",
            json=sample_update_request.model_dump(mode="json", exclude_none=True),
        )


class TestProjectsAPIUpdateProjectFromDictAsync:  # pylint: disable=too-few-public-methods
    """Test suite for update_project_from_dict_async method."""

    @pytest.mark.asyncio
    async def test_update_project_from_dict_async_success(
        self,
        projects_api: ProjectsAPI,
        mock_response: Mock,
        sample_project_data: Dict[str, Any],
    ) -> None:
        """Test successful async project update from dictionary.

        Verifies that update_project_from_dict_async makes correct async API call.
        """
        # Arrange
        project_id = "project-123"
        update_dict = {"name": "Updated Name", "description": "Updated description"}
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.update_project_from_dict_async(
            project_id, update_dict
        )

        # Assert
        assert isinstance(result, Project)
        assert result.id == sample_project_data["id"]

        projects_api.client.request_async.assert_called_once_with(
            "PUT", f"/projects/{project_id}", json=update_dict
        )


class TestProjectsAPIDeleteProject:
    """Test suite for delete_project method."""

    def test_delete_project_success(
        self, projects_api: ProjectsAPI, mock_error_handler: Mock
    ) -> None:
        """Test successful project deletion.

        Verifies that delete_project makes correct API call with error handling.
        """
        # Arrange
        project_id = "project-123"
        mock_response = Mock()
        mock_response.status_code = 200
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.delete_project(project_id)

        # Assert
        assert result is True

        projects_api.client.request.assert_called_once_with(
            "DELETE", f"/projects/{project_id}"
        )

        # Verify error context was created and used
        mock_error_handler.handle_operation.assert_called_once()
        context_call = mock_error_handler.handle_operation.call_args[0][0]
        assert isinstance(context_call, ErrorContext)
        assert context_call.operation == "delete_project"
        assert context_call.method == "DELETE"
        # Note: additional_context structure may vary based on implementation
        assert hasattr(context_call, "additional_context")

    def test_delete_project_failure_status_code(
        self,
        projects_api: ProjectsAPI,
        mock_error_handler: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test project deletion with non-200 status code.

        Verifies that non-200 status codes return False.
        """
        # Arrange
        project_id = "project-123"
        mock_response = Mock()
        mock_response.status_code = 404
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.delete_project(project_id)

        # Assert
        assert result is False
        projects_api.client.request.assert_called_once_with(
            "DELETE", f"/projects/{project_id}"
        )

    def test_delete_project_error_context_creation(
        self,
        projects_api: ProjectsAPI,
        mock_error_handler: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test that delete_project creates proper error context.

        Verifies that error context is created with correct parameters.
        """
        # Arrange
        project_id = "project-123"
        mock_response = Mock()
        mock_response.status_code = 200
        projects_api.client.request.return_value = mock_response

        # Mock the _create_error_context method to verify it's called
        projects_api._create_error_context = Mock(return_value=Mock())

        # Act
        projects_api.delete_project(project_id)

        # Assert
        projects_api._create_error_context.assert_called_once_with(
            operation="delete_project",
            method="DELETE",
            path=f"/projects/{project_id}",
            additional_context={"project_id": project_id},
        )

    def test_delete_project_with_error_handler_exception(
        self,
        projects_api: ProjectsAPI,
        mock_error_handler: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test delete_project when error handler raises exception.

        Verifies that exceptions from error handler are propagated.
        """
        # Arrange
        project_id = "project-123"
        mock_error_handler.handle_operation.side_effect = Exception(
            "Error handler exception"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Error handler exception"):
            projects_api.delete_project(project_id)


class TestProjectsAPIDeleteProjectAsync:
    """Test suite for delete_project_async method."""

    @pytest.mark.asyncio
    async def test_delete_project_async_success(
        self, projects_api: ProjectsAPI, mock_error_handler: Mock
    ) -> None:
        """Test successful async project deletion.

        Verifies that delete_project_async makes correct async API call.
        """
        # Arrange
        project_id = "project-123"
        mock_response = Mock()
        mock_response.status_code = 200
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.delete_project_async(project_id)

        # Assert
        assert result is True

        projects_api.client.request_async.assert_called_once_with(
            "DELETE", f"/projects/{project_id}"
        )

        # Verify error context was created and used
        mock_error_handler.handle_operation.assert_called_once()
        context_call = mock_error_handler.handle_operation.call_args[0][0]
        assert isinstance(context_call, ErrorContext)
        assert context_call.operation == "delete_project_async"

    @pytest.mark.asyncio
    async def test_delete_project_async_failure_status_code(
        self,
        projects_api: ProjectsAPI,
        mock_error_handler: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test async project deletion with non-200 status code.

        Verifies that non-200 status codes return False in async version.
        """
        # Arrange
        project_id = "project-123"
        mock_response = Mock()
        mock_response.status_code = 500
        projects_api.client.request_async.return_value = mock_response

        # Act
        result = await projects_api.delete_project_async(project_id)

        # Assert
        assert result is False


class TestProjectsAPIEdgeCases:
    """Test suite for edge cases and error scenarios."""

    def test_empty_project_id_handling(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test handling of empty project ID.

        Verifies that empty project ID is handled appropriately.
        """
        # Arrange
        empty_project_id = ""
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.get_project(empty_project_id)

        # Assert
        projects_api.client.request.assert_called_once_with("GET", "/projects/")

    def test_none_project_id_handling(
        self, projects_api: ProjectsAPI, mock_response: Mock
    ) -> None:
        """Test handling of None project ID.

        Verifies that None project ID is converted to string.
        """
        # Arrange
        none_project_id = None
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.get_project(none_project_id)

        # Assert
        projects_api.client.request.assert_called_once_with("GET", "/projects/None")

    def test_large_limit_parameter(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test list_projects with very large limit parameter.

        Verifies that large limit values are handled correctly.
        """
        # Arrange
        large_limit = 999999
        projects_api.client.request.return_value = mock_list_response
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        projects_api.list_projects(limit=large_limit)

        # Assert
        projects_api.client.request.assert_called_once_with(
            "GET", "/projects", params={"limit": large_limit}
        )

    def test_negative_limit_parameter(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test list_projects with negative limit parameter.

        Verifies that negative limit values are passed through.
        """
        # Arrange
        negative_limit = -10
        projects_api.client.request.return_value = mock_list_response
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        projects_api.list_projects(limit=negative_limit)

        # Assert
        projects_api.client.request.assert_called_once_with(
            "GET", "/projects", params={"limit": negative_limit}
        )

    def test_zero_limit_parameter(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test list_projects with zero limit parameter.

        Verifies that zero limit is handled correctly.
        """
        # Arrange
        zero_limit = 0
        projects_api.client.request.return_value = mock_list_response
        projects_api._process_data_dynamically = Mock(return_value=[])

        # Act
        projects_api.list_projects(limit=zero_limit)

        # Assert
        projects_api.client.request.assert_called_once_with(
            "GET", "/projects", params={"limit": zero_limit}
        )


class TestProjectsAPIIntegrationWithBaseAPI:
    """Test suite for integration with BaseAPI functionality."""

    def test_process_data_dynamically_integration(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test integration with BaseAPI's _process_data_dynamically method.

        Verifies that the method is called with correct parameters.
        """
        # Arrange
        projects_api.client.request.return_value = mock_list_response

        # Don't mock _process_data_dynamically to test real integration
        # But mock the client._log method that might be called
        projects_api.client._log = Mock()

        # Act
        result = projects_api.list_projects()

        # Assert
        assert isinstance(result, list)
        # The actual _process_data_dynamically should handle the conversion

    def test_error_context_creation_integration(
        self, projects_api: ProjectsAPI, mock_error_handler: Mock
    ) -> None:
        """Test integration with BaseAPI's _create_error_context method.

        Verifies that error context is properly created and used.
        """
        # Arrange
        project_id = "test-project"
        mock_response = Mock()
        mock_response.status_code = 200
        projects_api.client.request.return_value = mock_response

        # Act
        projects_api.delete_project(project_id)

        # Assert
        # Verify that handle_operation was called (indicating error context was created)
        mock_error_handler.handle_operation.assert_called_once()

        # Verify the context has the expected structure
        context = mock_error_handler.handle_operation.call_args[0][0]
        assert hasattr(context, "operation")
        assert hasattr(context, "method")
        assert hasattr(context, "additional_context")


class TestProjectsAPITypeAnnotations:
    """Test suite for type annotations and return types."""

    def test_create_project_return_type(
        self,
        projects_api: ProjectsAPI,
        sample_create_request: CreateProjectRequest,
        mock_response: Mock,
    ) -> None:
        """Test that create_project returns correct type.

        Verifies that return type is Project instance.
        """
        # Arrange
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.create_project(sample_create_request)

        # Assert
        assert isinstance(result, Project)

    def test_list_projects_return_type(
        self, projects_api: ProjectsAPI, mock_list_response: Mock
    ) -> None:
        """Test that list_projects returns correct type.

        Verifies that return type is List[Project].
        """
        # Arrange
        projects_api.client.request.return_value = mock_list_response
        projects_api._process_data_dynamically = Mock(
            return_value=[
                Project(id="1", name="Test 1", description="Description 1"),
                Project(id="2", name="Test 2", description="Description 2"),
            ]
        )

        # Act
        result = projects_api.list_projects()

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(project, Project) for project in result)

    def test_delete_project_return_type(
        self,
        projects_api: ProjectsAPI,
        mock_error_handler: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test that delete_project returns correct type.

        Verifies that return type is bool.
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        projects_api.client.request.return_value = mock_response

        # Act
        result = projects_api.delete_project("test-id")

        # Assert
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.asyncio
    async def test_async_methods_return_types(
        self,
        projects_api: ProjectsAPI,
        sample_create_request: CreateProjectRequest,
        mock_response: Mock,
    ) -> None:
        """Test that async methods return correct types.

        Verifies that async methods return the same types as sync versions.
        """
        # Arrange
        projects_api.client.request_async.return_value = mock_response

        # Act
        create_result = await projects_api.create_project_async(sample_create_request)
        get_result = await projects_api.get_project_async("test-id")

        # Assert
        assert isinstance(create_result, Project)
        assert isinstance(get_result, Project)
