from typing import *

import httpx

from ..api_config import APIConfig, HTTPException, _serialize_query_params
from ..models import *


def getMetrics(
    api_config_override: Optional[APIConfig] = None,
    *,
    type: Optional[str] = None,
    id: Optional[str] = None,
) -> GetMetricsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"type": type, "id": id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getMetrics failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetMetricsResponse(**body) if body is not None else GetMetricsResponse()


def createMetric(
    api_config_override: Optional[APIConfig] = None, *, data: CreateMetricRequest
) -> CreateMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
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


def updateMetricLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyUpdateMetricRequest
) -> UpdateMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateMetricLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return UpdateMetricResponse(**body) if body is not None else UpdateMetricResponse()


def deleteMetricLegacy(
    api_config_override: Optional[APIConfig] = None, *, metric_id: str
) -> DeleteMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"metric_id": metric_id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteMetricLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return DeleteMetricResponse(**body) if body is not None else DeleteMetricResponse()


def updateMetric(
    api_config_override: Optional[APIConfig] = None,
    *,
    metric_id: str,
    data: UpdateMetricRequest,
) -> UpdateMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/{metric_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
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


def deleteMetric(
    api_config_override: Optional[APIConfig] = None, *, metric_id: str
) -> DeleteMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/{metric_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteMetric failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return DeleteMetricResponse(**body) if body is not None else DeleteMetricResponse()


def runMetric(
    api_config_override: Optional[APIConfig] = None, *, data: RunMetricRequest
) -> RunMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/run"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
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


def runMetricLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyRunMetricRequest
) -> RunMetricResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/metrics/run_metric"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"runMetricLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return RunMetricResponse(**body) if body is not None else RunMetricResponse()
