from typing import *

import httpx

from ..api_config import (
    APIConfig,
    HTTPException,
    _raise_http_exception,
    _serialize_query_params,
)
from ..models import *


def getQueuesLegacy(
    api_config_override: Optional[APIConfig] = None, *, enabled: Optional[bool] = None
) -> GetAnnotationQueuesResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/queues"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"enabled": enabled}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getQueuesLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetAnnotationQueuesResponse(**body)
        if body is not None
        else GetAnnotationQueuesResponse()
    )


def createQueueLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    data: CreateAnnotationQueueRequest,
) -> CreateAnnotationQueueResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/queues"
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

    if response.status_code != 201:
        _raise_http_exception("createQueueLegacy", response)
    else:
        body = None if 201 == 204 else response.json()

    return (
        CreateAnnotationQueueResponse(**body)
        if body is not None
        else CreateAnnotationQueueResponse()
    )


def getQueues(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    enabled: Optional[bool] = None,
) -> GetAnnotationQueuesResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/queues"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"enabled": enabled}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getQueues", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetAnnotationQueuesResponse(**body)
        if body is not None
        else GetAnnotationQueuesResponse()
    )


def createQueue(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    data: CreateAnnotationQueueRequest,
) -> CreateAnnotationQueueResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/queues"
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

    if response.status_code != 201:
        _raise_http_exception("createQueue", response)
    else:
        body = None if 201 == 204 else response.json()

    return (
        CreateAnnotationQueueResponse(**body)
        if body is not None
        else CreateAnnotationQueueResponse()
    )


def getQueueLegacy(
    api_config_override: Optional[APIConfig] = None, *, queue_id: str
) -> GetAnnotationQueueByIdResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/queues/{queue_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getQueueLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetAnnotationQueueByIdResponse(**body)
        if body is not None
        else GetAnnotationQueueByIdResponse()
    )


def updateQueueLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    queue_id: str,
    data: UpdateAnnotationQueueRequest,
) -> UpdateAnnotationQueueResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/queues/{queue_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateQueueLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        UpdateAnnotationQueueResponse(**body)
        if body is not None
        else UpdateAnnotationQueueResponse()
    )


def deleteQueueLegacy(
    api_config_override: Optional[APIConfig] = None, *, queue_id: str
) -> DeleteAnnotationQueueResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/queues/{queue_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteQueueLegacy", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteAnnotationQueueResponse(**body)
        if body is not None
        else DeleteAnnotationQueueResponse()
    )


def getQueue(
    api_config_override: Optional[APIConfig] = None, *, project_id: str, queue_id: str
) -> GetAnnotationQueueByIdResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/queues/{queue_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getQueue", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetAnnotationQueueByIdResponse(**body)
        if body is not None
        else GetAnnotationQueueByIdResponse()
    )


def deleteQueue(
    api_config_override: Optional[APIConfig] = None, *, project_id: str, queue_id: str
) -> DeleteAnnotationQueueResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/queues/{queue_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("deleteQueue", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteAnnotationQueueResponse(**body)
        if body is not None
        else DeleteAnnotationQueueResponse()
    )


def updateQueue(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    queue_id: str,
    data: UpdateAnnotationQueueRequest,
) -> UpdateAnnotationQueueResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/queues/{queue_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "patch",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("updateQueue", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        UpdateAnnotationQueueResponse(**body)
        if body is not None
        else UpdateAnnotationQueueResponse()
    )
