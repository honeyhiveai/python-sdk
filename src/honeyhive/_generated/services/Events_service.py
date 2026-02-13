from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def createEvent(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events"
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
            "post", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body


def updateEvent(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events"
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
            "put", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def getEvents(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/export"
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
            "post", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getEvents failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body


def createModelEvent(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/model"
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
            "post", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createModelEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body


def createEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/batch"
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
            "post", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEventBatch failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body


def createModelEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/model/batch"
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
            "post", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createModelEventBatch failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return body
