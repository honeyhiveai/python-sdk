from typing import *

from ..api_config import APIConfig, HTTPException, _make_request
from ..models import *


def getMetrics(
    api_config_override: Optional[APIConfig] = None, *, project_name: str
) -> List[Metric]:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"project_name": project_name}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(api_config, "get", path, headers, params=query_params)

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getMetrics failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return [Metric(**item) for item in body]


def createMetric(
    api_config_override: Optional[APIConfig] = None, *, data: Metric
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
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
            f"createMetric failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def updateMetric(
    api_config_override: Optional[APIConfig] = None, *, data: MetricEdit
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
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
            f"updateMetric failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def deleteMetric(
    api_config_override: Optional[APIConfig] = None, *, metric_id: str
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"metric_id": metric_id}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(api_config, "delete", path, headers, params=query_params)

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteMetric failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None
