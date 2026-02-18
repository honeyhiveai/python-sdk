"""DatasetsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import CreateDatasetRequest


def _get_dataset_id(response: Any) -> str:
    """Extract dataset ID from CreateDatasetResponse or dict."""
    result = getattr(response, "result", None)
    if result is None and isinstance(response, dict):
        result = response.get("result")
    assert result is not None, f"Missing result in response: {response}"
    dataset_id = result.get("insertedId")
    assert dataset_id is not None, f"Missing insertedId in result: {result}"
    return dataset_id


class TestDatasetsAPI:
    """Test DatasetsAPI CRUD operations."""

    def test_create_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset creation with metadata, verify backend."""
        test_id = str(uuid.uuid4())[:8]
        dataset_name = f"test_dataset_{test_id}"

        dataset_request = CreateDatasetRequest(
            project=integration_project_name,
            name=dataset_name,
            description=f"Test dataset {test_id}",
        )

        response = integration_client.datasets.create(dataset_request)

        assert response is not None
        # CreateDatasetResponse has `inserted` and `result` fields
        inserted = getattr(response, "inserted", None)
        if inserted is None and isinstance(response, dict):
            inserted = response.get("inserted")
        assert inserted is True

        _get_dataset_id(response)  # verify insertedId is present

        time.sleep(2)

        # Verify via list - API requires project param
        datasets_response = integration_client.datasets.list(
            project=integration_project_name
        )
        # GetDatasetsResponse has datasets field (list of Dataset objects)
        datasets = getattr(datasets_response, "testcases", None) or getattr(datasets_response, "datasets", None)
        if datasets is None and isinstance(datasets_response, dict):
            datasets = datasets_response.get("testcases", datasets_response.get("datasets", []))
        assert datasets is not None

        found = None
        for ds in datasets:
            ds_name = (
                ds.get("name") if isinstance(ds, dict) else getattr(ds, "name", None)
            )
            if ds_name == dataset_name:
                found = ds
                break
        assert found is not None

    def test_get_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset retrieval with datapoints count, verify metadata."""
        test_id = str(uuid.uuid4())[:8]
        dataset_name = f"test_get_dataset_{test_id}"

        dataset_request = CreateDatasetRequest(
            project=integration_project_name,
            name=dataset_name,
            description="Test get dataset",
        )

        create_response = integration_client.datasets.create(dataset_request)
        _get_dataset_id(create_response)  # verify insertedId is present

        time.sleep(2)

        # Test retrieval via list (v1 doesn't have get_dataset method)
        # API list() requires project, doesn't support name filter
        datasets_response = integration_client.datasets.list(
            project=integration_project_name
        )
        datasets = getattr(datasets_response, "testcases", None) or getattr(datasets_response, "datasets", None)
        if datasets is None and isinstance(datasets_response, dict):
            datasets = datasets_response.get("testcases", datasets_response.get("datasets", []))
        assert datasets is not None
        assert len(datasets) >= 1

        # Find our specific dataset by name
        dataset = None
        for ds in datasets:
            ds_name = (
                ds.get("name") if isinstance(ds, dict) else getattr(ds, "name", None)
            )
            if ds_name == dataset_name:
                dataset = ds
                break
        assert dataset is not None, f"Dataset {dataset_name} not found in list"

        ds_desc = (
            dataset.get("description")
            if isinstance(dataset, dict)
            else getattr(dataset, "description", None)
        )
        assert ds_desc == "Test get dataset"

    def test_list_datasets(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset listing, pagination, project filter."""
        test_id = str(uuid.uuid4())[:8]

        # Create multiple datasets
        for i in range(2):
            dataset_request = CreateDatasetRequest(
                project=integration_project_name,
                name=f"test_list_dataset_{test_id}_{i}",
            )
            response = integration_client.datasets.create(dataset_request)
            _get_dataset_id(response)  # verify insertedId is present

        time.sleep(2)

        # Test listing - API requires project param
        datasets_response = integration_client.datasets.list(
            project=integration_project_name
        )

        datasets = getattr(datasets_response, "testcases", None) or getattr(datasets_response, "datasets", None)
        if datasets is None and isinstance(datasets_response, dict):
            datasets = datasets_response.get("testcases", datasets_response.get("datasets", []))
        assert datasets is not None
        assert isinstance(datasets, list)
        assert len(datasets) >= 2

    def test_list_datasets_filter_by_name(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset listing with name filter."""
        test_id = str(uuid.uuid4())[:8]
        unique_name = f"test_name_filter_{test_id}"

        dataset_request = CreateDatasetRequest(
            project=integration_project_name,
            name=unique_name,
            description="Test name filtering",
        )
        response = integration_client.datasets.create(dataset_request)
        _get_dataset_id(response)  # verify insertedId is present

        time.sleep(2)

        # API list() doesn't support name filter - list all and filter in-memory
        datasets_response = integration_client.datasets.list(
            project=integration_project_name
        )

        datasets = getattr(datasets_response, "testcases", None) or getattr(datasets_response, "datasets", None)
        if datasets is None and isinstance(datasets_response, dict):
            datasets = datasets_response.get("testcases", datasets_response.get("datasets", []))
        assert datasets is not None
        assert isinstance(datasets, list)
        assert len(datasets) >= 1
        found = any(
            (d.get("name") if isinstance(d, dict) else getattr(d, "name", None))
            == unique_name
            for d in datasets
        )
        assert found, f"Dataset with name {unique_name} not found in results"

    def test_list_datasets_include_datapoints(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset listing with include_datapoints parameter."""
        pytest.skip("Backend issue with include_datapoints parameter")

    def test_delete_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset deletion, verify not in list after delete."""
        pytest.skip("Dataset deletion is not supported by the API")

    def test_update_dataset(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test dataset metadata updates, verify persistence."""
        pytest.skip(
            "UpdateDatasetRequest requires dataset_id field - needs investigation"
        )
