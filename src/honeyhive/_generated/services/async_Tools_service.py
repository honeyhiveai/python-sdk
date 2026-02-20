from typing import *

from ..api_config import APIConfig, HTTPException, _make_request_async
from ..models import *


async def getTools(api_config_override: Optional[APIConfig] = None) -> List[Tool]:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/tools"
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
            f"getTools failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return [Tool(**item) for item in body]


async def createTool(
    api_config_override: Optional[APIConfig] = None, *, data: CreateToolRequest
) -> CreateToolResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/tools"
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
            f"createTool failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return CreateToolResponse(**body)


async def updateTool(
    api_config_override: Optional[APIConfig] = None, *, data: UpdateToolRequest
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/tools"
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
            f"updateTool failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return None


async def deleteTool(
    api_config_override: Optional[APIConfig] = None, *, function_id: str
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/tools"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"function_id": function_id}

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
            f"deleteTool failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return None
