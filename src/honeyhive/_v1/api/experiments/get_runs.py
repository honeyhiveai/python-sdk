from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_experiment_runs_response import GetExperimentRunsResponse
from ...models.get_runs_date_range_type_1 import GetRunsDateRangeType1
from ...models.get_runs_sort_by import GetRunsSortBy
from ...models.get_runs_sort_order import GetRunsSortOrder
from ...models.get_runs_status import GetRunsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    dataset_id: str | Unset = UNSET,
    page: int | Unset = 1,
    limit: int | Unset = 20,
    run_ids: list[str] | Unset = UNSET,
    name: str | Unset = UNSET,
    status: GetRunsStatus | Unset = UNSET,
    date_range: GetRunsDateRangeType1 | str | Unset = UNSET,
    sort_by: GetRunsSortBy | Unset = GetRunsSortBy.CREATED_AT,
    sort_order: GetRunsSortOrder | Unset = GetRunsSortOrder.DESC,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["dataset_id"] = dataset_id

    params["page"] = page

    params["limit"] = limit

    json_run_ids: list[str] | Unset = UNSET
    if not isinstance(run_ids, Unset):
        json_run_ids = run_ids

    params["run_ids"] = json_run_ids

    params["name"] = name

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    json_date_range: dict[str, Any] | str | Unset
    if isinstance(date_range, Unset):
        json_date_range = UNSET
    elif isinstance(date_range, GetRunsDateRangeType1):
        json_date_range = date_range.to_dict()
    else:
        json_date_range = date_range
    params["dateRange"] = json_date_range

    json_sort_by: str | Unset = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by.value

    params["sort_by"] = json_sort_by

    json_sort_order: str | Unset = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sort_order"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/runs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetExperimentRunsResponse | None:
    if response.status_code == 200:
        response_200 = GetExperimentRunsResponse.from_dict(response.json())

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
) -> Response[Any | GetExperimentRunsResponse]:
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
    page: int | Unset = 1,
    limit: int | Unset = 20,
    run_ids: list[str] | Unset = UNSET,
    name: str | Unset = UNSET,
    status: GetRunsStatus | Unset = UNSET,
    date_range: GetRunsDateRangeType1 | str | Unset = UNSET,
    sort_by: GetRunsSortBy | Unset = GetRunsSortBy.CREATED_AT,
    sort_order: GetRunsSortOrder | Unset = GetRunsSortOrder.DESC,
) -> Response[Any | GetExperimentRunsResponse]:
    """Get a list of evaluation runs

    Args:
        dataset_id (str | Unset):
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 20.
        run_ids (list[str] | Unset):
        name (str | Unset):
        status (GetRunsStatus | Unset):
        date_range (GetRunsDateRangeType1 | str | Unset):
        sort_by (GetRunsSortBy | Unset):  Default: GetRunsSortBy.CREATED_AT.
        sort_order (GetRunsSortOrder | Unset):  Default: GetRunsSortOrder.DESC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GetExperimentRunsResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        page=page,
        limit=limit,
        run_ids=run_ids,
        name=name,
        status=status,
        date_range=date_range,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    page: int | Unset = 1,
    limit: int | Unset = 20,
    run_ids: list[str] | Unset = UNSET,
    name: str | Unset = UNSET,
    status: GetRunsStatus | Unset = UNSET,
    date_range: GetRunsDateRangeType1 | str | Unset = UNSET,
    sort_by: GetRunsSortBy | Unset = GetRunsSortBy.CREATED_AT,
    sort_order: GetRunsSortOrder | Unset = GetRunsSortOrder.DESC,
) -> Any | GetExperimentRunsResponse | None:
    """Get a list of evaluation runs

    Args:
        dataset_id (str | Unset):
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 20.
        run_ids (list[str] | Unset):
        name (str | Unset):
        status (GetRunsStatus | Unset):
        date_range (GetRunsDateRangeType1 | str | Unset):
        sort_by (GetRunsSortBy | Unset):  Default: GetRunsSortBy.CREATED_AT.
        sort_order (GetRunsSortOrder | Unset):  Default: GetRunsSortOrder.DESC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | GetExperimentRunsResponse
    """

    return sync_detailed(
        client=client,
        dataset_id=dataset_id,
        page=page,
        limit=limit,
        run_ids=run_ids,
        name=name,
        status=status,
        date_range=date_range,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    page: int | Unset = 1,
    limit: int | Unset = 20,
    run_ids: list[str] | Unset = UNSET,
    name: str | Unset = UNSET,
    status: GetRunsStatus | Unset = UNSET,
    date_range: GetRunsDateRangeType1 | str | Unset = UNSET,
    sort_by: GetRunsSortBy | Unset = GetRunsSortBy.CREATED_AT,
    sort_order: GetRunsSortOrder | Unset = GetRunsSortOrder.DESC,
) -> Response[Any | GetExperimentRunsResponse]:
    """Get a list of evaluation runs

    Args:
        dataset_id (str | Unset):
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 20.
        run_ids (list[str] | Unset):
        name (str | Unset):
        status (GetRunsStatus | Unset):
        date_range (GetRunsDateRangeType1 | str | Unset):
        sort_by (GetRunsSortBy | Unset):  Default: GetRunsSortBy.CREATED_AT.
        sort_order (GetRunsSortOrder | Unset):  Default: GetRunsSortOrder.DESC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GetExperimentRunsResponse]
    """

    kwargs = _get_kwargs(
        dataset_id=dataset_id,
        page=page,
        limit=limit,
        run_ids=run_ids,
        name=name,
        status=status,
        date_range=date_range,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    dataset_id: str | Unset = UNSET,
    page: int | Unset = 1,
    limit: int | Unset = 20,
    run_ids: list[str] | Unset = UNSET,
    name: str | Unset = UNSET,
    status: GetRunsStatus | Unset = UNSET,
    date_range: GetRunsDateRangeType1 | str | Unset = UNSET,
    sort_by: GetRunsSortBy | Unset = GetRunsSortBy.CREATED_AT,
    sort_order: GetRunsSortOrder | Unset = GetRunsSortOrder.DESC,
) -> Any | GetExperimentRunsResponse | None:
    """Get a list of evaluation runs

    Args:
        dataset_id (str | Unset):
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 20.
        run_ids (list[str] | Unset):
        name (str | Unset):
        status (GetRunsStatus | Unset):
        date_range (GetRunsDateRangeType1 | str | Unset):
        sort_by (GetRunsSortBy | Unset):  Default: GetRunsSortBy.CREATED_AT.
        sort_order (GetRunsSortOrder | Unset):  Default: GetRunsSortOrder.DESC.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | GetExperimentRunsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            dataset_id=dataset_id,
            page=page,
            limit=limit,
            run_ids=run_ids,
            name=name,
            status=status,
            date_range=date_range,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
