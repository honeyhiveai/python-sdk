#!/bin/sh
# Run from the SDK root with the provider and instrumentor dependencies installed.
set -eu

# Provider tests skip when credentials are absent. Fail before importing dependencies instead.
: "${HH_API_KEY:?HH_API_KEY is required}"
: "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"
: "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY is required}"

# Fail on missing dependencies instead of allowing pytest.importorskip to hide them.
python <<'PY'
import anthropic
import claude_agent_sdk
import openai
from openinference.instrumentation.anthropic import AnthropicInstrumentor
from openinference.instrumentation.claude_agent_sdk import ClaudeAgentSDKInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
import langchain_openai
import langgraph
import agents
import openinference.instrumentation.langchain
import openinference.instrumentation.openai_agents
import opentelemetry.instrumentation.openai
import opentelemetry.instrumentation.anthropic
import opentelemetry.instrumentation.langchain
PY

# Select client-side and server-side providers through their separate environment switches.
# Optional cloud integrations report skips when their credentials or dependencies are absent.
# Keep tests with shared evaluator state on the same worker.
exec pytest \
  tests/integration \
  -n 8 \
  --dist=loadgroup \
  --real-api \
  --asyncio-mode=auto \
  --durations=10 \
  -ra \
  "$@"
