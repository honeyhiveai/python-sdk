from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_experiment_runs_schema_date_range_type_1 import (
    GetExperimentRunsSchemaDateRangeType1,
)
from ...models.get_experiment_runs_schema_response import (
    GetExperimentRunsSchemaResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    date_range: GetExperimentRunsSchemaDateRangeType1 | str | Unset = UNSET,
    evaluation_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_date_range: dict[str, Any] | str | Unset
    if isinstance(date_range, Unset):
        json_date_range = UNSET
    elif isinstance(date_range, GetExperimentRunsSchemaDateRangeType1):
        json_date_range = date_range.to_dict()
    else:
        json_date_range = date_range
    params["dateRange"] = json_date_range

    params["evaluation_id"] = evaluation_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/runs/schema",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetExperimentRunsSchemaResponse | None:
    if response.status_code == 200:
        response_200 = GetExperimentRunsSchemaResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetExperimentRunsSchemaResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    date_range: GetExperimentRunsSchemaDateRangeType1 | str | Unset = UNSET,
    evaluation_id: str | Unset = UNSET,
) -> Response[GetExperimentRunsSchemaResponse]:
    """Get experiment runs schema

     Retrieve the schema and metadata for experiment runs

    Args:
        date_range (GetExperimentRunsSchemaDateRangeType1 | str | Unset):
        evaluation_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetExperimentRunsSchemaResponse]
    """

    kwargs = _get_kwargs(
        date_range=date_range,
        evaluation_id=evaluation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    date_range: GetExperimentRunsSchemaDateRangeType1 | str | Unset = UNSET,
    evaluation_id: str | Unset = UNSET,
) -> GetExperimentRunsSchemaResponse | None:
    """Get experiment runs schema

     Retrieve the schema and metadata for experiment runs

    Args:
        date_range (GetExperimentRunsSchemaDateRangeType1 | str | Unset):
        evaluation_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetExperimentRunsSchemaResponse
    """

    return sync_detailed(
        client=client,
        date_range=date_range,
        evaluation_id=evaluation_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    date_range: GetExperimentRunsSchemaDateRangeType1 | str | Unset = UNSET,
    evaluation_id: str | Unset = UNSET,
) -> Response[GetExperimentRunsSchemaResponse]:
    """Get experiment runs schema

     Retrieve the schema and metadata for experiment runs

    Args:
        date_range (GetExperimentRunsSchemaDateRangeType1 | str | Unset):
        evaluation_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetExperimentRunsSchemaResponse]
    """

    kwargs = _get_kwargs(
        date_range=date_range,
        evaluation_id=evaluation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    date_range: GetExperimentRunsSchemaDateRangeType1 | str | Unset = UNSET,
    evaluation_id: str | Unset = UNSET,
) -> GetExperimentRunsSchemaResponse | None:
    """Get experiment runs schema

     Retrieve the schema and metadata for experiment runs

    Args:
        date_range (GetExperimentRunsSchemaDateRangeType1 | str | Unset):
        evaluation_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetExperimentRunsSchemaResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            date_range=date_range,
            evaluation_id=evaluation_id,
        )
    ).parsed
