"""
Configuration for integration tests with external providers.

These tests require real API keys and make actual API calls.
They are skipped by default unless the required environment variables are set.
"""

import os
import pytest
from typing import Optional


def pytest_configure(config):
    """Configure pytest markers for integration tests."""
    config.addinivalue_line(
        "markers", "openai: marks tests requiring OpenAI API key"
    )
    config.addinivalue_line(
        "markers", "anthropic: marks tests requiring Anthropic API key"
    )
    config.addinivalue_line(
        "markers", "langchain: marks tests requiring LangChain + OpenAI"
    )
    config.addinivalue_line(
        "markers", "litellm: marks tests requiring LiteLLM"
    )
    config.addinivalue_line(
        "markers", "bedrock: marks tests requiring AWS Bedrock"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


# Skip conditions
def skip_if_no_openai():
    """Skip if OPENAI_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )


def skip_if_no_anthropic():
    """Skip if ANTHROPIC_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )


def skip_if_no_honeyhive():
    """Skip if HH_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("HH_API_KEY"),
        reason="HH_API_KEY not set"
    )


# Fixtures
@pytest.fixture
def api_key() -> Optional[str]:
    """Get HoneyHive API key from environment."""
    return os.getenv("HH_API_KEY")


@pytest.fixture
def project() -> str:
    """Get HoneyHive project from environment."""
    return os.getenv("HH_PROJECT", "sdk-integration-tests")


@pytest.fixture
def openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment."""
    return os.getenv("OPENAI_API_KEY")


@pytest.fixture
def anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment."""
    return os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture(autouse=True)
def reset_otel_state():
    """Reset OpenTelemetry state between tests."""
    from opentelemetry import context, trace
    
    # Reset context
    context.attach(context.Context())
    
    yield
    
    # Cleanup after test
    context.attach(context.Context())
