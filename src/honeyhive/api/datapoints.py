"""Datapoints API module for HoneyHive."""

from typing import List, Optional

from ..models import CreateDatapointRequest, Datapoint, UpdateDatapointRequest
from .base import BaseAPI


class DatapointsAPI(BaseAPI):
    """API for datapoint operations."""

    def create_datapoint(self, request: CreateDatapointRequest) -> Datapoint:
        """Create a new datapoint using CreateDatapointRequest model."""
        response = self.client.request(
            "POST",
            "/datapoints",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            inserted_id = data["result"]["insertedId"]
            # Create a Datapoint object with the inserted ID and original request data
            return Datapoint(
                _id=inserted_id,
                inputs=request.inputs,
                ground_truth=request.ground_truth,
                metadata=request.metadata,
                linked_event=request.linked_event,
                linked_datasets=request.linked_datasets,
                history=request.history,
            )
        # Legacy format: direct datapoint object
        return Datapoint(**data)

    def create_datapoint_from_dict(self, datapoint_data: dict) -> Datapoint:
        """Create a new datapoint from dictionary (legacy method)."""
        response = self.client.request("POST", "/datapoints", json=datapoint_data)

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            inserted_id = data["result"]["insertedId"]
            # Create a Datapoint object with the inserted ID and original request data
            return Datapoint(
                _id=inserted_id,
                inputs=datapoint_data.get("inputs"),
                ground_truth=datapoint_data.get("ground_truth"),
                metadata=datapoint_data.get("metadata"),
                linked_event=datapoint_data.get("linked_event"),
                linked_datasets=datapoint_data.get("linked_datasets"),
                history=datapoint_data.get("history"),
            )
        # Legacy format: direct datapoint object
        return Datapoint(**data)

    async def create_datapoint_async(
        self, request: CreateDatapointRequest
    ) -> Datapoint:
        """Create a new datapoint asynchronously using CreateDatapointRequest model."""
        response = await self.client.request_async(
            "POST",
            "/datapoints",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            inserted_id = data["result"]["insertedId"]
            # Create a Datapoint object with the inserted ID and original request data
            return Datapoint(
                _id=inserted_id,
                inputs=request.inputs,
                ground_truth=request.ground_truth,
                metadata=request.metadata,
                linked_event=request.linked_event,
                linked_datasets=request.linked_datasets,
                history=request.history,
            )
        # Legacy format: direct datapoint object
        return Datapoint(**data)

    async def create_datapoint_from_dict_async(self, datapoint_data: dict) -> Datapoint:
        """Create a new datapoint asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "POST", "/datapoints", json=datapoint_data
        )

        data = response.json()

        # Handle new API response format that returns insertion result
        if "result" in data and "insertedId" in data["result"]:
            # New format: {"inserted": true, "result": {"insertedId": "...", ...}}
            inserted_id = data["result"]["insertedId"]
            # Create a Datapoint object with the inserted ID and original request data
            return Datapoint(
                _id=inserted_id,
                inputs=datapoint_data.get("inputs"),
                ground_truth=datapoint_data.get("ground_truth"),
                metadata=datapoint_data.get("metadata"),
                linked_event=datapoint_data.get("linked_event"),
                linked_datasets=datapoint_data.get("linked_datasets"),
                history=datapoint_data.get("history"),
            )
        # Legacy format: direct datapoint object
        return Datapoint(**data)

    def get_datapoint(self, datapoint_id: str) -> Datapoint:
        """Get a datapoint by ID."""
        response = self.client.request("GET", f"/datapoints/{datapoint_id}")
        data = response.json()

        # API returns {"datapoint": [datapoint_object]}
        if (
            "datapoint" in data
            and isinstance(data["datapoint"], list)
            and data["datapoint"]
        ):
            datapoint_data = data["datapoint"][0]
            # Map 'id' to '_id' for the Datapoint model
            if "id" in datapoint_data and "_id" not in datapoint_data:
                datapoint_data["_id"] = datapoint_data["id"]
            return Datapoint(**datapoint_data)
        # Fallback for unexpected format
        return Datapoint(**data)

    async def get_datapoint_async(self, datapoint_id: str) -> Datapoint:
        """Get a datapoint by ID asynchronously."""
        response = await self.client.request_async("GET", f"/datapoints/{datapoint_id}")
        data = response.json()

        # API returns {"datapoint": [datapoint_object]}
        if (
            "datapoint" in data
            and isinstance(data["datapoint"], list)
            and data["datapoint"]
        ):
            datapoint_data = data["datapoint"][0]
            # Map 'id' to '_id' for the Datapoint model
            if "id" in datapoint_data and "_id" not in datapoint_data:
                datapoint_data["_id"] = datapoint_data["id"]
            return Datapoint(**datapoint_data)
        # Fallback for unexpected format
        return Datapoint(**data)

    def list_datapoints(
        self,
        project: Optional[str] = None,
        dataset: Optional[str] = None,
        dataset_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
    ) -> List[Datapoint]:
        """List datapoints with optional filtering.

        Args:
            project: Project name to filter by
            dataset: (Legacy) Dataset ID or name to filter by - use dataset_id or
                dataset_name instead
            dataset_id: Dataset ID to filter by (takes precedence over dataset_name)
            dataset_name: Dataset name to filter by

        Returns:
            List of Datapoint objects matching the filters
        """
        params = {}
        if project:
            params["project"] = project

        # Prioritize explicit parameters over legacy 'dataset'
        if dataset_id:
            params["dataset_id"] = dataset_id
        elif dataset_name:
            params["dataset_name"] = dataset_name
        elif dataset:
            # Legacy: try to determine if it's an ID or name
            # NanoIDs are 24 chars, so use that as heuristic
            if (
                len(dataset) == 24
                and dataset.replace("_", "").replace("-", "").isalnum()
            ):
                params["dataset_id"] = dataset
            else:
                params["dataset_name"] = dataset

        response = self.client.request("GET", "/datapoints", params=params)
        data = response.json()
        return self._process_data_dynamically(
            data.get("datapoints", []), Datapoint, "datapoints"
        )

    async def list_datapoints_async(
        self,
        project: Optional[str] = None,
        dataset: Optional[str] = None,
        dataset_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
    ) -> List[Datapoint]:
        """List datapoints asynchronously with optional filtering.

        Args:
            project: Project name to filter by
            dataset: (Legacy) Dataset ID or name to filter by - use dataset_id or
                dataset_name instead
            dataset_id: Dataset ID to filter by (takes precedence over dataset_name)
            dataset_name: Dataset name to filter by

        Returns:
            List of Datapoint objects matching the filters
        """
        params = {}
        if project:
            params["project"] = project

        # Prioritize explicit parameters over legacy 'dataset'
        if dataset_id:
            params["dataset_id"] = dataset_id
        elif dataset_name:
            params["dataset_name"] = dataset_name
        elif dataset:
            # Legacy: try to determine if it's an ID or name
            # NanoIDs are 24 chars, so use that as heuristic
            if (
                len(dataset) == 24
                and dataset.replace("_", "").replace("-", "").isalnum()
            ):
                params["dataset_id"] = dataset
            else:
                params["dataset_name"] = dataset

        response = await self.client.request_async("GET", "/datapoints", params=params)
        data = response.json()
        return self._process_data_dynamically(
            data.get("datapoints", []), Datapoint, "datapoints"
        )

    def update_datapoint(
        self, datapoint_id: str, request: UpdateDatapointRequest
    ) -> Datapoint:
        """Update a datapoint using UpdateDatapointRequest model."""
        response = self.client.request(
            "PUT",
            f"/datapoints/{datapoint_id}",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return Datapoint(**data)

    def update_datapoint_from_dict(
        self, datapoint_id: str, datapoint_data: dict
    ) -> Datapoint:
        """Update a datapoint from dictionary (legacy method)."""
        response = self.client.request(
            "PUT", f"/datapoints/{datapoint_id}", json=datapoint_data
        )

        data = response.json()
        return Datapoint(**data)

    async def update_datapoint_async(
        self, datapoint_id: str, request: UpdateDatapointRequest
    ) -> Datapoint:
        """Update a datapoint asynchronously using UpdateDatapointRequest model."""
        response = await self.client.request_async(
            "PUT",
            f"/datapoints/{datapoint_id}",
            json=request.model_dump(mode="json", exclude_none=True),
        )

        data = response.json()
        return Datapoint(**data)

    async def update_datapoint_from_dict_async(
        self, datapoint_id: str, datapoint_data: dict
    ) -> Datapoint:
        """Update a datapoint asynchronously from dictionary (legacy method)."""
        response = await self.client.request_async(
            "PUT", f"/datapoints/{datapoint_id}", json=datapoint_data
        )

        data = response.json()
        return Datapoint(**data)
