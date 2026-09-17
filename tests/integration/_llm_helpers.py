"""Configure provider clients for integration tests.

SDK_TEST_LLM_PROVIDER selects mock or live calls for create_llm_client.
LangChain tests always use live OpenAI. Server-side evaluators select providers separately.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI
    from openai import OpenAI

# Use one model across live OpenAI integrations and server-side evaluations.
LIVE_OPENAI_MODEL = "gpt-5.6-luna"

# Keep this equal to the deterministic mock service response to detect streaming corruption.
MOCK_RESPONSE = "This is a mock explanation. Rating: [[5]]"


class CompletionOptions(TypedDict, total=False):
    """Allow each provider to receive its supported completion parameters."""

    max_tokens: int
    max_completion_tokens: int
    reasoning_effort: Literal["low"]


def using_mock_llm() -> bool:
    """Require an explicit opt-in before tests incur provider charges."""
    provider = os.environ.get("SDK_TEST_LLM_PROVIDER", "mock")
    if provider not in ("mock", "openai"):
        raise ValueError("SDK_TEST_LLM_PROVIDER must be mock or openai")
    return provider == "mock"


def get_llm_model() -> str:
    """Match the model name to the selected client-side provider."""
    if using_mock_llm():
        return "deterministic/default/default"
    return LIVE_OPENAI_MODEL


def get_completion_options(mock_max_tokens: int) -> CompletionOptions:
    """Reserve tokens for reasoning without changing the mock request limits."""
    if using_mock_llm():
        return {"max_tokens": mock_max_tokens}
    return {"max_completion_tokens": 1024, "reasoning_effort": "low"}


def create_live_langchain_client() -> ChatOpenAI:
    """Share live model settings across LangChain and LangGraph tests."""
    # Keep the optional dependency out of test collection.
    from langchain_openai import ChatOpenAI

    # GPT-5 counts reasoning tokens against the completion limit.
    return ChatOpenAI(
        model=LIVE_OPENAI_MODEL,
        base_url="https://api.openai.com/v1",
        max_completion_tokens=1024,
        reasoning_effort="low",
    )


def create_llm_client() -> OpenAI:
    """Keep client-side provider selection independent of other OpenAI tests."""
    mock = using_mock_llm()
    api_key = (
        os.environ.get("MOCK_LLM_API_KEY", "mock-llm-api-key")
        if mock
        else os.environ.get("OPENAI_API_KEY", "")
    )
    if not mock and not api_key.strip():
        raise ValueError("OPENAI_API_KEY is required when SDK_TEST_LLM_PROVIDER=openai")

    # Keep the optional OpenAI dependency out of test collection.
    from openai import OpenAI

    return OpenAI(
        api_key=api_key,
        base_url="http://localhost:9025/v1" if mock else "https://api.openai.com/v1",
    )
