from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def getConfigurations(
    api_config_override: Optional[APIConfig] = None,
    *,
    project: str,
    env: Optional[str] = None,
    name: Optional[str] = None,
) -> List[Configuration]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
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
            f"getConfigurations failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return [Configuration(**item) for item in body]


def createConfiguration(
    api_config_override: Optional[APIConfig] = None, *, data: PostConfigurationRequest
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
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
            f"createConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def updateConfiguration(
    api_config_override: Optional[APIConfig] = None,
    *,
    id: str,
    data: PutConfigurationRequest,
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
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
            f"updateConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def deleteConfiguration(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
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
            f"deleteConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None
