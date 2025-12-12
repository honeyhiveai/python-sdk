from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_session_params import DeleteSessionParams
from ...models.delete_session_response import DeleteSessionResponse
from ...types import Response


def _get_kwargs(
    session_id: DeleteSessionParams,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/sessions/{session_id}".format(
            session_id=quote(str(session_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | DeleteSessionResponse | None:
    if response.status_code == 200:
        response_200 = DeleteSessionResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | DeleteSessionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    session_id: DeleteSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | DeleteSessionResponse]:
    """Delete all events for a session

     Delete all events associated with the given session ID from both events and aggregates tables

    Args:
        session_id (DeleteSessionParams): Path parameters for deleting a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteSessionResponse]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    session_id: DeleteSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Any | DeleteSessionResponse | None:
    """Delete all events for a session

     Delete all events associated with the given session ID from both events and aggregates tables

    Args:
        session_id (DeleteSessionParams): Path parameters for deleting a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DeleteSessionResponse
    """

    return sync_detailed(
        session_id=session_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    session_id: DeleteSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | DeleteSessionResponse]:
    """Delete all events for a session

     Delete all events associated with the given session ID from both events and aggregates tables

    Args:
        session_id (DeleteSessionParams): Path parameters for deleting a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteSessionResponse]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    session_id: DeleteSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Any | DeleteSessionResponse | None:
    """Delete all events for a session

     Delete all events associated with the given session ID from both events and aggregates tables

    Args:
        session_id (DeleteSessionParams): Path parameters for deleting a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DeleteSessionResponse
    """

    return (
        await asyncio_detailed(
            session_id=session_id,
            client=client,
        )
    ).parsed
