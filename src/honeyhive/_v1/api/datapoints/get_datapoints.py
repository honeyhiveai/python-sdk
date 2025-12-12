from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    datapoint_ids: list[str] | Unset = UNSET,
    dataset_name: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_datapoint_ids: list[str] | Unset = UNSET
    if not isinstance(datapoint_ids, Unset):
        json_datapoint_ids = datapoint_ids

    params["datapoint_ids"] = json_datapoint_ids

    params["dataset_name"] = dataset_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/datapoints",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    datapoint_ids: list[str] | Unset = UNSET,
    dataset_name: str | Unset = UNSET,
) -> Response[Any]:
    """Retrieve a list of datapoints

    Args:
        datapoint_ids (list[str] | Unset):
        dataset_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        datapoint_ids=datapoint_ids,
        dataset_name=dataset_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    datapoint_ids: list[str] | Unset = UNSET,
    dataset_name: str | Unset = UNSET,
) -> Response[Any]:
    """Retrieve a list of datapoints

    Args:
        datapoint_ids (list[str] | Unset):
        dataset_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        datapoint_ids=datapoint_ids,
        dataset_name=dataset_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
