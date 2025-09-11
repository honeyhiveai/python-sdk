"""Datasets API module for HoneyHive."""

from typing import List, Optional

from ..models import CreateDatasetRequest, Dataset, DatasetUpdate
from .base import BaseAPI


class DatasetsAPI(BaseAPI):
    """API for dataset operations."""

    def create_dataset(self, request: CreateDatasetRequest) -> Dataset:
        """Create a new dataset using CreateDatasetRequest model."""
        response = self.client.request(
            "POST",
            "/datasets",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            _inserted_id = data["result"][
                "insertedId"
            ]  # Not used yet, but available for future use
            # Create a Dataset object with the inserted ID and original request data
            return Dataset(
                project=request.project,
                name=request.name,
                description=request.description,
            )
        else:
            # Legacy format: direct dataset object
            return Dataset(**data)

    def create_dataset_from_dict(self, dataset_data: dict) -> Dataset:
        """Create a new dataset from dictionary (legacy method)."""
        response = self.client.request("POST", "/datasets", json=dataset_data)

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            _inserted_id = data["result"][
                "insertedId"
            ]  # Not used yet, but available for future use
            # Create a Dataset object with the inserted ID and original request data
            return Dataset(
                project=dataset_data.get("project"),
                name=dataset_data.get("name"),
                description=dataset_data.get("description"),
            )
        else:
            # Legacy format: direct dataset object
            return Dataset(**data)

    async def create_dataset_async(self, request: CreateDatasetRequest) -> Dataset:
        """Create a new dataset asynchronously using CreateDatasetRequest model."""
        response = await self.client.request_async(
            "POST",
            "/datasets",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            _inserted_id = data["result"][
                "insertedId"
            ]  # Not used yet, but available for future use
            # Create a Dataset object with the inserted ID and original request data
            return Dataset(
                project=request.project,
                name=request.name,
                description=request.description,
            )
        else:
            # Legacy format: direct dataset object
            return Dataset(**data)

    async def create_dataset_from_dict_async(self, dataset_data: dict) -> Dataset:
        """Create a new dataset asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/datasets", json=dataset_data
        )

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            _inserted_id = data["result"][
                "insertedId"
            ]  # Not used yet, but available for future use
            # Create a Dataset object with the inserted ID and original request data
            return Dataset(
                project=dataset_data.get("project"),
                name=dataset_data.get("name"),
                description=dataset_data.get("description"),
            )
        else:
            # Legacy format: direct dataset object
            return Dataset(**data)

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Get a dataset by ID."""
        response = self.client.request("GET", f"/datasets/{dataset_id}")
        data = response.json()
        return Dataset(**data)

    async def get_dataset_async(self, dataset_id: str) -> Dataset:
        """Get a dataset by ID asynchronously."""
        response = await self.client.request_async("GET", f"/datasets/{dataset_id}")
        data = response.json()
        return Dataset(**data)

    def list_datasets(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Dataset]:
        """List datasets with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = self.client.request("GET", "/datasets", params=params)
        data = response.json()
        return [Dataset(**dataset_data) for dataset_data in data.get("datasets", [])]

    async def list_datasets_async(
        self, project: Optional[str] = None, limit: int = 100
    ) -> List[Dataset]:
        """List datasets asynchronously with optional filtering."""
        params = {"limit": str(limit)}
        if project:
            params["project"] = project

        response = await self.client.request_async("GET", "/datasets", params=params)
        data = response.json()
        return [Dataset(**dataset_data) for dataset_data in data.get("datasets", [])]

    def update_dataset(self, dataset_id: str, request: DatasetUpdate) -> Dataset:
        """Update a dataset using DatasetUpdate model."""
        response = self.client.request(
            "PUT",
            f"/datasets/{dataset_id}",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return Dataset(**data)

    def update_dataset_from_dict(self, dataset_id: str, dataset_data: dict) -> Dataset:
        """Update a dataset from dictionary (legacy method)."""
        response = self.client.request(
            "PUT", f"/datasets/{dataset_id}", json=dataset_data
        )

        data = response.json()
        return Dataset(**data)

    async def update_dataset_async(
        self, dataset_id: str, request: DatasetUpdate
    ) -> Dataset:
        """Update a dataset asynchronously using DatasetUpdate model."""
        response = await self.client.request_async(
            "PUT",
            f"/datasets/{dataset_id}",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return Dataset(**data)

    async def update_dataset_from_dict_async(
        self, dataset_id: str, dataset_data: dict
    ) -> Dataset:
        """Update a dataset asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/datasets/{dataset_id}", json=dataset_data
        )

        data = response.json()
        return Dataset(**data)

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset by ID."""
        context = self._create_error_context(
            operation="delete_dataset",
            method="DELETE",
            path=f"/datasets/{dataset_id}",
            additional_context={"dataset_id": dataset_id},
        )

        with self.error_handler.handle_operation(context):
            response = self.client.request("DELETE", f"/datasets/{dataset_id}")
            return response.status_code == 200

    async def delete_dataset_async(self, dataset_id: str) -> bool:
        """Delete a dataset by ID asynchronously."""
        context = self._create_error_context(
            operation="delete_dataset_async",
            method="DELETE",
            path=f"/datasets/{dataset_id}",
            additional_context={"dataset_id": dataset_id},
        )

        with self.error_handler.handle_operation(context):
            response = await self.client.request_async(
                "DELETE", f"/datasets/{dataset_id}"
            )
            return response.status_code == 200
