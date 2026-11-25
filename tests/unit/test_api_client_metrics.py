"""Unit tests for the requests ``MetricsAPI`` sends to update and delete a metric.

``update`` takes a request with the metric's ``id`` inside it and sends that
id in the path, with the rest of the request as the body. The body must be
the JSON the body-id operation receives for the same request, minus ``id``,
including nulls nested in ``threshold`` and in a ``categories`` item, and the
call must raise no warning. The httpx client inside the generated services is
stubbed, so the real generated functions build each request and these tests
read what they would send.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Tuple
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Metrics_service as metrics_svc
from honeyhive.api.client import HoneyHive
from honeyhive.models import UpdateMetricRequest

pytestmark = pytest.mark.filterwarnings("error")

PROJECT_KEY = "hh_" + "x" * 32
METRIC_ID = "01JD6Z1Q8M5V3T0K9R2W4X7Y6B"
METRIC_PATH = f"/v1/metrics/{METRIC_ID}"
UPDATED: Dict[str, Any] = {"updated": True}
DELETED: Dict[str, Any] = {"deleted": True}

NESTED_NULLS = UpdateMetricRequest(
    id=METRIC_ID,
    name="n",
    threshold={"min": 0, "max": None},
    categories=[{"category": "good", "score": None}],
)
NON_OBJECT_CATEGORY = UpdateMetricRequest(id=METRIC_ID, categories=["good"])


def _response(body: Dict[str, Any]) -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = body
    return response


@contextmanager
def _sync_transport(body: Dict[str, Any]) -> Iterator[MagicMock]:
    """Stub the sync services' httpx client, yielding its ``request``."""
    with patch(
        "honeyhive._generated.services.Metrics_service.httpx.Client"
    ) as client_cls:
        client = MagicMock()
        client.request.return_value = _response(body)
        client_cls.return_value.__enter__.return_value = client
        yield client.request


@contextmanager
def _async_transport(body: Dict[str, Any]) -> Iterator[MagicMock]:
    """Stub the async services' httpx client, yielding its ``request``."""
    with patch(
        "honeyhive._generated.services.async_Metrics_service.httpx.AsyncClient"
    ) as client_cls:
        client = MagicMock()
        client.request = AsyncMock(return_value=_response(body))
        client_cls.return_value.__aenter__.return_value = client
        yield client.request


def _client() -> HoneyHive:
    with patch.dict(os.environ, {}, clear=True):
        return HoneyHive(api_key=PROJECT_KEY)


def _sent(request: MagicMock) -> Tuple[str, str, Dict[str, Any]]:
    """The method, path, and keyword arguments of the one request sent."""
    request.assert_called_once()
    method, url = request.call_args.args[:2]
    return method, str(url), request.call_args.kwargs


def _body_id_body(request: UpdateMetricRequest) -> Dict[str, Any]:
    """What the body-id operation sends for ``request``, without ``id``."""
    with _sync_transport(UPDATED) as sent:
        metrics_svc.updateMetricLegacy(APIConfig(), data=request)
    body: Dict[str, Any] = _sent(sent)[2]["json"]
    assert body.pop("id") == METRIC_ID
    return body


def _assert_project_key(kwargs: Dict[str, Any]) -> None:
    assert kwargs["headers"]["Authorization"] == f"Bearer {PROJECT_KEY}"


class TestUpdate:
    """``update`` sends the request's id in the path and the rest as the body."""

    def test_update_sends_the_id_in_the_path(self) -> None:
        with _sync_transport(UPDATED) as sent:
            result = _client().metrics.update(
                UpdateMetricRequest(id=METRIC_ID, name="n")
            )

        method, path, kwargs = _sent(sent)
        assert (method, path) == ("put", METRIC_PATH)
        assert kwargs["json"] == {"name": "n"}
        _assert_project_key(kwargs)
        assert result.updated is True

    @pytest.mark.asyncio
    async def test_update_async_sends_the_id_in_the_path(self) -> None:
        with _async_transport(UPDATED) as sent:
            result = await _client().metrics.update_async(
                UpdateMetricRequest(id=METRIC_ID, name="n")
            )

        method, path, kwargs = _sent(sent)
        assert (method, path) == ("put", METRIC_PATH)
        assert kwargs["json"] == {"name": "n"}
        _assert_project_key(kwargs)
        assert result.updated is True

    def test_update_metric_alias_sends_the_same_request(self) -> None:
        with _sync_transport(UPDATED) as sent:
            _client().metrics.update_metric(UpdateMetricRequest(id=METRIC_ID, name="n"))

        method, path, kwargs = _sent(sent)
        assert (method, path) == ("put", METRIC_PATH)
        assert kwargs["json"] == {"name": "n"}
        _assert_project_key(kwargs)

    def test_update_keeps_nulls_nested_in_threshold_and_categories(self) -> None:
        with _sync_transport(UPDATED) as sent:
            _client().metrics.update(NESTED_NULLS)

        assert _sent(sent)[2]["json"] == {
            "name": "n",
            "threshold": {"min": 0, "max": None},
            "categories": [{"category": "good", "score": None}],
        }

    @pytest.mark.parametrize(
        "request_",
        [NESTED_NULLS, NON_OBJECT_CATEGORY],
        ids=["nested-nulls", "non-object-category"],
    )
    def test_update_body_is_the_body_id_body_without_id(
        self, request_: UpdateMetricRequest
    ) -> None:
        expected = _body_id_body(request_)

        with _sync_transport(UPDATED) as sent:
            _client().metrics.update(request_)

        assert _sent(sent)[2]["json"] == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "request_",
        [NESTED_NULLS, NON_OBJECT_CATEGORY],
        ids=["nested-nulls", "non-object-category"],
    )
    async def test_update_async_body_is_the_body_id_body_without_id(
        self, request_: UpdateMetricRequest
    ) -> None:
        expected = _body_id_body(request_)

        with _async_transport(UPDATED) as sent:
            await _client().metrics.update_async(request_)

        assert _sent(sent)[2]["json"] == expected


class TestDelete:
    """``delete`` sends its argument in the path and nothing in the query."""

    def test_delete_sends_the_id_in_the_path(self) -> None:
        with _sync_transport(DELETED) as sent:
            result = _client().metrics.delete(METRIC_ID)

        method, path, kwargs = _sent(sent)
        assert (method, path) == ("delete", METRIC_PATH)
        assert kwargs["params"] == []
        _assert_project_key(kwargs)
        assert result.deleted is True

    @pytest.mark.asyncio
    async def test_delete_async_sends_the_id_in_the_path(self) -> None:
        with _async_transport(DELETED) as sent:
            result = await _client().metrics.delete_async(METRIC_ID)

        method, path, kwargs = _sent(sent)
        assert (method, path) == ("delete", METRIC_PATH)
        assert kwargs["params"] == []
        _assert_project_key(kwargs)
        assert result.deleted is True

    def test_delete_metric_alias_sends_the_same_request(self) -> None:
        with _sync_transport(DELETED) as sent:
            _client().metrics.delete_metric(METRIC_ID)

        method, path, kwargs = _sent(sent)
        assert (method, path) == ("delete", METRIC_PATH)
        assert kwargs["params"] == []
        _assert_project_key(kwargs)
