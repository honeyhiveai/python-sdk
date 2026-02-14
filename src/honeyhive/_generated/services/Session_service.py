from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def startSession(
    api_config_override: Optional[APIConfig] = None, *, data: StartSessionRequestBody
) -> StartSessionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/session/start"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify, timeout=api_config.timeout) as client:
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
            f"startSession failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return StartSessionResponse(**body) if body is not None else StartSessionResponse()


def getSession(
    api_config_override: Optional[APIConfig] = None, *, session_id: str
) -> Event:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/session/{session_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify, timeout=api_config.timeout) as client:
        response = client.request(
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

    return Event(**body) if body is not None else Event()
