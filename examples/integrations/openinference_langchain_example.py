#!/usr/bin/env python3
"""
LangChain + HoneyHive integration example (OpenInference).

Demonstrates the two most common LangChain 1.x patterns traced end-to-end
via the OpenInference instrumentor:

  1) Single agent with tools
  2) Multi-agent with subagents (agent-as-tool)

The same ``openinference-instrumentation-langchain`` package also traces
LangGraph ``StateGraph`` workflows; see ``examples/integrations/langgraph_integration.py``.

Install:
    pip install honeyhive[openinference-langchain] langchain-openai

Run:
    python examples/integrations/openinference_langchain_example.py

Environment:
    HH_API_KEY
    OPENAI_API_KEY
"""

from __future__ import annotations

import os
import sys

from langchain.agents import create_agent
from langchain.tools import tool
from openinference.instrumentation.langchain import LangChainInstrumentor

from honeyhive import HoneyHiveTracer


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    return str(eval(expression, {"__builtins__": {}}, {}))


@tool
def policy_lookup(topic: str) -> str:
    """Look up company policy on a topic."""
    policies = {
        "soc2": "SOC 2 covers security, availability, processing integrity, confidentiality, and privacy.",
        "retention": "Default retention is 30 days unless compliance requires longer.",
    }
    return policies.get(topic.lower(), "No policy found.")


def main() -> None:
    """Run LangChain single-agent and multi-agent examples with HoneyHive tracing."""
    if not os.getenv("HH_API_KEY"):
        print("Set HH_API_KEY to your HoneyHive API key.", file=sys.stderr)
        raise SystemExit(1)
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY to your OpenAI API key.", file=sys.stderr)
        raise SystemExit(1)
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="openinference_langchain_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    instrumentor = LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        # --- Pattern 1: Single agent with tools ---
        agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[calculator, policy_lookup],
            system_prompt="You are a support assistant. Use tools when needed.",
        )

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "What is 17 * 3 + 5? Also summarize our SOC2 policy.",
                    }
                ]
            }
        )
        print(result["messages"][-1].content)

        # --- Pattern 2: Multi-agent with subagents ---
        math_agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[calculator],
            system_prompt="You are a math specialist. Use calculator for all arithmetic.",
        )

        policy_agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[policy_lookup],
            system_prompt="You are a compliance specialist. Use policy_lookup for questions.",
        )

        @tool("math_expert", description="Solve math and arithmetic problems")
        def call_math_agent(query: str) -> str:
            inner = math_agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )
            return inner["messages"][-1].content

        @tool("policy_expert", description="Answer questions about company policies")
        def call_policy_agent(query: str) -> str:
            inner = policy_agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )
            return inner["messages"][-1].content

        supervisor = create_agent(
            model="openai:gpt-4o-mini",
            tools=[call_math_agent, call_policy_agent],
            system_prompt="You coordinate specialist agents. Delegate tasks to the right expert.",
        )

        result = supervisor.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "What is 24 * 7? And what's our retention policy?",
                    }
                ]
            }
        )
        print(result["messages"][-1].content)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
