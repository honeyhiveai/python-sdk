from typing import *

import httpx

from ..api_config import (
    APIConfig,
    HTTPException,
    _raise_http_exception,
    _serialize_query_params,
)
from ..models import *


def startSessionLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyStartSessionRequest
) -> PostSessionStartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/session/start"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("startSessionLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostSessionStartResponse(**body)
        if body is not None
        else PostSessionStartResponse()
    )


def addSessionTracesLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    session_id: str,
    data: AddSessionTracesRequest,
) -> SessionTracesResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/session/{session_id}/traces"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("addSessionTracesLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        SessionTracesResponse(**body) if body is not None else SessionTracesResponse()
    )


def createSession(
    api_config_override: Optional[APIConfig] = None, *, data: StartSessionRequest
) -> PostSessionStartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/sessions"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createSession", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostSessionStartResponse(**body)
        if body is not None
        else PostSessionStartResponse()
    )


def createSessionEventBatch(
    api_config_override: Optional[APIConfig] = None,
    *,
    session_id: str,
    data: SessionEventBatchRequest,
) -> SessionTracesResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/sessions/{session_id}/events/batch"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createSessionEventBatch", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        SessionTracesResponse(**body) if body is not None else SessionTracesResponse()
    )
