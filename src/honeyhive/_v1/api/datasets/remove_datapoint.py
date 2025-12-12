from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.remove_datapoint_response import RemoveDatapointResponse
from ...types import Response


def _get_kwargs(
    dataset_id: str,
    datapoint_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/datasets/{dataset_id}/datapoints/{datapoint_id}".format(
            dataset_id=quote(str(dataset_id), safe=""),
            datapoint_id=quote(str(datapoint_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RemoveDatapointResponse | None:
    if response.status_code == 200:
        response_200 = RemoveDatapointResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[RemoveDatapointResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_id: str,
    datapoint_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[RemoveDatapointResponse]:
    """Remove a datapoint from a dataset

    Args:
        dataset_id (str):
        datapoint_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RemoveDatapointResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        datapoint_id=datapoint_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_id: str,
    datapoint_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> RemoveDatapointResponse | None:
    """Remove a datapoint from a dataset

    Args:
        dataset_id (str):
        datapoint_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RemoveDatapointResponse
    """

    return sync_detailed(
        dataset_id=dataset_id,
        datapoint_id=datapoint_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    dataset_id: str,
    datapoint_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[RemoveDatapointResponse]:
    """Remove a datapoint from a dataset

    Args:
        dataset_id (str):
        datapoint_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RemoveDatapointResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        datapoint_id=datapoint_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_id: str,
    datapoint_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> RemoveDatapointResponse | None:
    """Remove a datapoint from a dataset

    Args:
        dataset_id (str):
        datapoint_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RemoveDatapointResponse
    """

    return (
        await asyncio_detailed(
            dataset_id=dataset_id,
            datapoint_id=datapoint_id,
            client=client,
        )
    ).parsed
