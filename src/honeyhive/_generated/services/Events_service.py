from typing import *

import httpx

from ..api_config import APIConfig, HTTPException, _serialize_query_params
from ..models import *


def createEventLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyPostEventRequest
) -> PostEventResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEventLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return PostEventResponse(**body) if body is not None else PostEventResponse()


def updateEventLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyUpdateEventRequest
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateEventLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def createEvent(
    api_config_override: Optional[APIConfig] = None, *, data: PostEventRequest
) -> PostEventResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return PostEventResponse(**body) if body is not None else PostEventResponse()


def updateEvent(
    api_config_override: Optional[APIConfig] = None,
    *,
    event_id: str,
    data: UpdateEventRequest,
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/{event_id}"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "put",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def exportEventsLegacy(
    api_config_override: Optional[APIConfig] = None, *, data: LegacyExportEventsRequest
) -> ExportEventsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/export"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"exportEventsLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return ExportEventsResponse(**body) if body is not None else ExportEventsResponse()


def searchEvents(
    api_config_override: Optional[APIConfig] = None, *, data: SearchEventsRequest
) -> ExportEventsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/search"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"searchEvents failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return ExportEventsResponse(**body) if body is not None else ExportEventsResponse()


def createEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: PostEventBatchRequest
) -> PostEventBatchResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/batch"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEventBatch failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostEventBatchResponse(**body) if body is not None else PostEventBatchResponse()
    )


def createModelEvent(
    api_config_override: Optional[APIConfig] = None, *, data: PostModelEventRequest
) -> PostEventResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/model"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createModelEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return PostEventResponse(**body) if body is not None else PostEventResponse()


def createEventBatchLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    data: LegacyPostEventBatchRequest,
) -> PostEventBatchResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/batch"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEventBatchLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostEventBatchResponse(**body) if body is not None else PostEventBatchResponse()
    )


def createModelEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: PostModelEventBatchRequest
) -> PostEventBatchResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events/model/batch"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createModelEventBatch failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        PostEventBatchResponse(**body) if body is not None else PostEventBatchResponse()
    )


def getEventsSchemaLegacy(
    api_config_override: Optional[APIConfig] = None,
    *,
    dateRange: Optional[Union[str, GetEventsSchemaLegacyDateRangeOneOf1]] = None,
    evaluation_id: Optional[str] = None,
) -> GetEventsSchemaResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/schema"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {
        "dateRange": dateRange,
        "evaluation_id": evaluation_id,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getEventsSchemaLegacy failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetEventsSchemaResponse(**body)
        if body is not None
        else GetEventsSchemaResponse()
    )
