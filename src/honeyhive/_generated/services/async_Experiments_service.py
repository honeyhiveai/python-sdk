from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def getRuns(
    api_config_override: Optional[APIConfig] = None, *, project: Optional[str] = None
) -> GetRunsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"project": project}

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

    return GetRunsResponse(**body) if body is not None else GetRunsResponse()


async def createRun(
    api_config_override: Optional[APIConfig] = None, *, data: CreateRunRequest
) -> CreateRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs"
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

    return CreateRunResponse(**body) if body is not None else CreateRunResponse()


async def getRun(
    api_config_override: Optional[APIConfig] = None, *, run_id: str
) -> GetRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs/{run_id}"
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

    return GetRunResponse(**body) if body is not None else GetRunResponse()


async def updateRun(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    data: UpdateRunRequest,
) -> UpdateRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs/{run_id}"
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

    return UpdateRunResponse(**body) if body is not None else UpdateRunResponse()


async def deleteRun(
    api_config_override: Optional[APIConfig] = None, *, run_id: str
) -> DeleteRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs/{run_id}"
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

    return DeleteRunResponse(**body) if body is not None else DeleteRunResponse()


async def getExperimentResult(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    project_id: str,
    aggregate_function: Optional[str] = None,
) -> ExperimentResultResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs/{run_id}/result"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "project_id": project_id,
        "aggregate_function": aggregate_function,
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
        ExperimentResultResponse(**body)
        if body is not None
        else ExperimentResultResponse()
    )


async def getExperimentComparison(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    run_id_1: str,
    run_id_2: str,
    aggregate_function: Optional[str] = None,
) -> ExperimentComparisonResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/runs/{run_id_1}/compare-with/{run_id_2}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "project_id": project_id,
        "aggregate_function": aggregate_function,
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
        ExperimentComparisonResponse(**body)
        if body is not None
        else ExperimentComparisonResponse()
    )
