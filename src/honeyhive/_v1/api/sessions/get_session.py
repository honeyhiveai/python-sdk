from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_session_params import GetSessionParams
from ...models.get_session_response import GetSessionResponse
from ...types import Response


def _get_kwargs(
    session_id: GetSessionParams,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sessions/{session_id}".format(
            session_id=quote(str(session_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetSessionResponse | None:
    if response.status_code == 200:
        response_200 = GetSessionResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | GetSessionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    session_id: GetSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | GetSessionResponse]:
    """Get session tree by session ID

     Retrieve a complete session event tree including all nested events and metadata

    Args:
        session_id (GetSessionParams): Path parameters for retrieving a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GetSessionResponse]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    session_id: GetSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Any | GetSessionResponse | None:
    """Get session tree by session ID

     Retrieve a complete session event tree including all nested events and metadata

    Args:
        session_id (GetSessionParams): Path parameters for retrieving a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | GetSessionResponse
    """

    return sync_detailed(
        session_id=session_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    session_id: GetSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | GetSessionResponse]:
    """Get session tree by session ID

     Retrieve a complete session event tree including all nested events and metadata

    Args:
        session_id (GetSessionParams): Path parameters for retrieving a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GetSessionResponse]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    session_id: GetSessionParams,
    *,
    client: AuthenticatedClient | Client,
) -> Any | GetSessionResponse | None:
    """Get session tree by session ID

     Retrieve a complete session event tree including all nested events and metadata

    Args:
        session_id (GetSessionParams): Path parameters for retrieving a session by ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | GetSessionResponse
    """

    return (
        await asyncio_detailed(
            session_id=session_id,
            client=client,
        )
    ).parsed
