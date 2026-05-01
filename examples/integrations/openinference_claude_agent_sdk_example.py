#!/usr/bin/env python3
"""
Claude Agent SDK (OpenInference) + HoneyHive integration example.

Demonstrates HoneyHive tracing for the Anthropic Claude Agents SDK
using the OpenInference Claude Agent SDK instrumentor (BYOI).

Install:
    pip install honeyhive[openinference-claude-agent-sdk]
    # or, equivalently:
    # pip install honeyhive openinference-instrumentation-claude-agent-sdk claude-agent-sdk

Run:
    python examples/integrations/openinference_claude_agent_sdk_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")

Tool spans (upstream instrumentor):
    The OpenInference instrumentor may emit two TOOL spans per tool call (hooks plus
    message-stream handling). HoneyHive does not deduplicate them in the UI.

Calling query:
    After instrument(), use ``claude_agent_sdk.query(...)``, or import ``query``
    only after ``instrument()``. Importing ``query`` before ``instrument()`` binds
    the unwrapped function (the instrumentor updates the package attribute, not
    existing local names).
"""

import asyncio
import os

import claude_agent_sdk
from claude_agent_sdk import ClaudeAgentOptions
from openinference.instrumentation.claude_agent_sdk import ClaudeAgentSDKInstrumentor

from honeyhive import HoneyHiveTracer


async def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_claude_agent_sdk_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    instrumentor = ClaudeAgentSDKInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        options = ClaudeAgentOptions(allowed_tools=["Glob"])

        # The prompt asks the agent to use an allowed tool so tool-level spans
        # are emitted beneath the agent span.
        prompt = (
            "Use the Glob tool to list the first 20 .py files in the current "
            "working directory. Then briefly summarize what you found."
        )

        async for message in claude_agent_sdk.query(prompt=prompt, options=options):
            # The SDK yields multiple intermediate messages; the final one
            # includes the aggregated result.
            result = getattr(message, "result", None)
            if result is not None:
                print(f"Agent result: {result}")
    finally:
        tracer.flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
