#!/usr/bin/env python3
"""
PydanticAI (OpenAI) + HoneyHive Integration Example: Agent with tools

This example demonstrates how to trace PydanticAI agents in HoneyHive using
PydanticAI's built-in OpenTelemetry instrumentation, wired to HoneyHive's
`tracer.provider`.

Requirements:
  pip install honeyhive pydantic-ai python-dotenv

Environment Variables (repo root .env):
  HH_API_KEY
  HH_PROJECT
  OPENAI_API_KEY
"""

import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    # Load environment variables from repo root .env
    root_dir = Path(__file__).parent.parent.parent
    load_dotenv(root_dir / ".env")

    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([hh_api_key, hh_project, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        print("\nAdd them to python-sdk/.env and try again.")
        return 1

    try:
        from honeyhive import HoneyHiveTracer

        from pydantic_ai import Agent, RunContext
        from pydantic_ai.models.instrumented import InstrumentationSettings

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive pydantic-ai python-dotenv")
        return 1

    print("🚀 PydanticAI (OpenAI) + HoneyHive: Tools Example")
    print("=" * 55)

    tracer = HoneyHiveTracer.init(
        api_key=hh_api_key,
        project=hh_project,
        session_name=Path(__file__).stem,
        source="pydantic_ai_openai_tools",
    )
    print("✓ HoneyHive tracer initialized")

    # IMPORTANT: HoneyHive may not be the global TracerProvider, so we explicitly
    # wire PydanticAI instrumentation to HoneyHive's provider.
    Agent.instrument_all(InstrumentationSettings(tracer_provider=tracer.provider))
    print("✓ PydanticAI instrumentation wired to HoneyHive tracer provider")

    agent = Agent(
        "openai:gpt-4o-mini",
        deps_type=str,
        system_prompt=(
            "You're a dice game. Roll the die and see if it matches the user's guess. "
            "If so, tell them they're a winner. Use the player's name in the response."
        ),
    )

    @agent.tool_plain
    def roll_dice() -> str:
        """Roll a six-sided die."""

        return str(random.randint(1, 6))

    @agent.tool
    def get_player_name(ctx: RunContext[str]) -> str:
        """Get the player's name."""

        return ctx.deps

    result = agent.run_sync("My guess is 4", deps="Anne")
    print("\n=== RESULT ===")
    print(result.output)

    print("\n📊 What to look for in HoneyHive:")
    print("   - Agent run span")
    print("   - Tool calls: roll_dice, get_player_name")
    print("   - Model request spans for OpenAI")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

