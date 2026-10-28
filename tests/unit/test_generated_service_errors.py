"""Unit tests for the HTTPException raised by generated services on failure."""

from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from honeyhive._generated.api_config import APIConfig, HTTPException
from honeyhive._generated.services import Datasets_service as datasets_svc
from honeyhive._generated.services import async_Datasets_service as datasets_svc_async

NOT_FOUND_BODY = {
    "statusCode": 404,
    "message": "Not found",
    "success": False,
    "errorCode": "not_found",
}


def _response(
    status_code: int, json_body: Optional[Any] = None, text: Optional[str] = None
) -> httpx.Response:
    request = httpx.Request("GET", "https://api.example.com/v1/datasets")
    if json_body is not None:
        return httpx.Response(status_code, json=json_body, request=request)
    return httpx.Response(status_code, text=text or "", request=request)


def _call_sync(mock_client_cls: MagicMock, response: httpx.Response) -> HTTPException:
    mock_client = MagicMock()
    mock_client.request.return_value = response
    mock_client_cls.return_value.__enter__.return_value = mock_client
    with pytest.raises(HTTPException) as exc_info:
        datasets_svc.getDatasets(api_config_override=APIConfig(), project_id="p1")
    return exc_info.value


class TestSyncServiceErrors:
    """Sync generated services raise HTTPException with the server's details."""

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_404_includes_server_message_and_hint(
        self, mock_client_cls: MagicMock
    ) -> None:
        """A 404 includes the server message and both possible causes."""
        exc = _call_sync(mock_client_cls, _response(404, NOT_FOUND_BODY))

        assert exc.status_code == 404
        assert exc.server_message == "Not found"
        assert exc.error_code == "not_found"
        assert exc.message == (
            "getDatasets failed with status code: 404: Not found "
            "(the resource does not exist or the API key lacks access to it)"
        )
        assert str(exc) == f"404 {exc.message}"

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_non_404_includes_server_message_without_hint(
        self, mock_client_cls: MagicMock
    ) -> None:
        """Non-404 errors include the server message but no 404 hint."""
        body = {
            "statusCode": 400,
            "message": "Invalid query parameters",
            "success": False,
            "errorCode": "bad_request",
        }
        exc = _call_sync(mock_client_cls, _response(400, body))

        assert exc.status_code == 400
        assert exc.error_code == "bad_request"
        assert exc.message == (
            "getDatasets failed with status code: 400: Invalid query parameters"
        )

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_non_json_body_falls_back_to_status_only(
        self, mock_client_cls: MagicMock
    ) -> None:
        """A non-JSON body (e.g. proxy HTML) falls back to the status code."""
        exc = _call_sync(
            mock_client_cls, _response(502, text="<html>Bad Gateway</html>")
        )

        assert exc.status_code == 502
        assert exc.server_message is None
        assert exc.error_code is None
        assert exc.message == "getDatasets failed with status code: 502"

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_404_without_body_still_includes_hint(
        self, mock_client_cls: MagicMock
    ) -> None:
        """A 404 with an empty body still names both possible causes."""
        exc = _call_sync(mock_client_cls, _response(404))

        assert exc.server_message is None
        assert exc.message == (
            "getDatasets failed with status code: 404 "
            "(the resource does not exist or the API key lacks access to it)"
        )

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_json_body_without_message_field(self, mock_client_cls: MagicMock) -> None:
        """A JSON body without a message falls back to the status code."""
        exc = _call_sync(mock_client_cls, _response(500, ["unexpected"]))

        assert exc.server_message is None
        assert exc.message == "getDatasets failed with status code: 500"


class TestAsyncServiceErrors:
    """Async generated services raise the same HTTPException as sync ones."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Datasets_service.httpx.AsyncClient")
    async def test_404_includes_server_message_and_hint(
        self, mock_client_cls: MagicMock
    ) -> None:
        """A 404 includes the server message and both possible causes."""
        mock_client = MagicMock()
        mock_client.request = AsyncMock(return_value=_response(404, NOT_FOUND_BODY))
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await datasets_svc_async.getDatasets(
                api_config_override=APIConfig(), project_id="p1"
            )

        exc = exc_info.value
        assert exc.status_code == 404
        assert exc.server_message == "Not found"
        assert exc.error_code == "not_found"
        assert exc.message == (
            "getDatasets failed with status code: 404: Not found "
            "(the resource does not exist or the API key lacks access to it)"
        )

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Datasets_service.httpx.AsyncClient")
    async def test_non_json_body_falls_back_to_status_only(
        self, mock_client_cls: MagicMock
    ) -> None:
        """A non-JSON body (e.g. proxy HTML) falls back to the status code."""
        mock_client = MagicMock()
        mock_client.request = AsyncMock(
            return_value=_response(502, text="<html>Bad Gateway</html>")
        )
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await datasets_svc_async.getDatasets(
                api_config_override=APIConfig(), project_id="p1"
            )

        assert exc_info.value.status_code == 502
        assert exc_info.value.message == "getDatasets failed with status code: 502"
