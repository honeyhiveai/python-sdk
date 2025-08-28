"""Datasets API module for HoneyHive."""

from typing import List, Optional

from ..models import Dataset, CreateDatasetRequest, DatasetUpdate
from .base import BaseAPI


class DatasetsAPI(BaseAPI):
    """API for dataset operations."""

    def create_dataset(self, request: CreateDatasetRequest) -> Dataset:
        """Create a new dataset."""
        response = self.client.request(
            "POST", 
            "/datasets", 
            json={"dataset": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
        return Dataset(**data)

    async def create_dataset_async(self, request: CreateDatasetRequest) -> Dataset:
        """Create a new dataset asynchronously."""
        response = await self.client.request_async(
            "POST", 
            "/datasets", 
            json={"dataset": request.model_dump(exclude_none=True)}
        )
        
        data = response.json()
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
        self, 
        project: Optional[str] = None, 
        limit: int = 100
    ) -> List[Dataset]:
        """List datasets with optional filtering."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        
        response = self.client.request("GET", "/datasets", params=params)
        data = response.json()
        return [Dataset(**dataset_data) for dataset_data in data.get("datasets", [])]

    async def list_datasets_async(
        self, 
        project: Optional[str] = None, 
        limit: int = 100
    ) -> List[Dataset]:
        """List datasets with optional filtering asynchronously."""
        params = {"limit": limit}
        if project:
            params["project"] = project
        
        response = await self.client.request_async("GET", "/datasets", params=params)
        data = response.json()
        return [Dataset(**dataset_data) for dataset_data in data.get("datasets", [])]

    def update_dataset(self, dataset_id: str, request: DatasetUpdate) -> Dataset:
        """Update a dataset."""
        response = self.client.request(
            "PUT", 
            f"/datasets/{dataset_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Dataset(**data)

    async def update_dataset_async(self, dataset_id: str, request: DatasetUpdate) -> Dataset:
        """Update a dataset asynchronously."""
        response = await self.client.request_async(
            "PUT", 
            f"/datasets/{dataset_id}", 
            json=request.model_dump(exclude_none=True)
        )
        
        data = response.json()
        return Dataset(**data)

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        response = self.client.request("DELETE", f"/datasets/{dataset_id}")
        return response.status_code == 200

    async def delete_dataset_async(self, dataset_id: str) -> bool:
        """Delete a dataset asynchronously."""
        response = await self.client.request_async("DELETE", f"/datasets/{dataset_id}")
        return response.status_code == 200
