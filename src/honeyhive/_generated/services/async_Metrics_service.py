from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def getMetrics(
    api_config_override: Optional[APIConfig] = None,
    *,
    type: Optional[str] = None,
    id: Optional[str] = None,
) -> List[GetMetricsResponse]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"type": type, "id": id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getMetrics failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return [GetMetricsResponse(**item) for item in body]


async def createMetric(
    api_config_override: Optional[APIConfig] = None, *, data: CreateMetricRequest
) -> CreateMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createMetric failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return CreateMetricResponse(**body) if body is not None else CreateMetricResponse()


async def updateMetric(
    api_config_override: Optional[APIConfig] = None, *, data: UpdateMetricRequest
) -> UpdateMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=query_params,
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateMetric failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return UpdateMetricResponse(**body) if body is not None else UpdateMetricResponse()


async def deleteMetric(
    api_config_override: Optional[APIConfig] = None, *, metric_id: str
) -> DeleteMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"metric_id": metric_id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteMetric failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return DeleteMetricResponse(**body) if body is not None else DeleteMetricResponse()


async def runMetric(
    api_config_override: Optional[APIConfig] = None, *, data: RunMetricRequest
) -> RunMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/run_metric"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"runMetric failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return RunMetricResponse(**body) if body is not None else RunMetricResponse()
