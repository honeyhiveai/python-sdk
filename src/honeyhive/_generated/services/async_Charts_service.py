from typing import *

import httpx

from ..api_config import APIConfig, HTTPException, _serialize_query_params
from ..models import *


async def getCharts(
    api_config_override: Optional[APIConfig] = None,
) -> GetChartsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/charts"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

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
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getCharts failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetChartsResponse(**body) if body is not None else GetChartsResponse()


async def createChart(
    api_config_override: Optional[APIConfig] = None, *, data: CreateChartRequest
) -> CreateChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/charts"
    headers = api_config.get_default_headers()
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
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createChart failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return CreateChartResponse(**body) if body is not None else CreateChartResponse()


async def getChart(
    api_config_override: Optional[APIConfig] = None, *, chart_id: str
) -> GetChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/charts/{chart_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

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
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getChart failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetChartResponse(**body) if body is not None else GetChartResponse()


async def updateChart(
    api_config_override: Optional[APIConfig] = None,
    *,
    chart_id: str,
    data: UpdateChartRequest,
) -> UpdateChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/charts/{chart_id}"
    headers = api_config.get_default_headers()
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
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateChart failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return UpdateChartResponse(**body) if body is not None else UpdateChartResponse()


async def deleteChart(
    api_config_override: Optional[APIConfig] = None, *, chart_id: str
) -> DeleteChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/charts/{chart_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

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
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteChart failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return DeleteChartResponse(**body) if body is not None else DeleteChartResponse()
