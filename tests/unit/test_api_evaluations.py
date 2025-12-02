"""Unit tests for HoneyHive API evaluations module."""

import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from honeyhive.api.evaluations import EvaluationsAPI
from honeyhive.models import (
    CreateRunRequest,
    CreateRunResponse,
    DeleteRunResponse,
    GetRunResponse,
    GetRunsResponse,
    UpdateRunRequest,
    UpdateRunResponse,
)
from honeyhive.models.generated import Status, UUIDType


class TestEvaluationsAPI:  # pylint: disable=attribute-defined-outside-init
    """Test cases for EvaluationsAPI functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.mock_client = Mock()
        self.api = EvaluationsAPI(self.mock_client)

    def test_create_run_success(self) -> None:
        """Test successful run creation."""
        # Mock response data
        mock_response = Mock()
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "evaluation": {
                "run_id": str(uuid.uuid4()),
                "name": "test-run",
                "project": "test-project",
                "status": "pending",  # Changed from "created" to valid enum value
            },
        }
        self.mock_client.request.return_value = mock_response

        # Create request with required fields
        request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )

        # Call method
        result = self.api.create_run(request)

        # Verify result
        assert isinstance(result, CreateRunResponse)
        assert result.run_id is not None
        assert result.evaluation is not None
        assert result.evaluation.name == "test-run"  # pylint: disable=no-member

        # Verify client call
        self.mock_client.request.assert_called_once_with(
            "POST",
            "/runs",
            json={"run": request.model_dump(mode="json", exclude_none=True)},
        )

    def test_create_run_with_uuid_conversion(self) -> None:
        """Test run creation with UUID string conversion."""
        run_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.json.return_value = {"run_id": run_id}
        self.mock_client.request.return_value = mock_response

        request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )
        result = self.api.create_run(request)

        assert isinstance(result.run_id, UUIDType)
        assert str(result.run_id) == run_id

    def test_create_run_uuid_conversion_failure(self) -> None:
        """Test run creation with UUID conversion failure."""
        mock_response = Mock()
        mock_response.json.return_value = {"run_id": "invalid-uuid"}
        self.mock_client.request.return_value = mock_response

        request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )

        # Should raise an error when invalid UUID is provided
        with pytest.raises(Exception):
            self.api.create_run(request)

    def test_create_run_from_dict(self) -> None:
        """Test run creation from dictionary."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "evaluation": {
                "status": "pending"
            },  # Changed from "created" to valid enum value
        }
        self.mock_client.request.return_value = mock_response

        run_data = {
            "project": "test-project",
            "name": "test-run",
            "event_ids": [str(uuid.uuid4())],
            "description": "Test run",
        }

        result = self.api.create_run_from_dict(run_data)

        assert isinstance(result, CreateRunResponse)
        self.mock_client.request.assert_called_once_with(
            "POST", "/runs", json={"run": run_data}
        )

    @pytest.mark.asyncio
    async def test_create_run_async(self) -> None:
        """Test asynchronous run creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "evaluation": {
                "status": "pending"
            },  # Changed from "created" to valid enum value
        }
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )
        result = await self.api.create_run_async(request)

        assert isinstance(result, CreateRunResponse)
        self.mock_client.request_async.assert_called_once_with(
            "POST",
            "/runs",
            json={"run": request.model_dump(mode="json", exclude_none=True)},
        )

    @pytest.mark.asyncio
    async def test_create_run_from_dict_async(self) -> None:
        """Test asynchronous run creation from dictionary."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "evaluation": {
                "status": "pending"
            },  # Changed from "created" to valid enum value
        }
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        run_data = {
            "project": "test-project",
            "name": "test-run",
            "event_ids": [str(uuid.uuid4())],
        }
        result = await self.api.create_run_from_dict_async(run_data)

        assert isinstance(result, CreateRunResponse)
        self.mock_client.request_async.assert_called_once_with(
            "POST", "/runs", json={"run": run_data}
        )

    def test_get_run_success(self) -> None:
        """Test successful run retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "evaluation": {
                "run_id": str(uuid.uuid4()),
                "name": "test-run",
                "status": "completed",
            }
        }
        self.mock_client.request.return_value = mock_response

        run_id = "test-run-id"
        result = self.api.get_run(run_id)

        assert isinstance(result, GetRunResponse)
        assert result.evaluation is not None
        assert result.evaluation.name == "test-run"
        assert result.evaluation.status == Status.completed
        self.mock_client.request.assert_called_once_with("GET", f"/runs/{run_id}")

    @pytest.mark.asyncio
    async def test_get_run_async(self) -> None:
        """Test asynchronous run retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "evaluation": {
                "run_id": str(uuid.uuid4()),
                "name": "test-run",
                "status": "completed",
            }
        }
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        run_id = "test-run-id"
        result = await self.api.get_run_async(run_id)

        assert isinstance(result, GetRunResponse)
        self.mock_client.request_async.assert_called_once_with("GET", f"/runs/{run_id}")

    def test_list_runs_no_filters(self) -> None:
        """Test listing runs without filters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "evaluations": [
                {"run_id": str(uuid.uuid4()), "name": "run-1"},
                {"run_id": str(uuid.uuid4()), "name": "run-2"},
            ]
        }
        self.mock_client.request.return_value = mock_response

        result = self.api.list_runs()

        assert isinstance(result, GetRunsResponse)
        assert result.evaluations is not None
        assert len(result.evaluations) == 2
        self.mock_client.request.assert_called_once_with(
            "GET", "/runs", params={"limit": 100}
        )

    def test_list_runs_with_project_filter(self) -> None:
        """Test listing runs with project filter."""
        mock_response = Mock()
        mock_response.json.return_value = {"runs": []}
        self.mock_client.request.return_value = mock_response

        result = self.api.list_runs(project="test-project")

        assert isinstance(result, GetRunsResponse)
        self.mock_client.request.assert_called_once_with(
            "GET", "/runs", params={"limit": 100, "project": "test-project"}
        )

    def test_list_runs_with_custom_limit(self) -> None:
        """Test listing runs with custom limit."""
        mock_response = Mock()
        mock_response.json.return_value = {"runs": []}
        self.mock_client.request.return_value = mock_response

        result = self.api.list_runs(limit=50)

        assert isinstance(result, GetRunsResponse)
        self.mock_client.request.assert_called_once_with(
            "GET", "/runs", params={"limit": 50}
        )

    @pytest.mark.asyncio
    async def test_list_runs_async(self) -> None:
        """Test asynchronous listing of runs."""
        mock_response = Mock()
        mock_response.json.return_value = {"runs": []}
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        result = await self.api.list_runs_async(project="test-project", limit=25)

        assert isinstance(result, GetRunsResponse)
        self.mock_client.request_async.assert_called_once_with(
            "GET", "/runs", params={"limit": 25, "project": "test-project"}
        )

    def test_update_run_success(self) -> None:
        """Test successful run update."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "evaluation": {
                "run_id": str(uuid.uuid4()),
                "name": "updated-run",
                "status": "updated",
            }
        }
        self.mock_client.request.return_value = mock_response

        request = UpdateRunRequest(name="updated-run")
        run_id = "test-run-id"

        result = self.api.update_run(run_id, request)

        assert isinstance(result, UpdateRunResponse)
        assert result.evaluation is not None
        assert result.evaluation["name"] == "updated-run"
        self.mock_client.request.assert_called_once_with(
            "PUT", f"/runs/{run_id}", json=request.model_dump(exclude_none=True)
        )

    def test_update_run_from_dict(self) -> None:
        """Test run update from dictionary."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "name": "updated-run",
        }
        self.mock_client.request.return_value = mock_response

        run_data = {"name": "updated-run", "description": "Updated"}
        run_id = "test-run-id"

        result = self.api.update_run_from_dict(run_id, run_data)

        assert isinstance(result, UpdateRunResponse)
        self.mock_client.request.assert_called_once_with(
            "PUT", f"/runs/{run_id}", json=run_data
        )

    @pytest.mark.asyncio
    async def test_update_run_async(self) -> None:
        """Test asynchronous run update."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "name": "updated-run",
        }
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        request = UpdateRunRequest(name="updated-run")
        run_id = "test-run-id"

        result = await self.api.update_run_async(run_id, request)

        assert isinstance(result, UpdateRunResponse)
        self.mock_client.request_async.assert_called_once_with(
            "PUT", f"/runs/{run_id}", json=request.model_dump(exclude_none=True)
        )

    @pytest.mark.asyncio
    async def test_update_run_from_dict_async(self) -> None:
        """Test asynchronous run update from dictionary."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "run_id": str(uuid.uuid4()),
            "name": "updated-run",
        }
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        run_data = {"name": "updated-run"}
        run_id = "test-run-id"

        result = await self.api.update_run_from_dict_async(run_id, run_data)

        assert isinstance(result, UpdateRunResponse)
        self.mock_client.request_async.assert_called_once_with(
            "PUT", f"/runs/{run_id}", json=run_data
        )

    def test_delete_run_success(self) -> None:
        """Test successful run deletion."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": str(uuid.uuid4()), "deleted": True}
        self.mock_client.request.return_value = mock_response

        run_id = "test-run-id"
        result = self.api.delete_run(run_id)

        assert isinstance(result, DeleteRunResponse)
        assert result.deleted is True
        self.mock_client.request.assert_called_once_with("DELETE", f"/runs/{run_id}")

    @pytest.mark.asyncio
    async def test_delete_run_async_success(self) -> None:
        """Test successful asynchronous run deletion."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": str(uuid.uuid4()), "deleted": True}
        self.mock_client.request_async = AsyncMock(return_value=mock_response)

        run_id = "test-run-id"
        result = await self.api.delete_run_async(run_id)

        assert isinstance(result, DeleteRunResponse)
        assert result.deleted is True
        self.mock_client.request_async.assert_called_once_with(
            "DELETE", f"/runs/{run_id}"
        )


class TestEvaluationsAPIErrorScenarios:  # pylint: disable=attribute-defined-outside-init
    """Test error scenarios for EvaluationsAPI."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.mock_client = Mock()
        self.api = EvaluationsAPI(self.mock_client)

    def test_create_run_api_error(self) -> None:
        """Test run creation with API error."""
        self.mock_client.request.side_effect = Exception("API Error")

        request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )

        with pytest.raises(Exception, match="API Error"):
            self.api.create_run(request)

    @pytest.mark.asyncio
    async def test_create_run_async_api_error(self) -> None:
        """Test asynchronous run creation with API error."""
        self.mock_client.request_async.side_effect = Exception("API Error")

        request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )

        with pytest.raises(Exception, match="API Error"):
            await self.api.create_run_async(request)

    def test_get_run_not_found(self) -> None:
        """Test getting non-existent run."""
        self.mock_client.request.side_effect = Exception("Not Found")

        with pytest.raises(Exception, match="Not Found"):
            self.api.get_run("non-existent-id")

    @pytest.mark.asyncio
    async def test_get_run_async_not_found(self) -> None:
        """Test getting non-existent run asynchronously."""
        self.mock_client.request_async.side_effect = Exception("Not Found")

        with pytest.raises(Exception, match="Not Found"):
            await self.api.get_run_async("non-existent-id")

    def test_update_run_not_found(self) -> None:
        """Test updating non-existent run."""
        self.mock_client.request.side_effect = Exception("Not Found")

        request = UpdateRunRequest(name="updated-run")

        with pytest.raises(Exception, match="Not Found"):
            self.api.update_run("non-existent-id", request)

    @pytest.mark.asyncio
    async def test_update_run_async_not_found(self) -> None:
        """Test updating non-existent run asynchronously."""
        self.mock_client.request_async.side_effect = Exception("Not Found")

        request = UpdateRunRequest(name="updated-run")

        with pytest.raises(Exception, match="Not Found"):
            await self.api.update_run_async("non-existent-id", request)


class TestEvaluationsAPIIntegration:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for EvaluationsAPI."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.mock_client = Mock()
        self.api = EvaluationsAPI(self.mock_client)

    def test_full_run_lifecycle(self) -> None:
        """Test complete run lifecycle: create, get, update, delete."""
        run_id = str(uuid.uuid4())

        # Mock responses for each operation
        create_response = Mock()
        create_response.json.return_value = {
            "run_id": run_id,
            "evaluation": {"status": "pending"},
        }

        get_response = Mock()
        get_response.json.return_value = {
            "evaluation": {"run_id": run_id, "name": "test-run", "status": "pending"}
        }

        update_response = Mock()
        update_response.json.return_value = {
            "evaluation": {
                "run_id": run_id,
                "name": "updated-run",
                "status": "completed",
            }
        }

        delete_response = Mock()
        delete_response.json.return_value = {"id": run_id, "deleted": True}

        # Set up mock to return different responses for different calls
        self.mock_client.request.side_effect = [
            create_response,
            get_response,
            update_response,
            delete_response,
        ]

        # Create run
        create_request = CreateRunRequest(
            project="test-project", name="test-run", event_ids=[UUIDType(uuid.uuid4())]
        )
        created_run = self.api.create_run(create_request)
        assert isinstance(created_run, CreateRunResponse)

        # Get run
        retrieved_run = self.api.get_run(run_id)
        assert isinstance(retrieved_run, GetRunResponse)

        # Update run
        update_request = UpdateRunRequest(name="updated-run")
        updated_run = self.api.update_run(run_id, update_request)
        assert isinstance(updated_run, UpdateRunResponse)

        # Delete run
        deleted_run = self.api.delete_run(run_id)
        assert isinstance(deleted_run, DeleteRunResponse)

        # Verify all expected calls were made
        assert self.mock_client.request.call_count == 4
