from typing import *

import httpx

from ..api_config import (
    APIConfig,
    HTTPException,
    _raise_http_exception,
    _serialize_query_params,
)
from ..models import *


def getChartsLegacy(
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

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getChartsLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetChartsResponse(**body) if body is not None else GetChartsResponse()


def createChartLegacy(
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

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createChartLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return CreateChartResponse(**body) if body is not None else CreateChartResponse()


def getChartLegacy(
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

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getChartLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetChartResponse(**body) if body is not None else GetChartResponse()


def updateChartLegacy(
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

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateChartLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return UpdateChartResponse(**body) if body is not None else UpdateChartResponse()


def deleteChartLegacy(
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

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteChartLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return DeleteChartResponse(**body) if body is not None else DeleteChartResponse()


def getCharts(
    api_config_override: Optional[APIConfig] = None, *, project_id: str
) -> GetChartsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/charts"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getCharts", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetChartsResponse(**body) if body is not None else GetChartsResponse()


def createChart(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    data: CreateChartRequest,
) -> CreateChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/charts"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createChart", response)
    else:
        body = None if 200 == 204 else response.json()

    return CreateChartResponse(**body) if body is not None else CreateChartResponse()


def getChart(
    api_config_override: Optional[APIConfig] = None, *, project_id: str, chart_id: str
) -> GetChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/charts/{chart_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getChart", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetChartResponse(**body) if body is not None else GetChartResponse()


def deleteChart(
    api_config_override: Optional[APIConfig] = None, *, project_id: str, chart_id: str
) -> DeleteChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/charts/{chart_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteChart", response)
    else:
        body = None if 200 == 204 else response.json()

    return DeleteChartResponse(**body) if body is not None else DeleteChartResponse()


def updateChart(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    chart_id: str,
    data: UpdateChartRequest,
) -> UpdateChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/charts/{chart_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "patch",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateChart", response)
    else:
        body = None if 200 == 204 else response.json()

    return UpdateChartResponse(**body) if body is not None else UpdateChartResponse()
