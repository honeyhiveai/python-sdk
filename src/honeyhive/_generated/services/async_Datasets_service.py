from typing import *

import httpx

from ..api_config import (
    APIConfig,
    HTTPException,
    _raise_http_exception,
    _serialize_query_params,
)
from ..models import *


async def getDatasetsLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
) -> GetDatasetsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"dataset_id": dataset_id, "name": name}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getDatasetsLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetDatasetsResponse(**body) if body is not None else GetDatasetsResponse()


async def createDatasetLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: CreateDatasetRequest
) -> CreateDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createDatasetLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateDatasetResponse(**body) if body is not None else CreateDatasetResponse()
    )


async def updateDatasetBodyIdLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyUpdateDatasetRequest
) -> UpdateDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateDatasetBodyIdLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        UpdateDatasetResponse(**body) if body is not None else UpdateDatasetResponse()
    )


async def deleteDatasetQueryIdLegacy(
    api_config_override: Optional[APIConfig] = None, *, dataset_id: str
) -> DeleteDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"dataset_id": dataset_id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteDatasetQueryIdLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteDatasetResponse(**body) if body is not None else DeleteDatasetResponse()
    )


async def updateDatasetLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: str,
    data: UpdateDatasetRequest,
) -> UpdateDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets/{dataset_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateDatasetLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        UpdateDatasetResponse(**body) if body is not None else UpdateDatasetResponse()
    )


async def deleteDatasetLegacy(
    api_config_override: Optional[APIConfig] = None, *, dataset_id: str
) -> DeleteDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets/{dataset_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteDatasetLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteDatasetResponse(**body) if body is not None else DeleteDatasetResponse()
    )


async def addDatapointsLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: str,
    data: AddDatapointsToDatasetRequest,
) -> AddDatapointsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets/{dataset_id}/datapoints"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("addDatapointsLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        AddDatapointsResponse(**body) if body is not None else AddDatapointsResponse()
    )


async def removeDatapointLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: str,
    datapoint_id: str,
) -> RemoveDatapointResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets/{dataset_id}/datapoints/{datapoint_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("removeDatapointLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        RemoveDatapointResponse(**body)
        if body is not None
        else RemoveDatapointResponse()
    )


async def removeDatapointShortPathLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: str,
    datapoint_id: str,
) -> RemoveDatapointResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/datasets/{dataset_id}/{datapoint_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("removeDatapointShortPathLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        RemoveDatapointResponse(**body)
        if body is not None
        else RemoveDatapointResponse()
    )


async def getDatasets(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
) -> GetDatasetsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/datasets"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"dataset_id": dataset_id, "name": name}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getDatasets", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetDatasetsResponse(**body) if body is not None else GetDatasetsResponse()


async def createDataset(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    data: CreateDatasetRequest,
) -> CreateDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/datasets"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createDataset", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateDatasetResponse(**body) if body is not None else CreateDatasetResponse()
    )


async def deleteDataset(
    api_config_override: Optional[APIConfig] = None, *, project_id: str, dataset_id: str
) -> DeleteDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/datasets/{dataset_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteDataset", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteDatasetResponse(**body) if body is not None else DeleteDatasetResponse()
    )


async def updateDataset(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    dataset_id: str,
    data: UpdateDatasetRequest,
) -> UpdateDatasetResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/datasets/{dataset_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "patch",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateDataset", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        UpdateDatasetResponse(**body) if body is not None else UpdateDatasetResponse()
    )


async def addDatapoints(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    dataset_id: str,
    data: AddDatapointsToDatasetRequest,
) -> AddDatapointsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/datasets/{dataset_id}/datapoints"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("addDatapoints", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        AddDatapointsResponse(**body) if body is not None else AddDatapointsResponse()
    )


async def removeDatapoint(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    dataset_id: str,
    datapoint_id: str,
) -> RemoveDatapointResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/datasets/{dataset_id}/datapoints/{datapoint_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("removeDatapoint", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        RemoveDatapointResponse(**body)
        if body is not None
        else RemoveDatapointResponse()
    )
