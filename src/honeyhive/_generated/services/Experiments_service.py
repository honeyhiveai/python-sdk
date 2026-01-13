from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def getExperimentRunsSchema(
    api_config_override: Optional[APIConfig] = None,
    *,
    dateRange: Optional[Union[str, Dict[str, Any]]] = None,
    evaluation_id: Optional[str] = None,
) -> GetExperimentRunsSchemaResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/schema"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "dateRange": dateRange,
        "evaluation_id": evaluation_id,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentRunsSchema failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunsSchemaResponse(**body)
        if body is not None
        else GetExperimentRunsSchemaResponse()
    )


def getRuns(
    api_config_override: Optional[APIConfig] = None,
    *,
    dataset_id: Optional[str] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None,
    run_ids: Optional[List[str]] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    dateRange: Optional[Union[str, Dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> GetExperimentRunsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "dataset_id": dataset_id,
        "page": page,
        "limit": limit,
        "run_ids": run_ids,
        "name": name,
        "status": status,
        "dateRange": dateRange,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getRuns failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunsResponse(**body)
        if body is not None
        else GetExperimentRunsResponse()
    )


def createRun(
    api_config_override: Optional[APIConfig] = None, *, data: PostExperimentRunRequest
) -> PostExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostExperimentRunResponse(**body)
        if body is not None
        else PostExperimentRunResponse()
    )


def getRun(
    api_config_override: Optional[APIConfig] = None, *, run_id: str
) -> GetExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/{run_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunResponse(**body)
        if body is not None
        else GetExperimentRunResponse()
    )


def updateRun(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    data: PutExperimentRunRequest,
) -> PutExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/{run_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=query_params,
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PutExperimentRunResponse(**body)
        if body is not None
        else PutExperimentRunResponse()
    )


def deleteRun(
    api_config_override: Optional[APIConfig] = None, *, run_id: str
) -> DeleteExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/{run_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteExperimentRunResponse(**body)
        if body is not None
        else DeleteExperimentRunResponse()
    )


def getExperimentRunMetrics(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    dateRange: Optional[str] = None,
    filters: Optional[Union[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/{run_id}/metrics"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"dateRange": dateRange, "filters": filters}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentRunMetrics failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body


def getExperimentResult(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    aggregate_function: Optional[str] = None,
    filters: Optional[Union[str, List[Dict[str, Any]]]] = None,
) -> GetExperimentRunResultResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/{run_id}/result"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "aggregate_function": aggregate_function,
        "filters": filters,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentResult failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunResultResponse(**body)
        if body is not None
        else GetExperimentRunResultResponse()
    )


def getExperimentComparison(
    api_config_override: Optional[APIConfig] = None,
    *,
    new_run_id: str,
    old_run_id: str,
    aggregate_function: Optional[str] = None,
    filters: Optional[Union[str, List[Dict[str, Any]]]] = None,
) -> GetExperimentRunCompareResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/{new_run_id}/compare-with/{old_run_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "aggregate_function": aggregate_function,
        "filters": filters,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentComparison failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunCompareResponse(**body)
        if body is not None
        else GetExperimentRunCompareResponse()
    )


def getExperimentCompareEvents(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id_1: str,
    run_id_2: str,
    event_name: Optional[str] = None,
    event_type: Optional[str] = None,
    filter: Optional[Union[str, Dict[str, Any]]] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/runs/compare/events"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "run_id_1": run_id_1,
        "run_id_2": run_id_2,
        "event_name": event_name,
        "event_type": event_type,
        "filter": filter,
        "limit": limit,
        "page": page,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentCompareEvents failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body
