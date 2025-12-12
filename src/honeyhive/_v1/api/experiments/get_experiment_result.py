from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_experiment_result_aggregate_function import (
    GetExperimentResultAggregateFunction,
)
from ...models.todo_schema import TODOSchema
from ...types import UNSET, Response, Unset


def _get_kwargs(
    run_id: str,
    *,
    project_id: str,
    aggregate_function: GetExperimentResultAggregateFunction | Unset = UNSET,
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
        "url": "/runs/{run_id}/result".format(
            run_id=quote(str(run_id), safe=""),
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
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentResultAggregateFunction | Unset = UNSET,
) -> Response[Any | TODOSchema]:
    """Retrieve experiment result

    Args:
        run_id (str):
        project_id (str):
        aggregate_function (GetExperimentResultAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | TODOSchema]
    """

    kwargs = _get_kwargs(
        run_id=run_id,
        project_id=project_id,
        aggregate_function=aggregate_function,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentResultAggregateFunction | Unset = UNSET,
) -> Any | TODOSchema | None:
    """Retrieve experiment result

    Args:
        run_id (str):
        project_id (str):
        aggregate_function (GetExperimentResultAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | TODOSchema
    """

    return sync_detailed(
        run_id=run_id,
        client=client,
        project_id=project_id,
        aggregate_function=aggregate_function,
    ).parsed


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentResultAggregateFunction | Unset = UNSET,
) -> Response[Any | TODOSchema]:
    """Retrieve experiment result

    Args:
        run_id (str):
        project_id (str):
        aggregate_function (GetExperimentResultAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | TODOSchema]
    """

    kwargs = _get_kwargs(
        run_id=run_id,
        project_id=project_id,
        aggregate_function=aggregate_function,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    project_id: str,
    aggregate_function: GetExperimentResultAggregateFunction | Unset = UNSET,
) -> Any | TODOSchema | None:
    """Retrieve experiment result

    Args:
        run_id (str):
        project_id (str):
        aggregate_function (GetExperimentResultAggregateFunction | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | TODOSchema
    """

    return (
        await asyncio_detailed(
            run_id=run_id,
            client=client,
            project_id=project_id,
            aggregate_function=aggregate_function,
        )
    ).parsed
