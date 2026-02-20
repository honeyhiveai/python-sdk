from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def getConfigurations(
    api_config_override: Optional[APIConfig] = None,
    *,
    name: Optional[str] = None,
    env: Optional[str] = None,
    tags: Optional[str] = None,
) -> List[GetConfigurationsResponse]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/configurations"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"name": name, "env": env, "tags": tags}

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

    return [GetConfigurationsResponse(**item) for item in body]


def createConfiguration(
    api_config_override: Optional[APIConfig] = None, *, data: CreateConfigurationRequest
) -> CreateConfigurationResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/configurations"
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

    return (
        CreateConfigurationResponse(**body)
        if body is not None
        else CreateConfigurationResponse()
    )


def updateConfiguration(
    api_config_override: Optional[APIConfig] = None,
    *,
    id: str,
    data: UpdateConfigurationRequest,
) -> UpdateConfigurationResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/configurations/{id}"
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

    return (
        UpdateConfigurationResponse(**body)
        if body is not None
        else UpdateConfigurationResponse()
    )


def deleteConfiguration(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> DeleteConfigurationResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/configurations/{id}"
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

    return (
        DeleteConfigurationResponse(**body)
        if body is not None
        else DeleteConfigurationResponse()
    )
