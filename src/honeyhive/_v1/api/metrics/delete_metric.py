from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_metric_response import DeleteMetricResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    metric_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["metric_id"] = metric_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/metrics",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteMetricResponse | None:
    if response.status_code == 200:
        response_200 = DeleteMetricResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteMetricResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    metric_id: str,
) -> Response[DeleteMetricResponse]:
    """Delete a metric

     Remove a metric

    Args:
        metric_id (str): Unique identifier of the metric

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteMetricResponse]
    """

    kwargs = _get_kwargs(
        metric_id=metric_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    metric_id: str,
) -> DeleteMetricResponse | None:
    """Delete a metric

     Remove a metric

    Args:
        metric_id (str): Unique identifier of the metric

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteMetricResponse
    """

    return sync_detailed(
        client=client,
        metric_id=metric_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    metric_id: str,
) -> Response[DeleteMetricResponse]:
    """Delete a metric

     Remove a metric

    Args:
        metric_id (str): Unique identifier of the metric

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteMetricResponse]
    """

    kwargs = _get_kwargs(
        metric_id=metric_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    metric_id: str,
) -> DeleteMetricResponse | None:
    """Delete a metric

     Remove a metric

    Args:
        metric_id (str): Unique identifier of the metric

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteMetricResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            metric_id=metric_id,
        )
    ).parsed
