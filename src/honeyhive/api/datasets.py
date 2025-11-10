"""Datasets API module for HoneyHive."""

from typing import List, Literal, Optional

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
            inserted_id = data["result"]["insertedId"]
            # Create a Dataset object with the inserted ID
            dataset = Dataset(
                project=request.project,
                name=request.name,
                description=request.description,
                metadata=request.metadata,
            )
            # Attach ID as a dynamic attribute for retrieval
            setattr(dataset, "_id", inserted_id)
            return dataset
        # Legacy format: direct dataset object
        return Dataset(**data)

    def create_dataset_from_dict(self, dataset_data: dict) -> Dataset:
        """Create a new dataset from dictionary (legacy method)."""
        response = self.client.request("POST", "/datasets", json=dataset_data)

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            inserted_id = data["result"]["insertedId"]
            # Create a Dataset object with the inserted ID
            dataset = Dataset(
                project=dataset_data.get("project"),
                name=dataset_data.get("name"),
                description=dataset_data.get("description"),
                metadata=dataset_data.get("metadata"),
            )
            # Attach ID as a dynamic attribute for retrieval
            setattr(dataset, "_id", inserted_id)
            return dataset
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
            inserted_id = data["result"]["insertedId"]
            # Create a Dataset object with the inserted ID
            dataset = Dataset(
                project=request.project,
                name=request.name,
                description=request.description,
                metadata=request.metadata,
            )
            # Attach ID as a dynamic attribute for retrieval
            setattr(dataset, "_id", inserted_id)
            return dataset
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
            inserted_id = data["result"]["insertedId"]
            # Create a Dataset object with the inserted ID
            dataset = Dataset(
                project=dataset_data.get("project"),
                name=dataset_data.get("name"),
                description=dataset_data.get("description"),
                metadata=dataset_data.get("metadata"),
            )
            # Attach ID as a dynamic attribute for retrieval
            setattr(dataset, "_id", inserted_id)
            return dataset
        # Legacy format: direct dataset object
        return Dataset(**data)

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Get a dataset by ID."""
        response = self.client.request(
            "GET", "/datasets", params={"dataset_id": dataset_id}
        )
        data = response.json()
        # Backend returns {"testcases": [dataset]}
        datasets = data.get("testcases", [])
        if not datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        return Dataset(**datasets[0])

    async def get_dataset_async(self, dataset_id: str) -> Dataset:
        """Get a dataset by ID asynchronously."""
        response = await self.client.request_async(
            "GET", "/datasets", params={"dataset_id": dataset_id}
        )
        data = response.json()
        # Backend returns {"testcases": [dataset]}
        datasets = data.get("testcases", [])
        if not datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        return Dataset(**datasets[0])

    def list_datasets(
        self,
        project: Optional[str] = None,
        *,
        dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
        include_datapoints: bool = False,
        limit: int = 100,
    ) -> List[Dataset]:
        """List datasets with optional filtering.

        Args:
            project: Project name to filter by
            dataset_type: Type of dataset - "evaluation" or "fine-tuning"
            dataset_id: Specific dataset ID to filter by
            name: Dataset name to filter by (exact match)
            include_datapoints: Include datapoints in response (may impact performance)
            limit: Maximum number of datasets to return (default: 100)

        Returns:
            List of Dataset objects matching the filters

        Examples:
            Find dataset by name::

                datasets = client.datasets.list_datasets(
                    project="My Project",
                    name="Training Data Q4"
                )

            Get specific dataset with datapoints::

                dataset = client.datasets.list_datasets(
                    dataset_id="663876ec4611c47f4970f0c3",
                    include_datapoints=True
                )[0]

            Filter by type and name::

                eval_datasets = client.datasets.list_datasets(
                    dataset_type="evaluation",
                    name="Regression Tests"
                )
        """
        params = {"limit": str(limit)}
        if project:
            params["project"] = project
        if dataset_type:
            params["type"] = dataset_type
        if dataset_id:
            params["dataset_id"] = dataset_id
        if name:
            params["name"] = name
        if include_datapoints:
            params["include_datapoints"] = str(include_datapoints).lower()

        response = self.client.request("GET", "/datasets", params=params)
        data = response.json()
        return self._process_data_dynamically(
            data.get("testcases", []), Dataset, "testcases"
        )

    async def list_datasets_async(
        self,
        project: Optional[str] = None,
        *,
        dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
        include_datapoints: bool = False,
        limit: int = 100,
    ) -> List[Dataset]:
        """List datasets asynchronously with optional filtering.

        Args:
            project: Project name to filter by
            dataset_type: Type of dataset - "evaluation" or "fine-tuning"
            dataset_id: Specific dataset ID to filter by
            name: Dataset name to filter by (exact match)
            include_datapoints: Include datapoints in response (may impact performance)
            limit: Maximum number of datasets to return (default: 100)

        Returns:
            List of Dataset objects matching the filters

        Examples:
            Find dataset by name::

                datasets = await client.datasets.list_datasets_async(
                    project="My Project",
                    name="Training Data Q4"
                )

            Get specific dataset with datapoints::

                dataset = await client.datasets.list_datasets_async(
                    dataset_id="663876ec4611c47f4970f0c3",
                    include_datapoints=True
                )

            Filter by type and name::

                eval_datasets = await client.datasets.list_datasets_async(
                    dataset_type="evaluation",
                    name="Regression Tests"
                )
        """
        params = {"limit": str(limit)}
        if project:
            params["project"] = project
        if dataset_type:
            params["type"] = dataset_type
        if dataset_id:
            params["dataset_id"] = dataset_id
        if name:
            params["name"] = name
        if include_datapoints:
            params["include_datapoints"] = str(include_datapoints).lower()

        response = await self.client.request_async("GET", "/datasets", params=params)
        data = response.json()
        return self._process_data_dynamically(
            data.get("testcases", []), Dataset, "testcases"
        )

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
            path="/datasets",
            additional_context={"dataset_id": dataset_id},
        )

        with self.error_handler.handle_operation(context):
            response = self.client.request(
                "DELETE", "/datasets", params={"dataset_id": dataset_id}
            )
            return response.status_code == 200

    async def delete_dataset_async(self, dataset_id: str) -> bool:
        """Delete a dataset by ID asynchronously."""
        context = self._create_error_context(
            operation="delete_dataset_async",
            method="DELETE",
            path="/datasets",
            additional_context={"dataset_id": dataset_id},
        )

        with self.error_handler.handle_operation(context):
            response = await self.client.request_async(
                "DELETE", "/datasets", params={"dataset_id": dataset_id}
            )
            return response.status_code == 200
