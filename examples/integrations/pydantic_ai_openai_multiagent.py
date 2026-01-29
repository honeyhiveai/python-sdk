#!/usr/bin/env python3
"""
PydanticAI (OpenAI) + HoneyHive Integration Example: Multi-agent delegation

This example demonstrates PydanticAI's "agent delegation" pattern (one agent calls
another agent from inside a tool) while tracing everything in HoneyHive via
OpenTelemetry.

Requirements:
  pip install honeyhive pydantic-ai python-dotenv

Environment Variables (repo root .env):
  HH_API_KEY
  HH_PROJECT
  OPENAI_API_KEY
"""

import os
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

        from pydantic_ai import Agent, RunContext, UsageLimits
        from pydantic_ai.models.instrumented import InstrumentationSettings

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive pydantic-ai python-dotenv")
        return 1

    print("🚀 PydanticAI (OpenAI) + HoneyHive: Multi-agent Delegation")
    print("=" * 60)

    tracer = HoneyHiveTracer.init(
        api_key=hh_api_key,
        project=hh_project,
        session_name=Path(__file__).stem,
        source="pydantic_ai_openai_multiagent",
    )
    print("✓ HoneyHive tracer initialized")

    # IMPORTANT: HoneyHive may not be the global TracerProvider, so we explicitly
    # wire PydanticAI instrumentation to HoneyHive's provider.
    Agent.instrument_all(InstrumentationSettings(tracer_provider=tracer.provider))
    print("✓ PydanticAI instrumentation wired to HoneyHive tracer provider")

    joke_selection_agent = Agent(
        "openai:gpt-4o-mini",
        system_prompt=(
            "Use the `joke_factory` tool to generate some jokes, then choose the best. "
            "You must return just a single joke."
        ),
    )

    joke_generation_agent = Agent(
        "openai:gpt-4o-mini",
        output_type=list[str],
    )

    @joke_selection_agent.tool
    async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
        # Pass ctx.usage so usage is attributed to the parent run.
        r = await joke_generation_agent.run(
            f"Please generate {count} short jokes.",
            usage=ctx.usage,
        )
        return r.output

    result = joke_selection_agent.run_sync(
        "Tell me a joke.",
        usage_limits=UsageLimits(request_limit=5, total_tokens_limit=5000),
    )

    print("\n=== RESULT ===")
    print(result.output)

    print("\n📊 What to look for in HoneyHive:")
    print("   - Parent agent run span")
    print("   - Tool call: joke_factory")
    print("   - Delegate agent run span nested under the tool call")
    print("   - Usage aggregated via ctx.usage")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

