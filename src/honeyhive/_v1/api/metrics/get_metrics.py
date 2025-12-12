from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_metrics_response_item import GetMetricsResponseItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    type_: str | Unset = UNSET,
    id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["type"] = type_

    params["id"] = id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metrics",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[list[GetMetricsResponseItem]] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = []
            _response_200_item = response_200_item_data
            for componentsschemas_get_metrics_response_item_data in _response_200_item:
                componentsschemas_get_metrics_response_item = (
                    GetMetricsResponseItem.from_dict(
                        componentsschemas_get_metrics_response_item_data
                    )
                )

                response_200_item.append(componentsschemas_get_metrics_response_item)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list[list[GetMetricsResponseItem]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    type_: str | Unset = UNSET,
    id: str | Unset = UNSET,
) -> Response[list[list[GetMetricsResponseItem]]]:
    """Get all metrics

     Retrieve a list of all metrics

    Args:
        type_ (str | Unset):
        id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[list[GetMetricsResponseItem]]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    type_: str | Unset = UNSET,
    id: str | Unset = UNSET,
) -> list[list[GetMetricsResponseItem]] | None:
    """Get all metrics

     Retrieve a list of all metrics

    Args:
        type_ (str | Unset):
        id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[list[GetMetricsResponseItem]]
    """

    return sync_detailed(
        client=client,
        type_=type_,
        id=id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    type_: str | Unset = UNSET,
    id: str | Unset = UNSET,
) -> Response[list[list[GetMetricsResponseItem]]]:
    """Get all metrics

     Retrieve a list of all metrics

    Args:
        type_ (str | Unset):
        id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[list[GetMetricsResponseItem]]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    type_: str | Unset = UNSET,
    id: str | Unset = UNSET,
) -> list[list[GetMetricsResponseItem]] | None:
    """Get all metrics

     Retrieve a list of all metrics

    Args:
        type_ (str | Unset):
        id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[list[GetMetricsResponseItem]]
    """

    return (
        await asyncio_detailed(
            client=client,
            type_=type_,
            id=id,
        )
    ).parsed
