from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_datapoint_request_type_0 import CreateDatapointRequestType0
from ...models.create_datapoint_request_type_1_item import (
    CreateDatapointRequestType1Item,
)
from ...models.create_datapoint_response import CreateDatapointResponse
from ...types import Response


def _get_kwargs(
    *,
    body: CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/datapoints",
    }

    if isinstance(body, CreateDatapointRequestType0):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = []
        for componentsschemas_create_datapoint_request_type_1_item_data in body:
            componentsschemas_create_datapoint_request_type_1_item = (
                componentsschemas_create_datapoint_request_type_1_item_data.to_dict()
            )
            _kwargs["json"].append(
                componentsschemas_create_datapoint_request_type_1_item
            )

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateDatapointResponse | None:
    if response.status_code == 200:
        response_200 = CreateDatapointResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateDatapointResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item],
) -> Response[CreateDatapointResponse]:
    """Create a new datapoint

    Args:
        body (CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDatapointResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item],
) -> CreateDatapointResponse | None:
    """Create a new datapoint

    Args:
        body (CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateDatapointResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item],
) -> Response[CreateDatapointResponse]:
    """Create a new datapoint

    Args:
        body (CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDatapointResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item],
) -> CreateDatapointResponse | None:
    """Create a new datapoint

    Args:
        body (CreateDatapointRequestType0 | list[CreateDatapointRequestType1Item]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateDatapointResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
