from typing import *

from ..api_config import APIConfig, HTTPException, _make_request_async
from ..models import *


async def getConfigurations(
    api_config_override: Optional[APIConfig] = None,
    *,
    project: str,
    env: Optional[str] = None,
    name: Optional[str] = None,
) -> List[Configuration]:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/configurations"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"project": project, "env": env, "name": name}

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
            f"getConfigurations failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return [Configuration(**item) for item in body]


async def createConfiguration(
    api_config_override: Optional[APIConfig] = None, *, data: CreateConfigurationRequest
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/configurations"
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
            f"createConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return None


async def updateConfiguration(
    api_config_override: Optional[APIConfig] = None,
    *,
    id: str,
    data: UpdateConfigurationRequest,
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/configurations/{id}"
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
            f"updateConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return None


async def deleteConfiguration(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/configurations/{id}"
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
            f"deleteConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return None
