from typing import *

from ..api_config import APIConfig, HTTPException, _make_request
from ..models import *


def createEvent(
    api_config_override: Optional[APIConfig] = None, *, data: CreateEventRequestBody
) -> CreateEventResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = _make_request(api_config, "post", path, headers, params=query_params, json=data.model_dump(exclude_none=True))

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEvent failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return CreateEventResponse(**body) if body is not None else CreateEventResponse()


def updateEvent(
    api_config_override: Optional[APIConfig] = None, *, data: UpdateEventRequest
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = _make_request(api_config, "put", path, headers, params=query_params, json=data.model_dump(exclude_none=True))

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateEvent failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def getEvents(
    api_config_override: Optional[APIConfig] = None, *, data: GetEventsRequest
) -> GetEventsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = _make_request(api_config, "post", path, headers, params=query_params, json=data.model_dump(exclude_none=True))

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getEvents failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return GetEventsResponse(**body) if body is not None else GetEventsResponse()


def createModelEvent(
    api_config_override: Optional[APIConfig] = None,
    *,
    data: CreateModelEventRequestBody,
) -> CreateEventResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = _make_request(api_config, "post", path, headers, params=query_params, json=data.model_dump(exclude_none=True))

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createModelEvent failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return CreateEventResponse(**body) if body is not None else CreateEventResponse()


def createEventBatch(
    api_config_override: Optional[APIConfig] = None, *, data: CreateEventBatchRequest
) -> CreateEventBatchResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = _make_request(api_config, "post", path, headers, params=query_params, json=data.model_dump(exclude_none=True))

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createEventBatch failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateEventBatchResponse(**body)
        if body is not None
        else CreateEventBatchResponse()
    )


def createModelEventBatch(
    api_config_override: Optional[APIConfig] = None,
    *,
    data: CreateModelEventBatchRequest,
) -> CreateModelEventBatchResponse:
    api_config = api_config_override if api_config_override else APIConfig()

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

    response = _make_request(api_config, "post", path, headers, params=query_params, json=data.model_dump(exclude_none=True))

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createModelEventBatch failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateModelEventBatchResponse(**body)
        if body is not None
        else CreateModelEventBatchResponse()
    )
