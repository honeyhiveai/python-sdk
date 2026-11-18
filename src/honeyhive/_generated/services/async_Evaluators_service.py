from typing import *

import httpx

from ..api_config import (
    APIConfig,
    HTTPException,
    _raise_http_exception,
    _serialize_query_params,
)
from ..models import *


async def listEvaluators(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> ListEvaluatorsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"page": page, "limit": limit}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("listEvaluators", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        ListEvaluatorsResponse(**body) if body is not None else ListEvaluatorsResponse()
    )


async def createEvaluator(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    data: CreateEvaluatorRequest,
) -> CreateEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 201:
        _raise_http_exception("createEvaluator", response)
    else:
        body = None if 201 == 204 else response.json()

    return (
        CreateEvaluatorResponse(**body)
        if body is not None
        else CreateEvaluatorResponse()
    )


async def getEvaluator(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
) -> GetEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getEvaluator", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetEvaluatorResponse(**body) if body is not None else GetEvaluatorResponse()


async def replaceEvaluator(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
    data: ReplaceUpdateEvaluatorRequest,
) -> ReplaceUpdateEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("replaceEvaluator", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        ReplaceUpdateEvaluatorResponse(**body)
        if body is not None
        else ReplaceUpdateEvaluatorResponse()
    )


async def archiveEvaluator(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
) -> DeleteEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("archiveEvaluator", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        DeleteEvaluatorResponse(**body)
        if body is not None
        else DeleteEvaluatorResponse()
    )


async def listEvaluatorVersions(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> ListEvaluatorVersionsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}/versions"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {"page": page, "limit": limit}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("listEvaluatorVersions", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        ListEvaluatorVersionsResponse(**body)
        if body is not None
        else ListEvaluatorVersionsResponse()
    )


async def getEvaluatorVersion(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
    version: int,
) -> GetEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}/versions/{version}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("getEvaluatorVersion", response)
    else:
        body = None if 200 == 204 else response.json()

    return GetEvaluatorResponse(**body) if body is not None else GetEvaluatorResponse()


async def publishEvaluator(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
    version: int,
) -> PublishEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}/versions/{version}/publish"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("publishEvaluator", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        PublishEvaluatorResponse(**body)
        if body is not None
        else PublishEvaluatorResponse()
    )


async def unpublishEvaluator(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    evaluator_id_or_slug: str,
) -> UnpublishEvaluatorResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/evaluators/{evaluator_id_or_slug}/unpublish"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        _raise_http_exception("unpublishEvaluator", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        UnpublishEvaluatorResponse(**body)
        if body is not None
        else UnpublishEvaluatorResponse()
    )
