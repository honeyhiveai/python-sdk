from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def getSession(
    api_config_override: Optional[APIConfig] = None, *, session_id: str
) -> GetSessionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/sessions/{session_id}"
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
            f"getSession failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetSessionResponse(**body) if body is not None else GetSessionResponse()


async def deleteSession(
    api_config_override: Optional[APIConfig] = None, *, session_id: str
) -> DeleteSessionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/sessions/{session_id}"
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
            f"deleteSession failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteSessionResponse(**body) if body is not None else DeleteSessionResponse()
    )
