"""Shared helpers for tests that drive the mock-llm service through the
OpenAI Python SDK.

The leading underscore keeps pytest from collecting this file as a test
module. Imported by integration tests that swap out real OpenAI for
mock-llm's OpenAI-compatible endpoint at ``http://localhost:9025/v1``.
This mirrors the centralization pattern already used by
``_experiments_helpers.require_server_side_eval_creds`` so all mock-llm
config lives in one place.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI

# Path-style model targets mock-llm's ``deterministic`` provider, which has
# no latency and ``error_rate: 0``. See mock_provider_config.yaml.
MOCK_LLM_MODEL = "deterministic/default/default"
MOCK_LLM_BASE_URL = "http://localhost:9025/v1"

# Mirror of ``mock_llm_service.main.MOCK_RESPONSE``. Kept here so tests can
# assert exact equality against the mocked response without reaching into the
# service package. If the service's constant changes, the streaming test will
# fail loudly — that's intentional: it surfaces the drift rather than letting
# it silently weaken the assertion.
MOCK_RESPONSE = "This is a mock explanation. Rating: [[5]]"


def mock_openai_client() -> OpenAI:
    """Return an OpenAI SDK client wired to mock-llm.

    Reads ``MOCK_LLM_API_KEY`` from env with a fallback to the literal
    that mock-llm's container starts with in ``config/dev.env``, matching
    the pattern used by the TS mock-llm tests.

    The ``openai`` import is deferred to the call site so importing this
    helper does not promote ``openai`` to a collection-time hard dep —
    callers can still use ``pytest.importorskip("openai")`` at the test
    level for environments without the ``openinference-openai`` extra.
    """
    from openai import OpenAI

    return OpenAI(
        api_key=os.environ.get("MOCK_LLM_API_KEY", "mock-llm-api-key"),
        base_url=MOCK_LLM_BASE_URL,
    )
