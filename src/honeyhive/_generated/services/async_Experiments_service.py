from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def getExperimentRunsSchema(
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
            f"getExperimentRunsSchema failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunsSchemaResponse(**body)
        if body is not None
        else GetExperimentRunsSchemaResponse()
    )


async def getRuns(
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
            f"getRuns failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunsResponse(**body)
        if body is not None
        else GetExperimentRunsResponse()
    )


async def createRun(
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
            f"createRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostExperimentRunResponse(**body)
        if body is not None
        else PostExperimentRunResponse()
    )


async def getRun(
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
            f"getRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunResponse(**body)
        if body is not None
        else GetExperimentRunResponse()
    )


async def updateRun(
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
            f"updateRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PutExperimentRunResponse(**body)
        if body is not None
        else PutExperimentRunResponse()
    )


async def deleteRun(
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
            f"deleteRun failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteExperimentRunResponse(**body)
        if body is not None
        else DeleteExperimentRunResponse()
    )


async def getExperimentRunMetrics(
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
            f"getExperimentRunMetrics failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body


async def getExperimentResult(
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
            f"getExperimentResult failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunResultResponse(**body)
        if body is not None
        else GetExperimentRunResultResponse()
    )


async def getExperimentComparison(
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
            f"getExperimentComparison failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetExperimentRunCompareResponse(**body)
        if body is not None
        else GetExperimentRunCompareResponse()
    )


async def getExperimentCompareEvents(
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
            f"getExperimentCompareEvents failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body
