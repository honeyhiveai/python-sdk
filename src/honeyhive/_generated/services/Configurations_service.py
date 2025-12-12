from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def getConfigurations(
    api_config_override: Optional[APIConfig] = None, *, project: Optional[str] = None
) -> List[Configuration]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/configurations"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"project": project}

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
    api_config_override: Optional[APIConfig] = None, *, data: CreateConfigurationRequest
) -> CreateConfigurationResponse:
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
            json=data.dict(),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createConfiguration failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateConfigurationResponse(**body)
        if body is not None
        else CreateConfigurationResponse()
    )
