from typing import *

from ..api_config import APIConfig, HTTPException, _make_request_async
from ..models import *


async def startSession(
    api_config_override: Optional[APIConfig] = None, *, data: StartSessionRequestBody
) -> StartSessionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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
            f"startSession failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return StartSessionResponse(**body)


async def getSession(
    api_config_override: Optional[APIConfig] = None, *, session_id: str
) -> Event:
    api_config = api_config_override if api_config_override else APIConfig()

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
            f"getSession failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return Event(**body)
