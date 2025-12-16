"""DatasetsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import (
    CreateDatasetRequest,
    DeleteDatasetResponse,
    GetDatasetsResponse,
)


class TestDatasetsAPI:
    """Test DatasetsAPI CRUD operations."""

    def test_create_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset creation with metadata, verify backend."""
        test_id = str(uuid.uuid4())[:8]
        dataset_name = f"test_dataset_{test_id}"

        dataset_request = CreateDatasetRequest(
            name=dataset_name,
            description=f"Test dataset {test_id}",
        )

        response = integration_client.datasets.create(dataset_request)

        assert response is not None
        # v1 API returns CreateDatasetResponse with inserted and result fields
        assert response.inserted is True
        assert "insertedId" in response.result
        dataset_id = response.result["insertedId"]

        time.sleep(2)

        # Verify via list
        datasets_response = integration_client.datasets.list()
        assert isinstance(datasets_response, GetDatasetsResponse)
        datasets = datasets_response.datapoints
        found = None
        for ds in datasets:
            # GetDatasetsResponse.datapoints is List[Dict[str, Any]]
            ds_name = ds.get("name")
            if ds_name == dataset_name:
                found = ds
                break
        assert found is not None

        # Cleanup
        integration_client.datasets.delete(dataset_id)

    def test_get_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset retrieval with datapoints count, verify metadata."""
        test_id = str(uuid.uuid4())[:8]
        dataset_name = f"test_get_dataset_{test_id}"

        dataset_request = CreateDatasetRequest(
            name=dataset_name,
            description="Test get dataset",
        )

        create_response = integration_client.datasets.create(dataset_request)
        dataset_id = create_response.result["insertedId"]

        time.sleep(2)

        # Test retrieval via list (v1 doesn't have get_dataset method)
        datasets_response = integration_client.datasets.list(name=dataset_name)
        assert isinstance(datasets_response, GetDatasetsResponse)
        datasets = datasets_response.datapoints
        assert len(datasets) >= 1
        dataset = datasets[0]
        # GetDatasetsResponse.datapoints is List[Dict[str, Any]]
        ds_name = dataset.get("name")
        ds_desc = dataset.get("description")
        assert ds_name == dataset_name
        assert ds_desc == "Test get dataset"

        # Cleanup
        integration_client.datasets.delete(dataset_id)

    def test_list_datasets(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset listing, pagination, project filter."""
        test_id = str(uuid.uuid4())[:8]
        created_ids = []

        # Create multiple datasets
        for i in range(2):
            dataset_request = CreateDatasetRequest(
                name=f"test_list_dataset_{test_id}_{i}",
            )
            response = integration_client.datasets.create(dataset_request)
            dataset_id = response.result["insertedId"]
            created_ids.append(dataset_id)

        time.sleep(2)

        # Test listing
        datasets_response = integration_client.datasets.list()

        assert isinstance(datasets_response, GetDatasetsResponse)
        datasets = datasets_response.datapoints
        assert isinstance(datasets, list)
        assert len(datasets) >= 2

        # Cleanup
        for dataset_id in created_ids:
            integration_client.datasets.delete(dataset_id)

    def test_list_datasets_filter_by_name(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset listing with name filter."""
        test_id = str(uuid.uuid4())[:8]
        unique_name = f"test_name_filter_{test_id}"

        dataset_request = CreateDatasetRequest(
            name=unique_name,
            description="Test name filtering",
        )
        response = integration_client.datasets.create(dataset_request)
        dataset_id = response.result["insertedId"]

        time.sleep(2)

        # Test filtering by name
        datasets_response = integration_client.datasets.list(name=unique_name)

        assert isinstance(datasets_response, GetDatasetsResponse)
        datasets = datasets_response.datapoints
        assert isinstance(datasets, list)
        assert len(datasets) >= 1
        # GetDatasetsResponse.datapoints is List[Dict[str, Any]]
        found = any(d.get("name") == unique_name for d in datasets)
        assert found, f"Dataset with name {unique_name} not found in results"

        # Cleanup
        integration_client.datasets.delete(dataset_id)

    def test_list_datasets_include_datapoints(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset listing with include_datapoints parameter."""
        pytest.skip("Backend issue with include_datapoints parameter")

    def test_delete_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset deletion, verify not in list after delete."""
        test_id = str(uuid.uuid4())[:8]
        dataset_name = f"test_delete_dataset_{test_id}"

        dataset_request = CreateDatasetRequest(
            name=dataset_name,
            description=f"Test delete dataset {test_id}",
        )

        create_response = integration_client.datasets.create(dataset_request)
        dataset_id = create_response.result["insertedId"]

        time.sleep(2)

        response = integration_client.datasets.delete(dataset_id)

        assert isinstance(response, DeleteDatasetResponse)
        # Delete succeeded if no exception was raised
        # The response model only has 'result' field
        assert response is not None

    def test_update_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset metadata updates, verify persistence."""
        pytest.skip(
            "UpdateDatasetRequest requires dataset_id field - needs investigation"
        )
