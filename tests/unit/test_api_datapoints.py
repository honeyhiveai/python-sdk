"""Comprehensive unit tests for HoneyHive DatapointsAPI module.

This module contains comprehensive unit tests for the DatapointsAPI class,
focusing on CRUD operations, async functionality, and error handling.

Tests cover:
- Datapoint creation (sync/async) with both model and dict inputs
- Datapoint retrieval (sync/async) with response format handling
- Datapoint listing (sync/async) with filtering parameters
- Datapoint updates (sync/async) with both model and dict inputs
- Error handling and edge cases
- Response format compatibility (new vs legacy API formats)
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.api.datapoints import DatapointsAPI
from honeyhive.models import CreateDatapointRequest, Datapoint, UpdateDatapointRequest


class TestDatapointsAPI:  # pylint: disable=too-many-public-methods
    """Test suite for DatapointsAPI class."""

    @pytest.fixture
    def api_key(self) -> str:
        """Provide test API key."""
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, api_key: str) -> HoneyHive:
        """Provide HoneyHive client instance."""
        return HoneyHive(api_key=api_key)

    @pytest.fixture
    def datapoints_api(self, client: HoneyHive) -> DatapointsAPI:
        """Provide DatapointsAPI instance."""
        return DatapointsAPI(client)

    @pytest.fixture
    def sample_datapoint_request(self) -> CreateDatapointRequest:
        """Provide sample CreateDatapointRequest."""
        return CreateDatapointRequest(
            project="test-project",
            inputs={"query": "What is AI?", "context": "Technology question"},
            ground_truth={"response": "AI is artificial intelligence"},
            metadata={"source": "unit_test", "version": "1.0"},
            linked_event="event-123",
            linked_datasets=["dataset-1", "dataset-2"],
            history=[{"role": "user", "content": "What is AI?"}],
        )

    @pytest.fixture
    def sample_datapoint_dict(self) -> Dict[str, Any]:
        """Provide sample datapoint dictionary."""
        return {
            "project": "test-project",
            "inputs": {"query": "What is AI?", "context": "Technology question"},
            "ground_truth": {"response": "AI is artificial intelligence"},
            "metadata": {"source": "unit_test", "version": "1.0"},
            "linked_event": "event-123",
            "linked_datasets": ["dataset-1", "dataset-2"],
            "history": [{"role": "user", "content": "What is AI?"}],
        }

    @pytest.fixture
    def sample_update_request(self) -> UpdateDatapointRequest:
        """Provide sample UpdateDatapointRequest."""
        return UpdateDatapointRequest(
            inputs={"query": "What is machine learning?"},
            ground_truth={"response": "ML is a subset of AI"},
            metadata={"source": "unit_test_updated", "version": "2.0"},
        )

    @pytest.fixture
    def mock_new_format_response(self) -> Dict[str, Any]:
        """Provide mock response in new API format."""
        return {
            "inserted": True,
            "result": {
                "insertedId": "datapoint-new-123",
                "acknowledged": True,
            },
        }

    @pytest.fixture
    def mock_legacy_format_response(self) -> Dict[str, Any]:
        """Provide mock response in legacy API format."""
        return {
            "_id": "datapoint-legacy-123",
            "project_id": "test-project",
            "inputs": {"query": "What is AI?"},
            "ground_truth": {"response": "AI is artificial intelligence"},
            "metadata": {"source": "unit_test"},
            "created_at": "2024-01-15T10:00:00Z",
        }

    @pytest.fixture
    def mock_get_response(self) -> Dict[str, Any]:
        """Provide mock response for get datapoint."""
        return {
            "datapoint": [
                {
                    "id": "datapoint-get-123",
                    "project_id": "test-project",
                    "inputs": {"query": "What is AI?"},
                    "ground_truth": {"response": "AI is artificial intelligence"},
                    "metadata": {"source": "unit_test"},
                    "created_at": "2024-01-15T10:00:00Z",
                }
            ]
        }

    @pytest.fixture
    def mock_list_response(self) -> Dict[str, Any]:
        """Provide mock response for list datapoints."""
        return {
            "datapoints": [
                {
                    "_id": "datapoint-1",
                    "project_id": "test-project",
                    "inputs": {"query": "Question 1"},
                    "ground_truth": {"response": "Answer 1"},
                },
                {
                    "_id": "datapoint-2",
                    "project_id": "test-project",
                    "inputs": {"query": "Question 2"},
                    "ground_truth": {"response": "Answer 2"},
                },
            ]
        }

    def test_datapoints_api_initialization(self, client: HoneyHive) -> None:
        """Test DatapointsAPI initialization."""
        datapoints_api = DatapointsAPI(client)

        assert datapoints_api.client == client
        assert hasattr(datapoints_api, "error_handler")
        assert datapoints_api._client_name == "DatapointsAPI"

    def test_create_datapoint_new_format(
        self,
        datapoints_api: DatapointsAPI,
        sample_datapoint_request: CreateDatapointRequest,
        mock_new_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint with new API response format."""
        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_new_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.create_datapoint(sample_datapoint_request)

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST",
                "/datapoints",
                json=sample_datapoint_request.model_dump(
                    mode="json", exclude_none=True
                ),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-new-123"
            assert result.inputs == sample_datapoint_request.inputs
            assert result.ground_truth == sample_datapoint_request.ground_truth
            assert result.metadata == sample_datapoint_request.metadata
            assert result.linked_event == sample_datapoint_request.linked_event
            assert result.linked_datasets == sample_datapoint_request.linked_datasets
            assert result.history == sample_datapoint_request.history

    def test_create_datapoint_legacy_format(
        self,
        datapoints_api: DatapointsAPI,
        sample_datapoint_request: CreateDatapointRequest,
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint with legacy API response format."""
        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.create_datapoint(sample_datapoint_request)

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST",
                "/datapoints",
                json=sample_datapoint_request.model_dump(
                    mode="json", exclude_none=True
                ),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"
            assert result.project_id == "test-project"

    def test_create_datapoint_from_dict_new_format(
        self,
        datapoints_api: DatapointsAPI,
        sample_datapoint_dict: Dict[str, Any],
        mock_new_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint from dict with new API response format."""
        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_new_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.create_datapoint_from_dict(sample_datapoint_dict)

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST", "/datapoints", json=sample_datapoint_dict
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-new-123"
            assert result.inputs == sample_datapoint_dict.get("inputs")
            assert result.ground_truth == sample_datapoint_dict.get("ground_truth")
            assert result.metadata == sample_datapoint_dict.get("metadata")

    def test_create_datapoint_from_dict_legacy_format(
        self,
        datapoints_api: DatapointsAPI,
        sample_datapoint_dict: Dict[str, Any],
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint from dict with legacy API response format."""
        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.create_datapoint_from_dict(sample_datapoint_dict)

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST", "/datapoints", json=sample_datapoint_dict
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"

    @pytest.mark.asyncio
    async def test_create_datapoint_async_new_format(
        self,
        datapoints_api: DatapointsAPI,
        sample_datapoint_request: CreateDatapointRequest,
        mock_new_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint asynchronously with new API response format."""
        with patch.object(datapoints_api.client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_new_format_response
            mock_request.return_value = mock_response

            result = await datapoints_api.create_datapoint_async(
                sample_datapoint_request
            )

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST",
                "/datapoints",
                json=sample_datapoint_request.model_dump(
                    mode="json", exclude_none=True
                ),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-new-123"
            assert result.inputs == sample_datapoint_request.inputs

    @pytest.mark.asyncio
    async def test_create_datapoint_from_dict_async_new_format(
        self,
        datapoints_api: DatapointsAPI,
        sample_datapoint_dict: Dict[str, Any],
        mock_new_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint from dict asynchronously with new format."""
        with patch.object(datapoints_api.client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_new_format_response
            mock_request.return_value = mock_response

            result = await datapoints_api.create_datapoint_from_dict_async(
                sample_datapoint_dict
            )

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST", "/datapoints", json=sample_datapoint_dict
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-new-123"

    def test_get_datapoint_success(
        self,
        datapoints_api: DatapointsAPI,
        mock_get_response: Dict[str, Any],
    ) -> None:
        """Test getting datapoint by ID successfully."""
        datapoint_id = "datapoint-get-123"

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_get_response
            mock_request.return_value = mock_response

            result = datapoints_api.get_datapoint(datapoint_id)

            # Verify request was made correctly
            mock_request.assert_called_once_with("GET", f"/datapoints/{datapoint_id}")

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-get-123"
            assert result.project_id == "test-project"

    def test_get_datapoint_fallback_format(
        self,
        datapoints_api: DatapointsAPI,
    ) -> None:
        """Test getting datapoint with fallback response format."""
        datapoint_id = "datapoint-fallback-123"
        fallback_response = {
            "_id": "datapoint-fallback-123",
            "project_id": "test-project",
            "inputs": {"query": "Fallback test"},
        }

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = fallback_response
            mock_request.return_value = mock_response

            result = datapoints_api.get_datapoint(datapoint_id)

            # Verify request was made correctly
            mock_request.assert_called_once_with("GET", f"/datapoints/{datapoint_id}")

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-fallback-123"

    @pytest.mark.asyncio
    async def test_get_datapoint_async_success(
        self,
        datapoints_api: DatapointsAPI,
        mock_get_response: Dict[str, Any],
    ) -> None:
        """Test getting datapoint by ID asynchronously."""
        datapoint_id = "datapoint-async-123"

        with patch.object(datapoints_api.client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_get_response
            mock_request.return_value = mock_response

            result = await datapoints_api.get_datapoint_async(datapoint_id)

            # Verify request was made correctly
            mock_request.assert_called_once_with("GET", f"/datapoints/{datapoint_id}")

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-get-123"

    def test_list_datapoints_no_filters(
        self,
        datapoints_api: DatapointsAPI,
        mock_list_response: Dict[str, Any],
    ) -> None:
        """Test listing datapoints without filters."""
        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_list_response
            mock_request.return_value = mock_response

            with patch.object(
                datapoints_api, "_process_data_dynamically"
            ) as mock_process:
                mock_process.return_value = [
                    Datapoint(_id="datapoint-1"),
                    Datapoint(_id="datapoint-2"),
                ]

                result = datapoints_api.list_datapoints()

                # Verify request was made correctly
                mock_request.assert_called_once_with("GET", "/datapoints", params={})

                # Verify data processing
                mock_process.assert_called_once_with(
                    mock_list_response["datapoints"], Datapoint, "datapoints"
                )

                # Verify response
                assert isinstance(result, list)
                assert len(result) == 2
                assert all(isinstance(dp, Datapoint) for dp in result)

    def test_list_datapoints_with_filters(
        self,
        datapoints_api: DatapointsAPI,
        mock_list_response: Dict[str, Any],
    ) -> None:
        """Test listing datapoints with project and dataset filters."""
        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_list_response
            mock_request.return_value = mock_response

            with patch.object(
                datapoints_api, "_process_data_dynamically"
            ) as mock_process:
                mock_process.return_value = [Datapoint(_id="datapoint-filtered")]

                result = datapoints_api.list_datapoints(
                    project="test-project", dataset="test-dataset"
                )

                # Verify request was made correctly
                # Legacy 'dataset' param is mapped to 'dataset_name' for non-NanoID strings
                mock_request.assert_called_once_with(
                    "GET",
                    "/datapoints",
                    params={
                        "project": "test-project",
                        "dataset_name": "test-dataset",
                    },
                )

                # Verify data processing
                mock_process.assert_called_once_with(
                    mock_list_response["datapoints"], Datapoint, "datapoints"
                )

                # Verify response
                assert isinstance(result, list)
                assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_datapoints_async_with_filters(
        self,
        datapoints_api: DatapointsAPI,
        mock_list_response: Dict[str, Any],
    ) -> None:
        """Test listing datapoints asynchronously with filters."""
        with patch.object(datapoints_api.client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_list_response
            mock_request.return_value = mock_response

            with patch.object(
                datapoints_api, "_process_data_dynamically"
            ) as mock_process:
                mock_process.return_value = [Datapoint(_id="datapoint-async")]

                result = await datapoints_api.list_datapoints_async(
                    project="async-project"
                )

                # Verify request was made correctly
                mock_request.assert_called_once_with(
                    "GET",
                    "/datapoints",
                    params={"project": "async-project"},
                )

                # Verify data processing
                mock_process.assert_called_once_with(
                    mock_list_response["datapoints"], Datapoint, "datapoints"
                )

                # Verify response
                assert isinstance(result, list)
                assert len(result) == 1

    def test_update_datapoint_with_model(
        self,
        datapoints_api: DatapointsAPI,
        sample_update_request: UpdateDatapointRequest,
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test updating datapoint using UpdateDatapointRequest model."""
        datapoint_id = "datapoint-update-123"

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.update_datapoint(
                datapoint_id, sample_update_request
            )

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "PUT",
                f"/datapoints/{datapoint_id}",
                json=sample_update_request.model_dump(mode="json", exclude_none=True),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"

    def test_update_datapoint_from_dict(
        self,
        datapoints_api: DatapointsAPI,
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test updating datapoint from dictionary."""
        datapoint_id = "datapoint-update-dict-123"
        update_data = {
            "inputs": {"query": "Updated question"},
            "metadata": {"updated": True},
        }

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.update_datapoint_from_dict(
                datapoint_id, update_data
            )

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "PUT", f"/datapoints/{datapoint_id}", json=update_data
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"

    @pytest.mark.asyncio
    async def test_update_datapoint_async_with_model(
        self,
        datapoints_api: DatapointsAPI,
        sample_update_request: UpdateDatapointRequest,
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test updating datapoint asynchronously using UpdateDatapointRequest model."""
        datapoint_id = "datapoint-async-update-123"

        with patch.object(datapoints_api.client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = await datapoints_api.update_datapoint_async(
                datapoint_id, sample_update_request
            )

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "PUT",
                f"/datapoints/{datapoint_id}",
                json=sample_update_request.model_dump(mode="json", exclude_none=True),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"

    @pytest.mark.asyncio
    async def test_update_datapoint_from_dict_async(
        self,
        datapoints_api: DatapointsAPI,
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test updating datapoint from dictionary asynchronously."""
        datapoint_id = "datapoint-async-dict-123"
        update_data = {
            "ground_truth": {"response": "Updated answer"},
            "metadata": {"async_updated": True},
        }

        with patch.object(datapoints_api.client, "request_async") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = await datapoints_api.update_datapoint_from_dict_async(
                datapoint_id, update_data
            )

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "PUT", f"/datapoints/{datapoint_id}", json=update_data
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"

    def test_create_datapoint_minimal_request(
        self,
        datapoints_api: DatapointsAPI,
        mock_new_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint with minimal required fields."""
        minimal_request = CreateDatapointRequest(
            project="minimal-project",
            inputs={"query": "Minimal test"},
        )

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_new_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.create_datapoint(minimal_request)

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "POST",
                "/datapoints",
                json=minimal_request.model_dump(mode="json", exclude_none=True),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-new-123"
            assert result.inputs == minimal_request.inputs

    def test_get_datapoint_empty_list_response(
        self,
        datapoints_api: DatapointsAPI,
    ) -> None:
        """Test getting datapoint with empty datapoint list in response."""
        datapoint_id = "datapoint-empty-123"
        empty_response: Dict[str, Any] = {"datapoint": []}

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = empty_response
            mock_request.return_value = mock_response

            result = datapoints_api.get_datapoint(datapoint_id)

            # Verify request was made correctly
            mock_request.assert_called_once_with("GET", f"/datapoints/{datapoint_id}")

            # Verify fallback response handling
            assert isinstance(result, Datapoint)

    def test_list_datapoints_empty_response(
        self,
        datapoints_api: DatapointsAPI,
    ) -> None:
        """Test listing datapoints with empty response."""
        empty_response: Dict[str, Any] = {"datapoints": []}

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = empty_response
            mock_request.return_value = mock_response

            with patch.object(
                datapoints_api, "_process_data_dynamically"
            ) as mock_process:
                mock_process.return_value = []

                result = datapoints_api.list_datapoints()

                # Verify request was made correctly
                mock_request.assert_called_once_with("GET", "/datapoints", params={})

                # Verify data processing
                mock_process.assert_called_once_with([], Datapoint, "datapoints")

                # Verify response
                assert isinstance(result, list)
                assert len(result) == 0

    def test_list_datapoints_missing_datapoints_key(
        self,
        datapoints_api: DatapointsAPI,
    ) -> None:
        """Test listing datapoints with missing datapoints key in response."""
        malformed_response = {"other_key": "other_value"}

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = malformed_response
            mock_request.return_value = mock_response

            with patch.object(
                datapoints_api, "_process_data_dynamically"
            ) as mock_process:
                mock_process.return_value = []

                result = datapoints_api.list_datapoints()

                # Verify request was made correctly
                mock_request.assert_called_once_with("GET", "/datapoints", params={})

                # Verify data processing with empty list
                mock_process.assert_called_once_with([], Datapoint, "datapoints")

                # Verify response
                assert isinstance(result, list)
                assert len(result) == 0

    def test_create_datapoint_from_dict_empty_dict(
        self,
        datapoints_api: DatapointsAPI,
        mock_new_format_response: Dict[str, Any],
    ) -> None:
        """Test creating datapoint from empty dictionary."""
        empty_dict: Dict[str, Any] = {}

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_new_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.create_datapoint_from_dict(empty_dict)

            # Verify request was made correctly
            mock_request.assert_called_once_with("POST", "/datapoints", json=empty_dict)

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-new-123"
            assert result.inputs is None
            assert result.ground_truth is None

    def test_update_datapoint_minimal_update(
        self,
        datapoints_api: DatapointsAPI,
        mock_legacy_format_response: Dict[str, Any],
    ) -> None:
        """Test updating datapoint with minimal update request."""
        datapoint_id = "datapoint-minimal-update-123"
        minimal_update = UpdateDatapointRequest(
            inputs={"query": "Minimal update"},
        )

        with patch.object(datapoints_api.client, "request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_legacy_format_response
            mock_request.return_value = mock_response

            result = datapoints_api.update_datapoint(datapoint_id, minimal_update)

            # Verify request was made correctly
            mock_request.assert_called_once_with(
                "PUT",
                f"/datapoints/{datapoint_id}",
                json=minimal_update.model_dump(mode="json", exclude_none=True),
            )

            # Verify response handling
            assert isinstance(result, Datapoint)
            assert result.field_id == "datapoint-legacy-123"
