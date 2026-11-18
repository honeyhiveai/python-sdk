"""Evaluator facade calls use project-scoped routes and the data plane key."""

import inspect
import os
from typing import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from honeyhive import MissingApiKeyError
from honeyhive.api.client import HoneyHive, evaluators_svc, evaluators_svc_async
from honeyhive.models import (
    CreateEvaluatorRequest,
    EvaluatorMetadata,
    HumanEvaluatorConfig,
    HumanEvaluatorDefinition,
    ReplaceUpdateEvaluatorRequest,
    ScoreSchema,
)
from tests.integration import _data_plane_operations as operations

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32
DEFINITION = {
    "type": "human",
    "human": {"name": "Example", "metadata": {}, "score_schema": {}},
}
CREATE = CreateEvaluatorRequest.model_validate(
    {"slug": "example", "definition": DEFINITION}
)
REPLACE = ReplaceUpdateEvaluatorRequest.model_validate({"definition": DEFINITION})
CASES = [
    ("create", "createEvaluator", (CREATE,), {}, {"data": CREATE}),
    ("list", "listEvaluators", (), {"page": 2, "limit": 5}, {"page": 2, "limit": 5}),
    ("get", "getEvaluator", ("example",), {}, {"evaluator_id_or_slug": "example"}),
    (
        "replace",
        "replaceEvaluator",
        ("example", REPLACE),
        {},
        {"evaluator_id_or_slug": "example", "data": REPLACE},
    ),
    (
        "archive",
        "archiveEvaluator",
        ("example",),
        {},
        {"evaluator_id_or_slug": "example"},
    ),
    (
        "list_versions",
        "listEvaluatorVersions",
        ("example",),
        {"page": 2, "limit": 5},
        {"evaluator_id_or_slug": "example", "page": 2, "limit": 5},
    ),
    (
        "get_version",
        "getEvaluatorVersion",
        ("example", 3),
        {},
        {"evaluator_id_or_slug": "example", "version": 3},
    ),
    (
        "publish",
        "publishEvaluator",
        ("example", 3),
        {},
        {"evaluator_id_or_slug": "example", "version": 3},
    ),
    (
        "unpublish",
        "unpublishEvaluator",
        ("example",),
        {},
        {"evaluator_id_or_slug": "example"},
    ),
]


@pytest.fixture(autouse=True)
def no_ambient_credentials() -> Iterator[None]:
    with patch.dict(os.environ, {}, clear=True):
        yield


@pytest.mark.parametrize(("method", "operation", "args", "kwargs", "expected"), CASES)
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_evaluator_method_uses_data_plane_config(
    method: str,
    operation: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    expected: dict[str, object],
    asynchronous: bool,
) -> None:
    client = HoneyHive(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
    client.api_config.timeout = 12
    client.api_config.base_path = "https://api.example.com"
    client.api_config.verify = False
    module = evaluators_svc_async if asynchronous else evaluators_svc
    send = AsyncMock() if asynchronous else MagicMock()
    with patch.object(module, operation, send):
        method_call = getattr(
            client.evaluators, method + ("_async" if asynchronous else "")
        )
        result = method_call(*args, project_id="example-project", **kwargs)
        if inspect.isawaitable(result):
            result = await result
        assert result is send.return_value
        call = send.call_args
        config = call.args[0]
        assert config.access_token == DATA_PLANE_KEY
        assert config.base_path == "https://api.example.com"
        assert config.timeout == 12
        assert config.verify is False
        assert call.kwargs == {"project_id": "example-project", **expected}
        if asynchronous:
            send.assert_awaited_once()
        else:
            send.assert_called_once()


@pytest.mark.parametrize(("method", "operation", "args", "kwargs", "expected"), CASES)
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_evaluator_never_falls_back_to_project_key(
    method: str,
    operation: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    expected: dict[str, object],
    asynchronous: bool,
) -> None:
    del expected
    client = HoneyHive(api_key=PROJECT_KEY)
    module = evaluators_svc_async if asynchronous else evaluators_svc
    with patch.object(module, operation) as send:
        with pytest.raises(MissingApiKeyError, match="Missing data plane API key"):
            method_call = getattr(
                client.evaluators, method + ("_async" if asynchronous else "")
            )
            result = method_call(*args, project_id="example-project", **kwargs)
            if inspect.isawaitable(result):
                await result
        send.assert_not_called()


def test_public_models_support_typed_definition_construction() -> None:
    definition = HumanEvaluatorDefinition(
        type="human",
        human=HumanEvaluatorConfig(
            name="Example",
            metadata=EvaluatorMetadata(),
            score_schema=ScoreSchema.model_validate({"type": "object"}),
        ),
    )
    request = CreateEvaluatorRequest(slug="example", definition=definition)
    assert request.definition is definition


def test_cleanup_does_not_mask_the_original_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = HoneyHive(data_plane_api_key=DATA_PLANE_KEY)
    with patch.object(
        client.evaluators, "archive", side_effect=RuntimeError("cleanup failed")
    ):
        with pytest.raises(AssertionError, match="original failure"):
            try:
                raise AssertionError("original failure")
            finally:
                operations._archive_evaluator_quietly(
                    client, "example", "example-project"
                )
    assert "Evaluator cleanup failed" in capsys.readouterr().out
