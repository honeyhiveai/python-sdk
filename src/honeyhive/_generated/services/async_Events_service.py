from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def getEvents(
    api_config_override: Optional[APIConfig] = None,
    *,
    dateRange: Optional[Union[str, Dict[str, Any]]] = None,
    filters: Optional[Union[List[Dict[str, Any]], str]] = None,
    projections: Optional[Union[List[str], str]] = None,
    ignore_order: Optional[Union[bool, str]] = None,
    limit: Optional[Union[int, str]] = None,
    page: Optional[Union[int, str]] = None,
    evaluation_id: Optional[str] = None,
) -> GetEventsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/events"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "dateRange": dateRange,
        "filters": filters,
        "projections": projections,
        "ignore_order": ignore_order,
        "limit": limit,
        "page": page,
        "evaluation_id": evaluation_id,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getEvents failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetEventsResponse(**body) if body is not None else GetEventsResponse()


async def createEvent(
    api_config_override: Optional[APIConfig] = None, *, data: Dict[str, Any]
) -> PostEventResponse:
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

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post", httpx.URL(path), headers=headers, params=query_params, json=data
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return PostEventResponse(**body) if body is not None else PostEventResponse()


async def updateEvent(
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

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
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


async def getEventsChart(
    api_config_override: Optional[APIConfig] = None,
    *,
    dateRange: Optional[Union[str, Dict[str, Any]]] = None,
    filters: Optional[Union[List[Dict[str, Any]], str]] = None,
    metric: Optional[str] = None,
    groupBy: Optional[str] = None,
    bucket: Optional[str] = None,
    aggregation: Optional[str] = None,
    evaluation_id: Optional[str] = None,
    only_experiments: Optional[Union[bool, str]] = None,
) -> GetEventsChartResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/chart"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "dateRange": dateRange,
        "filters": filters,
        "metric": metric,
        "groupBy": groupBy,
        "bucket": bucket,
        "aggregation": aggregation,
        "evaluation_id": evaluation_id,
        "only_experiments": only_experiments,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getEventsChart failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetEventsChartResponse(**body) if body is not None else GetEventsChartResponse()
    )


async def getEventsBySessionId(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> GetEventsBySessionIdResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/{id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getEventsBySessionId failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetEventsBySessionIdResponse(**body)
        if body is not None
        else GetEventsBySessionIdResponse()
    )


async def deleteEvent(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> DeleteEventResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/{id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteEvent failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return DeleteEventResponse(**body) if body is not None else DeleteEventResponse()


async def exportEvents(
    api_config_override: Optional[APIConfig] = None, *, data: GetEventsLegacyRequest
) -> GetEventsLegacyResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/events/export"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"exportEvents failed with status code: {response.status_code}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        GetEventsLegacyResponse(**body)
        if body is not None
        else GetEventsLegacyResponse()
    )


async def createModelEvent(
    api_config_override: Optional[APIConfig] = None, *, data: PostModelEventRequest
) -> PostEventResponse:
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

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
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


async def createEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: PostEventBatchRequest
) -> PostEventBatchResponse:
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

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
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


async def createModelEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: PostModelEventBatchRequest
) -> PostEventBatchResponse:
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

    async with httpx.AsyncClient(
        base_url=base_path, verify=api_config.verify
    ) as client:
        response = await client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
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
