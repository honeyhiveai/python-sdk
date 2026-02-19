from typing import *

from ..api_config import APIConfig, HTTPException, _make_request_async
from ..models import *


async def getDatasets(
    api_config_override: Optional[APIConfig] = None,
    *,
    project: str,
    type: Optional[str] = None,
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
) -> GetDatasetsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datasets"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "project": project,
        "type": type,
        "dataset_id": dataset_id,
        "name": name,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = await _make_request_async(
        api_config, "get", path, headers, params=query_params
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getDatasets failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetDatasetsResponse(**body) if body is not None else GetDatasetsResponse()


async def createDataset(
    api_config_override: Optional[APIConfig] = None, *, data: CreateDatasetRequest
) -> CreateDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datasets"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = await _make_request_async(
        api_config,
        "post",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createDataset failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateDatasetResponse(**body) if body is not None else CreateDatasetResponse()
    )


async def updateDataset(
    api_config_override: Optional[APIConfig] = None, *, data: DatasetUpdate
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datasets"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = await _make_request_async(
        api_config,
        "put",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateDataset failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


async def deleteDataset(
    api_config_override: Optional[APIConfig] = None, *, dataset_id: str
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datasets"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"dataset_id": dataset_id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = await _make_request_async(
        api_config, "delete", path, headers, params=query_params
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteDataset failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


async def addDatapoints(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: str,
    data: AddDatapointsRequest,
) -> AddDatapointsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datasets/{dataset_id}/datapoints"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = await _make_request_async(
        api_config,
        "post",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"addDatapoints failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        AddDatapointsResponse(**body) if body is not None else AddDatapointsResponse()
    )
