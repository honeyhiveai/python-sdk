from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_experiment_comparison_aggregate_function import (
    GetExperimentComparisonAggregateFunction,
)
from ...models.todo_schema import TODOSchema
from ...types import UNSET, Response, Unset


def _get_kwargs(
    run_id_1: str,
    run_id_2: str,
    *,
    project_id: str,
    aggregate_function: GetExperimentComparisonAggregateFunction | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["project_id"] = project_id

    json_aggregate_function: str | Unset = UNSET
    if not isinstance(aggregate_function, Unset):
        json_aggregate_function = aggregate_function.value

    params["aggregate_function"] = json_aggregate_function

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/runs/{run_id_1}/compare-with/{run_id_2}".format(
            run_id_1=quote(str(run_id_1), safe=""),
            run_id_2=quote(str(run_id_2), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | TODOSchema | None:
    if response.status_code == 200:
        response_200 = TODOSchema.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | TODOSchema]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    run_id_1: str,
    run_id_2: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentComparisonAggregateFunction | Unset = UNSET,
) -> Response[Any | TODOSchema]:
    """Retrieve experiment comparison

    Args:
        run_id_1 (str):
        run_id_2 (str):
        project_id (str):
        aggregate_function (GetExperimentComparisonAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | TODOSchema]
    """

    kwargs = _get_kwargs(
        run_id_1=run_id_1,
        run_id_2=run_id_2,
        project_id=project_id,
        aggregate_function=aggregate_function,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    run_id_1: str,
    run_id_2: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentComparisonAggregateFunction | Unset = UNSET,
) -> Any | TODOSchema | None:
    """Retrieve experiment comparison

    Args:
        run_id_1 (str):
        run_id_2 (str):
        project_id (str):
        aggregate_function (GetExperimentComparisonAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | TODOSchema
    """

    return sync_detailed(
        run_id_1=run_id_1,
        run_id_2=run_id_2,
        client=client,
        project_id=project_id,
        aggregate_function=aggregate_function,
    ).parsed


async def asyncio_detailed(
    run_id_1: str,
    run_id_2: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentComparisonAggregateFunction | Unset = UNSET,
) -> Response[Any | TODOSchema]:
    """Retrieve experiment comparison

    Args:
        run_id_1 (str):
        run_id_2 (str):
        project_id (str):
        aggregate_function (GetExperimentComparisonAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | TODOSchema]
    """

    kwargs = _get_kwargs(
        run_id_1=run_id_1,
        run_id_2=run_id_2,
        project_id=project_id,
        aggregate_function=aggregate_function,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    run_id_1: str,
    run_id_2: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentComparisonAggregateFunction | Unset = UNSET,
) -> Any | TODOSchema | None:
    """Retrieve experiment comparison

    Args:
        run_id_1 (str):
        run_id_2 (str):
        project_id (str):
        aggregate_function (GetExperimentComparisonAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | TODOSchema
    """

    return (
        await asyncio_detailed(
            run_id_1=run_id_1,
            run_id_2=run_id_2,
            client=client,
            project_id=project_id,
            aggregate_function=aggregate_function,
        )
    ).parsed
