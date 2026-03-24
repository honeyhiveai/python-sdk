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
import tempfile

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    query,
)
from openinference.instrumentation.claude_agent_sdk import ClaudeAgentSDKInstrumentor

from honeyhive import HoneyHiveTracer

WORK_DIR = tempfile.mkdtemp(prefix="claude_agent_sdk_example_")


async def run_single_query_scenario() -> None:
    """Scenario 1: single query() call with tool access.

    Uses Write and Read tools to create and inspect a customer order file.
    """
    print("\n--- Scenario 1: Single query with tools ---")
    async for message in query(
        prompt=(
            "Write a JSON file at {work_dir}/orders.json with this content:\n"
            "{{\n"
            '  "ORD-1001": {{"state": "shipped", "eta_days": 2}},\n'
            '  "ORD-1002": {{"state": "processing", "eta_days": 5}},\n'
            '  "ORD-1003": {{"state": "delayed", "eta_days": 8}}\n'
            "}}\n"
            "Then read it back and summarize the order with the longest ETA."
        ).format(work_dir=WORK_DIR),
        options=ClaudeAgentOptions(
            system_prompt=(
                "You are a support assistant. Complete file tasks concisely. "
                "Do not ask for confirmation."
            ),
            allowed_tools=["Bash", "Read", "Write"],
            max_turns=5,
            permission_mode="bypassPermissions",
            cwd=WORK_DIR,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"[Cost: ${message.total_cost_usd:.4f}]")


async def run_multi_turn_scenario() -> None:
    """Scenario 2: multi-turn conversation with ClaudeSDKClient.

    Demonstrates session continuity — the agent remembers context from turn 1
    when answering turn 2.
    """
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
            cwd=WORK_DIR,
        )
    )

    await client.connect()
    try:
        # Turn 1: ask about a specific order
        print("Turn 1:")
        await client.query(
            prompt=(f"Read {WORK_DIR}/orders.json and tell me the status of ORD-1002."),
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
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_claude_agent_sdk_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = ClaudeAgentSDKInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        await run_single_query_scenario()
        await run_multi_turn_scenario()
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
