from typing import *

import httpx

from ..api_config import APIConfig, HTTPException, _serialize_query_params
from ..models import *


async def getMetricVersions(
    api_config_override: Optional[APIConfig] = None, *, metric_id: str
) -> GetMetricVersionsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/{metric_id}/versions"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

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
        raise HTTPException(
            response.status_code,
            f"getMetricVersions failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetMetricVersionsResponse(**body)
        if body is not None
        else GetMetricVersionsResponse()
    )


async def createMetricVersion(
    api_config_override: Optional[APIConfig] = None,
    *,
    metric_id: str,
    data: CreateMetricVersionRequest,
) -> CreateMetricVersionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/{metric_id}/versions"
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
        raise HTTPException(
            response.status_code,
            f"createMetricVersion failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateMetricVersionResponse(**body)
        if body is not None
        else CreateMetricVersionResponse()
    )


async def deployMetricVersion(
    api_config_override: Optional[APIConfig] = None,
    *,
    metric_id: str,
    version_name: str,
) -> DeployMetricVersionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/{metric_id}/versions/{version_name}/deploy"
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
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deployMetricVersion failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeployMetricVersionResponse(**body)
        if body is not None
        else DeployMetricVersionResponse()
    )
