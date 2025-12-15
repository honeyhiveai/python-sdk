from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def getTools(api_config_override: Optional[APIConfig] = None) -> List[GetToolsResponse]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/tools"
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
            f"getTools failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return [GetToolsResponse(**item) for item in body]


def createTool(
    api_config_override: Optional[APIConfig] = None, *, data: CreateToolRequest
) -> CreateToolResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/tools"
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
            f"createTool failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return CreateToolResponse(**body) if body is not None else CreateToolResponse()


def updateTool(
    api_config_override: Optional[APIConfig] = None, *, data: UpdateToolRequest
) -> UpdateToolResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/tools"
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
            f"updateTool failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return UpdateToolResponse(**body) if body is not None else UpdateToolResponse()


def deleteTool(
    api_config_override: Optional[APIConfig] = None, *, function_id: str
) -> DeleteToolResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/tools"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"function_id": function_id}

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
            f"deleteTool failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return DeleteToolResponse(**body) if body is not None else DeleteToolResponse()
