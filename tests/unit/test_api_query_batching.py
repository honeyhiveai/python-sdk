"""Unit tests for query string array batching in the API client.

When list params (datapoint_ids, run_ids) exceed QUERY_BATCH_SIZE the client
should transparently split requests into batches and merge the results.
"""

import asyncio
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from honeyhive.api.client import (
    QUERY_BATCH_SIZE,
    DatapointsAPI,
    ExperimentsAPI,
    _chunk_list,
)
from honeyhive._generated.models.Pagination import Pagination


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_datapoints_response(ids: List[str]) -> MagicMock:
    """Build a mock GetDatapointsResponse with a .datapoints list."""
    resp = MagicMock()
    resp.datapoints = [{"id": dp_id} for dp_id in ids]
    return resp


def _make_runs_response(
    run_ids: List[str], metrics: List[str] | None = None
) -> MagicMock:
    """Build a mock GetExperimentRunsResponse."""
    resp = MagicMock()
    resp.evaluations = [{"run_id": rid} for rid in run_ids]
    resp.metrics = metrics or ["accuracy"]
    resp.pagination = Pagination(
        page=1,
        limit=len(run_ids),
        total=len(run_ids),
        total_unfiltered=len(run_ids),
        total_pages=1,
        has_next=False,
        has_prev=False,
    )
    return resp


def _make_api(cls: type) -> Any:
    """Instantiate a DatapointsAPI or ExperimentsAPI with a mock config."""
    mock_config = MagicMock()
    mock_config.base_path = "https://api.test"
    mock_config.get_access_token.return_value = "tok"
    mock_config.verify = True
    return cls(mock_config)


# ---------------------------------------------------------------------------
# _chunk_list
# ---------------------------------------------------------------------------


class TestChunkList:
    def test_empty(self) -> None:
        assert _chunk_list([], 100) == []

    def test_under_size(self) -> None:
        assert _chunk_list(["a", "b"], 100) == [["a", "b"]]

    def test_exact_multiple(self) -> None:
        items = list(range(6))
        assert _chunk_list(items, 3) == [[0, 1, 2], [3, 4, 5]]

    def test_remainder(self) -> None:
        items = list(range(7))
        assert _chunk_list(items, 3) == [[0, 1, 2], [3, 4, 5], [6]]


# ---------------------------------------------------------------------------
# DatapointsAPI.list
# ---------------------------------------------------------------------------


class TestDatapointsListBatching:
    @patch("honeyhive.api.client.datapoints_svc")
    def test_small_list_makes_single_call(self, mock_svc: MagicMock) -> None:
        """Lists <= QUERY_BATCH_SIZE should pass through directly."""
        ids = [f"id_{i}" for i in range(50)]
        expected = _make_datapoints_response(ids)
        mock_svc.getDatapoints.return_value = expected

        api = _make_api(DatapointsAPI)
        result = api.list(datapoint_ids=ids)

        mock_svc.getDatapoints.assert_called_once()
        assert result is expected

    @patch("honeyhive.api.client.datapoints_svc")
    def test_none_passes_through(self, mock_svc: MagicMock) -> None:
        """None datapoint_ids should pass through without batching."""
        expected = _make_datapoints_response([])
        mock_svc.getDatapoints.return_value = expected

        api = _make_api(DatapointsAPI)
        result = api.list(datapoint_ids=None)

        mock_svc.getDatapoints.assert_called_once()
        assert result is expected

    @patch("honeyhive.api.client.datapoints_svc")
    def test_large_list_batches_and_merges(self, mock_svc: MagicMock) -> None:
        """Lists > QUERY_BATCH_SIZE should be split into batches."""
        total = QUERY_BATCH_SIZE + 50
        all_ids = [f"id_{i}" for i in range(total)]

        mock_svc.getDatapoints.side_effect = [
            _make_datapoints_response(all_ids[:QUERY_BATCH_SIZE]),
            _make_datapoints_response(all_ids[QUERY_BATCH_SIZE:]),
        ]

        api = _make_api(DatapointsAPI)
        result = api.list(datapoint_ids=all_ids)

        assert mock_svc.getDatapoints.call_count == 2
        assert len(result.datapoints) == total

    @patch("honeyhive.api.client.datapoints_svc")
    def test_exact_boundary_no_batch(self, mock_svc: MagicMock) -> None:
        """Exactly QUERY_BATCH_SIZE items should NOT trigger batching."""
        ids = [f"id_{i}" for i in range(QUERY_BATCH_SIZE)]
        expected = _make_datapoints_response(ids)
        mock_svc.getDatapoints.return_value = expected

        api = _make_api(DatapointsAPI)
        result = api.list(datapoint_ids=ids)

        mock_svc.getDatapoints.assert_called_once()
        assert result is expected

    @patch("honeyhive.api.client.datapoints_svc")
    def test_dataset_name_forwarded_to_each_batch(
        self, mock_svc: MagicMock
    ) -> None:
        """dataset_name should be forwarded to every batch request."""
        total = QUERY_BATCH_SIZE + 10
        all_ids = [f"id_{i}" for i in range(total)]

        mock_svc.getDatapoints.side_effect = [
            _make_datapoints_response(all_ids[:QUERY_BATCH_SIZE]),
            _make_datapoints_response(all_ids[QUERY_BATCH_SIZE:]),
        ]

        api = _make_api(DatapointsAPI)
        api.list(datapoint_ids=all_ids, dataset_name="my-dataset")

        for c in mock_svc.getDatapoints.call_args_list:
            assert c.kwargs["dataset_name"] == "my-dataset"


# ---------------------------------------------------------------------------
# DatapointsAPI.list_async
# ---------------------------------------------------------------------------


class TestDatapointsListAsyncBatching:
    @patch("honeyhive.api.client.datapoints_svc_async")
    def test_large_list_batches_async(self, mock_svc: MagicMock) -> None:
        """Async: lists > QUERY_BATCH_SIZE should batch and merge."""
        total = QUERY_BATCH_SIZE + 30
        all_ids = [f"id_{i}" for i in range(total)]

        mock_svc.getDatapoints = AsyncMock(
            side_effect=[
                _make_datapoints_response(all_ids[:QUERY_BATCH_SIZE]),
                _make_datapoints_response(all_ids[QUERY_BATCH_SIZE:]),
            ]
        )

        api = _make_api(DatapointsAPI)
        result = asyncio.get_event_loop().run_until_complete(
            api.list_async(datapoint_ids=all_ids)
        )

        assert mock_svc.getDatapoints.call_count == 2
        assert len(result.datapoints) == total


# ---------------------------------------------------------------------------
# ExperimentsAPI.list_runs
# ---------------------------------------------------------------------------


class TestExperimentsListRunsBatching:
    @patch("honeyhive.api.client.experiments_svc")
    def test_small_list_makes_single_call(self, mock_svc: MagicMock) -> None:
        ids = [f"run_{i}" for i in range(50)]
        expected = _make_runs_response(ids)
        mock_svc.getRuns.return_value = expected

        api = _make_api(ExperimentsAPI)
        result = api.list_runs(run_ids=ids)

        mock_svc.getRuns.assert_called_once()
        assert result is expected

    @patch("honeyhive.api.client.experiments_svc")
    def test_large_list_batches_and_merges(self, mock_svc: MagicMock) -> None:
        total = QUERY_BATCH_SIZE + 20
        all_ids = [f"run_{i}" for i in range(total)]

        mock_svc.getRuns.side_effect = [
            _make_runs_response(all_ids[:QUERY_BATCH_SIZE], metrics=["accuracy", "f1"]),
            _make_runs_response(all_ids[QUERY_BATCH_SIZE:], metrics=["f1", "latency"]),
        ]

        api = _make_api(ExperimentsAPI)
        result = api.list_runs(run_ids=all_ids)

        assert mock_svc.getRuns.call_count == 2
        assert len(result.evaluations) == total
        # Metrics should be deduplicated and order-preserved.
        assert result.metrics == ["accuracy", "f1", "latency"]
        assert result.pagination.total == total

    @patch("honeyhive.api.client.experiments_svc")
    def test_none_run_ids_passes_through(self, mock_svc: MagicMock) -> None:
        expected = _make_runs_response([])
        mock_svc.getRuns.return_value = expected

        api = _make_api(ExperimentsAPI)
        result = api.list_runs(run_ids=None)

        mock_svc.getRuns.assert_called_once()
        assert result is expected


# ---------------------------------------------------------------------------
# ExperimentsAPI.list_runs_async
# ---------------------------------------------------------------------------


class TestExperimentsListRunsAsyncBatching:
    @patch("honeyhive.api.client.experiments_svc_async")
    def test_large_list_batches_async(self, mock_svc: MagicMock) -> None:
        total = QUERY_BATCH_SIZE + 10
        all_ids = [f"run_{i}" for i in range(total)]

        mock_svc.getRuns = AsyncMock(
            side_effect=[
                _make_runs_response(all_ids[:QUERY_BATCH_SIZE]),
                _make_runs_response(all_ids[QUERY_BATCH_SIZE:]),
            ]
        )

        api = _make_api(ExperimentsAPI)
        result = asyncio.get_event_loop().run_until_complete(
            api.list_runs_async(run_ids=all_ids)
        )

        assert mock_svc.getRuns.call_count == 2
        assert len(result.evaluations) == total
