#!/usr/bin/env python3
"""
Claude Agent SDK + HoneyHive integration example.

Demonstrates two Claude Agent SDK patterns with HoneyHive tracing:

1) Single query with built-in tools (query())
2) Multi-turn conversation with session continuity (ClaudeSDKClient)

The Claude Agent SDK wraps Claude Code, giving the agent access to built-in
tools like Bash, Read, Write, and Glob. The OpenInference instrumentor
captures AGENT and TOOL spans automatically.

Install:
    uv pip install honeyhive openinference-instrumentation-claude-agent-sdk claude-agent-sdk

Run:
    uv run python examples/integrations/openinference_claude_agent_sdk_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os
import shutil
import tempfile

from openinference.instrumentation.claude_agent_sdk import ClaudeAgentSDKInstrumentor

from honeyhive import HoneyHiveTracer

# claude_agent_sdk is imported inside each function so that the references
# resolve to the instrumented (wrapped) versions.  Importing at module level
# would capture the *original* functions before the instrumentor patches them,
# which causes query() spans to be silently lost.

ORDER_DATA = """\
{
  "ORD-1001": {"state": "shipped", "eta_days": 2},
  "ORD-1002": {"state": "processing", "eta_days": 5},
  "ORD-1003": {"state": "delayed", "eta_days": 8}
}"""


async def run_single_query_scenario(work_dir: str) -> None:
    """Scenario 1: single query() call with tool access.

    Uses Write and Read tools to create and inspect a customer order file.
    """
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    print("\n--- Scenario 1: Single query with tools ---")
    async for message in query(
        prompt=(
            f"Write a JSON file at {work_dir}/orders.json with this content:\n"
            f"{ORDER_DATA}\n"
            "Then read it back and summarize the order with the longest ETA."
        ),
        options=ClaudeAgentOptions(
            system_prompt=(
                "You are a support assistant. Complete file tasks concisely. "
                "Do not ask for confirmation."
            ),
            allowed_tools=["Bash", "Read", "Write"],
            max_turns=5,
            # bypassPermissions: allows unrestricted tool use without interactive
            # prompts. Use only in sandboxed or non-interactive environments.
            permission_mode="bypassPermissions",
            cwd=work_dir,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"[Cost: ${message.total_cost_usd:.4f}]")


async def run_multi_turn_scenario(work_dir: str) -> None:
    """Scenario 2: multi-turn conversation with ClaudeSDKClient.

    Demonstrates session continuity -- the agent remembers context from turn 1
    when answering turn 2.
    """
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeSDKClient,
        TextBlock,
    )

    print("\n--- Scenario 2: Multi-turn conversation ---")
    client = ClaudeSDKClient(
        options=ClaudeAgentOptions(
            system_prompt=(
                "You are a customer support agent. Use available tools to "
                "look up information from files. Keep responses concise."
            ),
            allowed_tools=["Bash", "Read"],
            max_turns=3,
            permission_mode="bypassPermissions",
            cwd=work_dir,
        )
    )

    await client.connect()
    try:
        # Turn 1: ask about a specific order
        print("Turn 1:")
        await client.query(
            prompt=f"Read {work_dir}/orders.json and tell me the status of ORD-1002.",
        )
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  {block.text}")

        # Turn 2: follow-up referencing previous context
        print("Turn 2:")
        await client.query(
            prompt="What about ORD-1003? Is it delayed? What should the customer expect?",
        )
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  {block.text}")
    finally:
        await client.disconnect()


async def main() -> None:
    """Run Claude Agent SDK scenarios with HoneyHive tracing."""
    work_dir = tempfile.mkdtemp(prefix="claude_agent_sdk_example_")

    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_claude_agent_sdk_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = ClaudeAgentSDKInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        await run_single_query_scenario(work_dir)
        await run_multi_turn_scenario(work_dir)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
