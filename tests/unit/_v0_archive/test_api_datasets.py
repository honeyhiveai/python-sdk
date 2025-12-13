"""Unit tests for honeyhive.api.datasets.

This module contains comprehensive unit tests for the DatasetsAPI class,
testing all CRUD operations for dataset management with proper mocking.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from unittest.mock import Mock, patch

import pytest

from honeyhive.api.datasets import DatasetsAPI
from honeyhive.models import CreateDatasetRequest, Dataset, DatasetUpdate


class TestDatasetsAPIInitialization:
    """Test DatasetsAPI initialization."""

    def test_initialization_with_client(self, mock_client: Mock) -> None:
        """Test DatasetsAPI initialization with client."""
        # Act
        datasets_api = DatasetsAPI(mock_client)

        # Assert
        assert datasets_api.client == mock_client
        assert hasattr(datasets_api, "error_handler")
        assert datasets_api._client_name == "DatasetsAPI"

    def test_initialization_inherits_from_base_api(self, mock_client: Mock) -> None:
        """Test DatasetsAPI inherits properly from BaseAPI."""
        # Act
        datasets_api = DatasetsAPI(mock_client)

        # Assert
        assert hasattr(datasets_api, "_create_error_context")
        assert hasattr(datasets_api, "_process_data_dynamically")
        assert hasattr(datasets_api, "error_handler")


class TestDatasetsAPICreateDataset:
    """Test dataset creation methods."""

    def test_create_dataset_new_format_response(self, mock_client: Mock) -> None:
        """Test create_dataset with new API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        request = CreateDatasetRequest(
            project="test-project",
            name="test-dataset",
            description="Test dataset description",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "inserted": True,
            "result": {"insertedId": "dataset-123"},
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.create_dataset(request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "test-project"
            assert result.name == "test-dataset"
            assert result.description == "Test dataset description"

            mock_client.request.assert_called_once_with(
                "POST",
                "/datasets",
                json={
                    "project": "test-project",
                    "name": "test-dataset",
                    "description": "Test dataset description",
                },
            )

    def test_create_dataset_legacy_format_response(self, mock_client: Mock) -> None:
        """Test create_dataset with legacy API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        request = CreateDatasetRequest(
            project="test-project",
            name="test-dataset",
            description="Test dataset description",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "project": "test-project",
            "name": "test-dataset",
            "description": "Test dataset description",
            "id": "dataset-456",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.create_dataset(request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "test-project"
            assert result.name == "test-dataset"
            assert result.description == "Test dataset description"

    def test_create_dataset_from_dict_new_format(self, mock_client: Mock) -> None:
        """Test create_dataset_from_dict with new API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_data = {
            "project": "test-project",
            "name": "test-dataset",
            "description": "Test dataset description",
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "inserted": True,
            "result": {"insertedId": "dataset-789"},
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.create_dataset_from_dict(dataset_data)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "test-project"
            assert result.name == "test-dataset"
            assert result.description == "Test dataset description"

            mock_client.request.assert_called_once_with(
                "POST", "/datasets", json=dataset_data
            )

    def test_create_dataset_from_dict_legacy_format(self, mock_client: Mock) -> None:
        """Test create_dataset_from_dict with legacy API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_data = {
            "project": "test-project",
            "name": "test-dataset",
            "description": "Test dataset description",
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "project": "test-project",
            "name": "test-dataset",
            "description": "Test dataset description",
            "id": "dataset-legacy",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.create_dataset_from_dict(dataset_data)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "test-project"
            assert result.name == "test-dataset"
            assert result.description == "Test dataset description"

    def test_create_dataset_from_dict_missing_fields(self, mock_client: Mock) -> None:
        """Test create_dataset_from_dict with missing optional fields."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_data = {"name": "test-dataset"}

        mock_response = Mock()
        mock_response.json.return_value = {
            "inserted": True,
            "result": {"insertedId": "dataset-minimal"},
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.create_dataset_from_dict(dataset_data)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project is None
            assert result.name == "test-dataset"
            assert result.description is None


class TestDatasetsAPICreateDatasetAsync:
    """Test async dataset creation methods."""

    @pytest.mark.asyncio
    async def test_create_dataset_async_new_format(self, mock_client: Mock) -> None:
        """Test create_dataset_async with new API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        request = CreateDatasetRequest(
            project="async-project",
            name="async-dataset",
            description="Async test dataset",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "inserted": True,
            "result": {"insertedId": "async-dataset-123"},
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.create_dataset_async(request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "async-project"
            assert result.name == "async-dataset"
            assert result.description == "Async test dataset"

            mock_client.request_async.assert_called_once_with(
                "POST",
                "/datasets",
                json={
                    "project": "async-project",
                    "name": "async-dataset",
                    "description": "Async test dataset",
                },
            )

    @pytest.mark.asyncio
    async def test_create_dataset_async_legacy_format(self, mock_client: Mock) -> None:
        """Test create_dataset_async with legacy API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        request = CreateDatasetRequest(
            project="async-project",
            name="async-dataset",
            description="Async test dataset",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "project": "async-project",
            "name": "async-dataset",
            "description": "Async test dataset",
            "id": "async-legacy-456",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.create_dataset_async(request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "async-project"
            assert result.name == "async-dataset"
            assert result.description == "Async test dataset"

    @pytest.mark.asyncio
    async def test_create_dataset_from_dict_async_new_format(
        self, mock_client: Mock
    ) -> None:
        """Test create_dataset_from_dict_async with new API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_data = {
            "project": "async-project",
            "name": "async-dict-dataset",
            "description": "Async dict dataset",
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "inserted": True,
            "result": {"insertedId": "async-dict-789"},
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.create_dataset_from_dict_async(dataset_data)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "async-project"
            assert result.name == "async-dict-dataset"
            assert result.description == "Async dict dataset"

            mock_client.request_async.assert_called_once_with(
                "POST", "/datasets", json=dataset_data
            )

    @pytest.mark.asyncio
    async def test_create_dataset_from_dict_async_legacy_format(
        self, mock_client: Mock
    ) -> None:
        """Test create_dataset_from_dict_async with legacy API response format."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_data = {
            "project": "async-project",
            "name": "async-dict-dataset",
            "description": "Async dict dataset",
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "project": "async-project",
            "name": "async-dict-dataset",
            "description": "Async dict dataset",
            "id": "async-dict-legacy",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.create_dataset_from_dict_async(dataset_data)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "async-project"
            assert result.name == "async-dict-dataset"
            assert result.description == "Async dict dataset"


class TestDatasetsAPIGetDataset:
    """Test dataset retrieval methods."""

    def test_get_dataset_success(self, mock_client: Mock) -> None:
        """Test get_dataset with successful response."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "dataset-123"

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {
                    "id": "dataset-123",
                    "project": "test-project",
                    "name": "retrieved-dataset",
                    "description": "Retrieved dataset description",
                }
            ]
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.get_dataset(dataset_id)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "test-project"
            assert result.name == "retrieved-dataset"
            assert result.description == "Retrieved dataset description"

            mock_client.request.assert_called_once_with(
                "GET", "/datasets", params={"dataset_id": dataset_id}
            )

    @pytest.mark.asyncio
    async def test_get_dataset_async_success(self, mock_client: Mock) -> None:
        """Test get_dataset_async with successful response."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "async-dataset-456"

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {
                    "id": "async-dataset-456",
                    "project": "async-project",
                    "name": "async-retrieved-dataset",
                    "description": "Async retrieved dataset",
                }
            ]
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.get_dataset_async(dataset_id)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "async-project"
            assert result.name == "async-retrieved-dataset"
            assert result.description == "Async retrieved dataset"

            mock_client.request_async.assert_called_once_with(
                "GET", "/datasets", params={"dataset_id": dataset_id}
            )


class TestDatasetsAPIListDatasets:
    """Test dataset listing methods."""

    def test_list_datasets_no_filters(self, mock_client: Mock) -> None:
        """Test list_datasets without filters."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {"id": "dataset-1", "name": "Dataset 1", "project": "project-1"},
                {"id": "dataset-2", "name": "Dataset 2", "project": "project-2"},
            ]
        }

        mock_processed_data = [
            Dataset(name="Dataset 1", project="project-1"),
            Dataset(name="Dataset 2", project="project-2"),
        ]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ) as mock_process:
                # Act
                result = datasets_api.list_datasets()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 2
                assert all(isinstance(dataset, Dataset) for dataset in result)

                mock_client.request.assert_called_once_with(
                    "GET", "/datasets", params={"limit": "100"}
                )

                mock_process.assert_called_once_with(
                    [
                        {
                            "id": "dataset-1",
                            "name": "Dataset 1",
                            "project": "project-1",
                        },
                        {
                            "id": "dataset-2",
                            "name": "Dataset 2",
                            "project": "project-2",
                        },
                    ],
                    Dataset,
                    "testcases",
                )

    def test_list_datasets_with_project_filter(self, mock_client: Mock) -> None:
        """Test list_datasets with project filter."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        project = "filtered-project"

        mock_response = Mock()
        mock_response.json.return_value = {
            "datasets": [
                {"id": "dataset-1", "name": "Dataset 1", "project": "filtered-project"}
            ]
        }

        mock_processed_data = [Dataset(name="Dataset 1", project="filtered-project")]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ):
                # Act
                result = datasets_api.list_datasets(project=project)

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0].project == "filtered-project"

                mock_client.request.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={"limit": "100", "project": "filtered-project"},
                )

    def test_list_datasets_with_custom_limit(self, mock_client: Mock) -> None:
        """Test list_datasets with custom limit."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        limit = 50

        mock_response = Mock()
        mock_response.json.return_value = {"datasets": []}

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api, "_process_data_dynamically", return_value=[]
            ):
                # Act
                result = datasets_api.list_datasets(limit=limit)

                # Assert
                assert isinstance(result, list)
                assert len(result) == 0

                mock_client.request.assert_called_once_with(
                    "GET", "/datasets", params={"limit": "50"}
                )

    def test_list_datasets_with_project_and_limit(self, mock_client: Mock) -> None:
        """Test list_datasets with both project filter and custom limit."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        project = "test-project"
        limit = 25

        mock_response = Mock()
        mock_response.json.return_value = {"datasets": []}

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api, "_process_data_dynamically", return_value=[]
            ):
                # Act
                result = datasets_api.list_datasets(project=project, limit=limit)

                # Assert
                assert isinstance(result, list)

                mock_client.request.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={"limit": "25", "project": "test-project"},
                )

    @pytest.mark.asyncio
    async def test_list_datasets_async_no_filters(self, mock_client: Mock) -> None:
        """Test list_datasets_async without filters."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "datasets": [
                {
                    "id": "async-dataset-1",
                    "name": "Async Dataset 1",
                    "project": "async-project-1",
                }
            ]
        }

        mock_processed_data = [
            Dataset(name="Async Dataset 1", project="async-project-1")
        ]

        with patch.object(mock_client, "request_async", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ):
                # Act
                result = await datasets_api.list_datasets_async()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0].project == "async-project-1"

                mock_client.request_async.assert_called_once_with(
                    "GET", "/datasets", params={"limit": "100"}
                )

    @pytest.mark.asyncio
    async def test_list_datasets_async_with_filters(self, mock_client: Mock) -> None:
        """Test list_datasets_async with project filter and custom limit."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        project = "async-filtered-project"
        limit = 75

        mock_response = Mock()
        mock_response.json.return_value = {"datasets": []}

        with patch.object(mock_client, "request_async", return_value=mock_response):
            with patch.object(
                datasets_api, "_process_data_dynamically", return_value=[]
            ):
                # Act
                result = await datasets_api.list_datasets_async(
                    project=project, limit=limit
                )

                # Assert
                assert isinstance(result, list)

                mock_client.request_async.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={"limit": "75", "project": "async-filtered-project"},
                )

    def test_list_datasets_with_name(self, mock_client: Mock) -> None:
        """Test list_datasets with name filter."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        name = "Training Data Q4"

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {
                    "id": "dataset-123",
                    "name": "Training Data Q4",
                    "project": "project-1",
                }
            ]
        }

        mock_processed_data = [Dataset(name="Training Data Q4", project="project-1")]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ):
                # Act
                result = datasets_api.list_datasets(name=name)

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0].name == "Training Data Q4"

                mock_client.request.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={"limit": "100", "name": "Training Data Q4"},
                )

    def test_list_datasets_with_include_datapoints(self, mock_client: Mock) -> None:
        """Test list_datasets with include_datapoints parameter."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {
                    "id": "dataset-456",
                    "name": "Dataset With Datapoints",
                    "project": "project-1",
                    "datapoints": [{"id": "dp-1"}, {"id": "dp-2"}],
                }
            ]
        }

        mock_processed_data = [
            Dataset(name="Dataset With Datapoints", project="project-1")
        ]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ):
                # Act
                result = datasets_api.list_datasets(include_datapoints=True)

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1

                # Verify boolean is converted to lowercase string
                mock_client.request.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={"limit": "100", "include_datapoints": "true"},
                )

    def test_list_datasets_with_all_filters(self, mock_client: Mock) -> None:
        """Test list_datasets with all filter parameters combined."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        project = "test-project"
        dataset_type = "evaluation"
        dataset_id = "dataset-789"
        name = "Regression Tests"
        include_datapoints = True
        limit = 50

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {
                    "id": "dataset-789",
                    "name": "Regression Tests",
                    "project": "test-project",
                    "type": "evaluation",
                    "datapoints": [{"id": "dp-1"}],
                }
            ]
        }

        mock_processed_data = [Dataset(name="Regression Tests", project="test-project")]

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ):
                # Act
                result = datasets_api.list_datasets(
                    project=project,
                    dataset_type=dataset_type,
                    dataset_id=dataset_id,
                    name=name,
                    include_datapoints=include_datapoints,
                    limit=limit,
                )

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0].name == "Regression Tests"

                # Verify all parameters are passed correctly
                mock_client.request.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={
                        "limit": "50",
                        "project": "test-project",
                        "type": "evaluation",
                        "dataset_id": "dataset-789",
                        "name": "Regression Tests",
                        "include_datapoints": "true",
                    },
                )

    @pytest.mark.asyncio
    async def test_list_datasets_async_with_new_filters(
        self, mock_client: Mock
    ) -> None:
        """Test list_datasets_async with name and include_datapoints filters."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        name = "Async Dataset Name"
        include_datapoints = True

        mock_response = Mock()
        mock_response.json.return_value = {
            "testcases": [
                {
                    "id": "async-dataset-999",
                    "name": "Async Dataset Name",
                    "project": "async-project",
                    "datapoints": [{"id": "dp-1"}],
                }
            ]
        }

        mock_processed_data = [
            Dataset(name="Async Dataset Name", project="async-project")
        ]

        with patch.object(mock_client, "request_async", return_value=mock_response):
            with patch.object(
                datasets_api,
                "_process_data_dynamically",
                return_value=mock_processed_data,
            ):
                # Act
                result = await datasets_api.list_datasets_async(
                    name=name, include_datapoints=include_datapoints
                )

                # Assert
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0].name == "Async Dataset Name"

                # When include_datapoints is True, it should be sent as "true"
                mock_client.request_async.assert_called_once_with(
                    "GET",
                    "/datasets",
                    params={
                        "limit": "100",
                        "name": "Async Dataset Name",
                        "include_datapoints": "true",
                    },
                )


class TestDatasetsAPIUpdateDataset:
    """Test dataset update methods."""

    def test_update_dataset_success(self, mock_client: Mock) -> None:
        """Test update_dataset with successful response."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "dataset-update-123"
        request = DatasetUpdate(
            dataset_id=dataset_id,
            name="updated-dataset-name",
            description="Updated dataset description",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "dataset-update-123",
            "name": "updated-dataset-name",
            "description": "Updated dataset description",
            "project": "test-project",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.update_dataset(dataset_id, request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.name == "updated-dataset-name"
            assert result.description == "Updated dataset description"

            mock_client.request.assert_called_once_with(
                "PUT",
                f"/datasets/{dataset_id}",
                json={
                    "dataset_id": dataset_id,
                    "name": "updated-dataset-name",
                    "description": "Updated dataset description",
                },
            )

    def test_update_dataset_from_dict_success(self, mock_client: Mock) -> None:
        """Test update_dataset_from_dict with successful response."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "dataset-dict-update-456"
        dataset_data = {
            "name": "dict-updated-name",
            "description": "Dict updated description",
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "dataset-dict-update-456",
            "name": "dict-updated-name",
            "description": "Dict updated description",
            "project": "dict-project",
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.update_dataset_from_dict(dataset_id, dataset_data)

            # Assert
            assert isinstance(result, Dataset)
            assert result.name == "dict-updated-name"
            assert result.description == "Dict updated description"

            mock_client.request.assert_called_once_with(
                "PUT", f"/datasets/{dataset_id}", json=dataset_data
            )

    @pytest.mark.asyncio
    async def test_update_dataset_async_success(self, mock_client: Mock) -> None:
        """Test update_dataset_async with successful response."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "async-update-789"
        request = DatasetUpdate(
            dataset_id=dataset_id,
            name="async-updated-name",
            description="Async updated description",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "async-update-789",
            "name": "async-updated-name",
            "description": "Async updated description",
            "project": "async-project",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.update_dataset_async(dataset_id, request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.name == "async-updated-name"
            assert result.description == "Async updated description"

            mock_client.request_async.assert_called_once_with(
                "PUT",
                f"/datasets/{dataset_id}",
                json={
                    "dataset_id": dataset_id,
                    "name": "async-updated-name",
                    "description": "Async updated description",
                },
            )

    @pytest.mark.asyncio
    async def test_update_dataset_from_dict_async_success(
        self, mock_client: Mock
    ) -> None:
        """Test update_dataset_from_dict_async with successful response."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "async-dict-update-101"
        dataset_data = {
            "name": "async-dict-updated-name",
            "description": "Async dict updated description",
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "async-dict-update-101",
            "name": "async-dict-updated-name",
            "description": "Async dict updated description",
            "project": "async-dict-project",
        }

        with patch.object(mock_client, "request_async", return_value=mock_response):
            # Act
            result = await datasets_api.update_dataset_from_dict_async(
                dataset_id, dataset_data
            )

            # Assert
            assert isinstance(result, Dataset)
            assert result.name == "async-dict-updated-name"
            assert result.description == "Async dict updated description"

            mock_client.request_async.assert_called_once_with(
                "PUT", f"/datasets/{dataset_id}", json=dataset_data
            )


class TestDatasetsAPIDeleteDataset:
    """Test dataset deletion methods."""

    def test_delete_dataset_success(self, mock_client: Mock) -> None:
        """Test delete_dataset with successful deletion."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "dataset-delete-123"

        mock_response = Mock()
        mock_response.status_code = 200

        mock_error_context = Mock()
        mock_error_handler = Mock()
        mock_error_handler.handle_operation.return_value.__enter__ = Mock()
        mock_error_handler.handle_operation.return_value.__exit__ = Mock(
            return_value=None
        )

        with patch.object(
            datasets_api, "_create_error_context", return_value=mock_error_context
        ) as mock_create_context:
            with patch.object(datasets_api, "error_handler", mock_error_handler):
                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    result = datasets_api.delete_dataset(dataset_id)

                    # Assert
                    assert result is True

                    mock_create_context.assert_called_once_with(
                        operation="delete_dataset",
                        method="DELETE",
                        path="/datasets",
                        additional_context={"dataset_id": dataset_id},
                    )

                    mock_client.request.assert_called_once_with(
                        "DELETE", "/datasets", params={"dataset_id": dataset_id}
                    )

    def test_delete_dataset_failure(self, mock_client: Mock) -> None:
        """Test delete_dataset with failed deletion."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "dataset-delete-fail-456"

        mock_response = Mock()
        mock_response.status_code = 404

        mock_error_context = Mock()
        mock_error_handler = Mock()
        mock_error_handler.handle_operation.return_value.__enter__ = Mock()
        mock_error_handler.handle_operation.return_value.__exit__ = Mock(
            return_value=None
        )

        with patch.object(
            datasets_api, "_create_error_context", return_value=mock_error_context
        ):
            with patch.object(datasets_api, "error_handler", mock_error_handler):
                with patch.object(mock_client, "request", return_value=mock_response):
                    # Act
                    result = datasets_api.delete_dataset(dataset_id)

                    # Assert
                    assert result is False

                    mock_client.request.assert_called_once_with(
                        "DELETE", "/datasets", params={"dataset_id": dataset_id}
                    )

    @pytest.mark.asyncio
    async def test_delete_dataset_async_success(self, mock_client: Mock) -> None:
        """Test delete_dataset_async with successful deletion."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "async-delete-789"

        mock_response = Mock()
        mock_response.status_code = 200

        mock_error_context = Mock()
        mock_error_handler = Mock()
        mock_error_handler.handle_operation.return_value.__enter__ = Mock()
        mock_error_handler.handle_operation.return_value.__exit__ = Mock(
            return_value=None
        )

        with patch.object(
            datasets_api, "_create_error_context", return_value=mock_error_context
        ) as mock_create_context:
            with patch.object(datasets_api, "error_handler", mock_error_handler):
                with patch.object(
                    mock_client, "request_async", return_value=mock_response
                ):
                    # Act
                    result = await datasets_api.delete_dataset_async(dataset_id)

                    # Assert
                    assert result is True

                    mock_create_context.assert_called_once_with(
                        operation="delete_dataset_async",
                        method="DELETE",
                        path="/datasets",
                        additional_context={"dataset_id": dataset_id},
                    )

                    mock_client.request_async.assert_called_once_with(
                        "DELETE", "/datasets", params={"dataset_id": dataset_id}
                    )

    @pytest.mark.asyncio
    async def test_delete_dataset_async_failure(self, mock_client: Mock) -> None:
        """Test delete_dataset_async with failed deletion."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "async-delete-fail-101"

        mock_response = Mock()
        mock_response.status_code = 500

        mock_error_context = Mock()
        mock_error_handler = Mock()
        mock_error_handler.handle_operation.return_value.__enter__ = Mock()
        mock_error_handler.handle_operation.return_value.__exit__ = Mock(
            return_value=None
        )

        with patch.object(
            datasets_api, "_create_error_context", return_value=mock_error_context
        ):
            with patch.object(datasets_api, "error_handler", mock_error_handler):
                with patch.object(
                    mock_client, "request_async", return_value=mock_response
                ):
                    # Act
                    result = await datasets_api.delete_dataset_async(dataset_id)

                    # Assert
                    assert result is False

                    mock_client.request_async.assert_called_once_with(
                        "DELETE", "/datasets", params={"dataset_id": dataset_id}
                    )


class TestDatasetsAPIEdgeCases:
    """Test edge cases and error conditions."""

    def test_create_dataset_with_none_values(self, mock_client: Mock) -> None:
        """Test create_dataset with None values in request."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        request = CreateDatasetRequest(
            project="test-project", name="test-dataset", description=None
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "inserted": True,
            "result": {"insertedId": "dataset-none-values"},
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.create_dataset(request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.project == "test-project"
            assert result.name == "test-dataset"
            assert result.description is None

            # Verify exclude_none=True removes None values from JSON
            mock_client.request.assert_called_once_with(
                "POST",
                "/datasets",
                json={
                    "project": "test-project",
                    "name": "test-dataset",
                    # description excluded due to exclude_none=True
                },
            )

    def test_list_datasets_empty_response(self, mock_client: Mock) -> None:
        """Test list_datasets with empty datasets array."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)

        mock_response = Mock()
        mock_response.json.return_value = {"testcases": []}

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api, "_process_data_dynamically", return_value=[]
            ) as mock_process:
                # Act
                result = datasets_api.list_datasets()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 0

                mock_process.assert_called_once_with([], Dataset, "testcases")

    def test_list_datasets_missing_datasets_key(self, mock_client: Mock) -> None:
        """Test list_datasets when response missing testcases key."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)

        mock_response = Mock()
        mock_response.json.return_value = {"other_key": "other_value"}

        with patch.object(mock_client, "request", return_value=mock_response):
            with patch.object(
                datasets_api, "_process_data_dynamically", return_value=[]
            ) as mock_process:
                # Act
                result = datasets_api.list_datasets()

                # Assert
                assert isinstance(result, list)
                assert len(result) == 0

                # Should pass empty list when testcases key is missing
                mock_process.assert_called_once_with([], Dataset, "testcases")

    def test_update_dataset_with_partial_data(self, mock_client: Mock) -> None:
        """Test update_dataset with partial update data."""
        # Arrange
        datasets_api = DatasetsAPI(mock_client)
        dataset_id = "partial-update-dataset"
        request = DatasetUpdate(
            dataset_id=dataset_id, name="new-name-only"
        )  # Only updating name

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "partial-update-dataset",
            "name": "new-name-only",
            "description": "original-description",  # Unchanged
            "project": "original-project",  # Unchanged
        }

        with patch.object(mock_client, "request", return_value=mock_response):
            # Act
            result = datasets_api.update_dataset(dataset_id, request)

            # Assert
            assert isinstance(result, Dataset)
            assert result.name == "new-name-only"
            assert result.description == "original-description"
            assert result.project == "original-project"

            # Verify only non-None fields are sent
            mock_client.request.assert_called_once_with(
                "PUT",
                f"/datasets/{dataset_id}",
                json={
                    "dataset_id": dataset_id,
                    "name": "new-name-only",
                },  # dataset_id and name fields sent
            )
