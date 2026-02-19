from typing import *

from ..api_config import APIConfig, HTTPException, _make_request
from ..models import *


def getDatapoints(
    api_config_override: Optional[APIConfig] = None,
    *,
    project: str,
    datapoint_ids: Optional[List[str]] = None,
    dataset_name: Optional[str] = None,
) -> GetDatapointsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datapoints"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "project": project,
        "datapoint_ids": datapoint_ids,
        "dataset_name": dataset_name,
    }

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "get",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getDatapoints failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return GetDatapointsResponse(**body)


def createDatapoint(
    api_config_override: Optional[APIConfig] = None, *, data: CreateDatapointRequest
) -> CreateDatapointResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datapoints"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "post",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createDatapoint failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return CreateDatapointResponse(**body)


def getDatapoint(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> GetDatapointResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datapoints/{id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "get",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getDatapoint failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return GetDatapointResponse(**body)


def updateDatapoint(
    api_config_override: Optional[APIConfig] = None,
    *,
    id: str,
    data: UpdateDatapointRequest,
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datapoints/{id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "put",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateDatapoint failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return None


def deleteDatapoint(
    api_config_override: Optional[APIConfig] = None, *, id: str
) -> DeleteDatapointResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/datapoints/{id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "delete",
        path,
        headers,
        params=query_params,
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteDatapoint failed with status code: {response.status_code}",
        )
    else:
        body = response.json()

    return DeleteDatapointResponse(**body)
