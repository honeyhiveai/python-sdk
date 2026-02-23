from typing import *

from ..api_config import APIConfig, HTTPException, _make_request_async
from ..models import *


async def getRuns(
    api_config_override: Optional[APIConfig] = None, *, project: Optional[str] = None
) -> GetRunsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
        api_config,
        "get",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getRuns failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return GetRunsResponse(**body)


async def createRun(
    api_config_override: Optional[APIConfig] = None, *, data: PostExperimentRunRequest
) -> PostExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
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
            f"createRun failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return PostExperimentRunResponse(**body)


async def getRun(
    api_config_override: Optional[APIConfig] = None, *, run_id: str
) -> GetExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
        api_config,
        "get",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getRun failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return GetExperimentRunResponse(**body)


async def updateRun(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    data: PutExperimentRunRequest,
) -> PutExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
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
            f"updateRun failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return PutExperimentRunResponse(**body)


async def deleteRun(
    api_config_override: Optional[APIConfig] = None, *, run_id: str
) -> DeleteExperimentRunResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
        api_config,
        "delete",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteRun failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return DeleteExperimentRunResponse(**body)


async def getExperimentResult(
    api_config_override: Optional[APIConfig] = None,
    *,
    run_id: str,
    project_id: str,
    aggregate_function: Optional[str] = None,
) -> ExperimentResultResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
        api_config,
        "get",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentResult failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return ExperimentResultResponse(**body)


async def getExperimentComparison(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    run_id_1: str,
    run_id_2: str,
    aggregate_function: Optional[str] = None,
) -> ExperimentComparisonResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = await _make_request_async(
        api_config,
        "get",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getExperimentComparison failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return ExperimentComparisonResponse(**body)
