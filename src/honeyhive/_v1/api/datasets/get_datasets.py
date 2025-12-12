from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_datasets_response import GetDatasetsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    dataset_id: str | Unset = UNSET,
    name: str | Unset = UNSET,
    include_datapoints: bool | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["dataset_id"] = dataset_id

    params["name"] = name

    json_include_datapoints: bool | str | Unset
    if isinstance(include_datapoints, Unset):
        json_include_datapoints = UNSET
    else:
        json_include_datapoints = include_datapoints
    params["include_datapoints"] = json_include_datapoints

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/datasets",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetDatasetsResponse | None:
    if response.status_code == 200:
        response_200 = GetDatasetsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetDatasetsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    name: str | Unset = UNSET,
    include_datapoints: bool | str | Unset = UNSET,
) -> Response[GetDatasetsResponse]:
    """Get datasets

    Args:
        dataset_id (str | Unset):
        name (str | Unset):
        include_datapoints (bool | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDatasetsResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        name=name,
        include_datapoints=include_datapoints,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    name: str | Unset = UNSET,
    include_datapoints: bool | str | Unset = UNSET,
) -> GetDatasetsResponse | None:
    """Get datasets

    Args:
        dataset_id (str | Unset):
        name (str | Unset):
        include_datapoints (bool | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDatasetsResponse
    """

    return sync_detailed(
        client=client,
        dataset_id=dataset_id,
        name=name,
        include_datapoints=include_datapoints,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    name: str | Unset = UNSET,
    include_datapoints: bool | str | Unset = UNSET,
) -> Response[GetDatasetsResponse]:
    """Get datasets

    Args:
        dataset_id (str | Unset):
        name (str | Unset):
        include_datapoints (bool | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDatasetsResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        name=name,
        include_datapoints=include_datapoints,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    name: str | Unset = UNSET,
    include_datapoints: bool | str | Unset = UNSET,
) -> GetDatasetsResponse | None:
    """Get datasets

    Args:
        dataset_id (str | Unset):
        name (str | Unset):
        include_datapoints (bool | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDatasetsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            dataset_id=dataset_id,
            name=name,
            include_datapoints=include_datapoints,
        )
    ).parsed
