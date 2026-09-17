"""Keep paid provider calls opt-in without changing mock integration behavior."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import Mock

import pytest

from tests.integration._llm_helpers import (
    create_live_langchain_client,
    create_llm_client,
    get_completion_options,
    get_llm_model,
    using_mock_llm,
)


@pytest.fixture(autouse=True)
def clear_llm_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent developer credentials from changing provider-selection expectations."""
    for name in (
        "SDK_TEST_LLM_PROVIDER",
        "MOCK_LLM_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def openai_constructor(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Exercise configuration without requiring or calling the optional provider SDK."""
    constructor = Mock()
    module = ModuleType("openai")
    monkeypatch.setattr(module, "OpenAI", constructor, raising=False)
    monkeypatch.setitem(sys.modules, "openai", module)
    return constructor


@pytest.mark.parametrize("provider", [None, "mock"])
def test_mock_is_the_default(
    monkeypatch: pytest.MonkeyPatch, openai_constructor: Mock, provider: str | None
) -> None:
    if provider is not None:
        monkeypatch.setenv("SDK_TEST_LLM_PROVIDER", provider)
    monkeypatch.setenv("OPENAI_API_KEY", "unused-live-key")

    assert using_mock_llm()
    assert get_llm_model() == "deterministic/default/default"
    assert get_completion_options(20) == {"max_tokens": 20}
    create_llm_client()
    openai_constructor.assert_called_once_with(
        api_key="mock-llm-api-key", base_url="http://localhost:9025/v1"
    )


def test_mock_key_override(
    monkeypatch: pytest.MonkeyPatch, openai_constructor: Mock
) -> None:
    monkeypatch.setenv("MOCK_LLM_API_KEY", "custom-mock-key")
    create_llm_client()
    openai_constructor.assert_called_once_with(
        api_key="custom-mock-key", base_url="http://localhost:9025/v1"
    )


def test_live_openai_configuration(
    monkeypatch: pytest.MonkeyPatch, openai_constructor: Mock
) -> None:
    monkeypatch.setenv("SDK_TEST_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    # A global endpoint override must not redirect an explicitly selected live call.
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:9025/v1")
    assert not using_mock_llm()
    assert get_llm_model() == "gpt-5.6-luna"
    assert get_completion_options(20) == {
        "max_completion_tokens": 1024,
        "reasoning_effort": "low",
    }
    create_llm_client()
    openai_constructor.assert_called_once_with(
        api_key="test-openai-key", base_url="https://api.openai.com/v1"
    )


@pytest.mark.parametrize("api_key", [None, "", " "])
def test_live_openai_requires_credentials(
    monkeypatch: pytest.MonkeyPatch, api_key: str | None
) -> None:
    monkeypatch.setenv("SDK_TEST_LLM_PROVIDER", "openai")
    if api_key is not None:
        monkeypatch.setenv("OPENAI_API_KEY", api_key)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        create_llm_client()


@pytest.mark.parametrize("provider", ["", "typo", "anthropic"])
def test_invalid_provider_fails(monkeypatch: pytest.MonkeyPatch, provider: str) -> None:
    monkeypatch.setenv("SDK_TEST_LLM_PROVIDER", provider)
    with pytest.raises(
        ValueError, match="SDK_TEST_LLM_PROVIDER must be mock or openai"
    ):
        create_llm_client()
    with pytest.raises(
        ValueError, match="SDK_TEST_LLM_PROVIDER must be mock or openai"
    ):
        get_llm_model()


def test_langchain_client_uses_live_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """A global mock endpoint must not redirect the live-only LangChain tests."""
    monkeypatch.setenv("SDK_TEST_LLM_PROVIDER", "mock")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:9025/v1")
    constructor = Mock()
    module = ModuleType("langchain_openai")
    monkeypatch.setattr(module, "ChatOpenAI", constructor, raising=False)
    monkeypatch.setitem(sys.modules, "langchain_openai", module)

    create_live_langchain_client()

    constructor.assert_called_once_with(
        model="gpt-5.6-luna",
        base_url="https://api.openai.com/v1",
        max_completion_tokens=1024,
        reasoning_effort="low",
    )
