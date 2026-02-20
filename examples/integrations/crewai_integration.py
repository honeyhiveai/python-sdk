"""
HoneyHive + CrewAI integration example.

Based on CrewAI docs (https://docs.crewai.com) with HoneyHive tracing on top.

Demonstrates two patterns:
1) Sequential crew - researcher + writer (from quickstart)
2) Hierarchical crew - manager delegates to tool-equipped specialists

Requirements:
    pip install honeyhive crewai openinference-instrumentation-crewai openinference-instrumentation-litellm

Environment variables:
    HH_API_KEY, HH_PROJECT, OPENAI_API_KEY (or LITELLM provider keys)
"""

import os

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor

from honeyhive import HoneyHiveTracer

# --- HoneyHive setup (add these 3 lines to any CrewAI app) ---

tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="crewai-example",
)

CrewAIInstrumentor().instrument(tracer_provider=tracer.provider)
LiteLLMInstrumentor().instrument(tracer_provider=tracer.provider)


# --- Pattern 1: Sequential crew (CrewAI quickstart) ---
# https://docs.crewai.com/quickstart

researcher = Agent(
    role="{topic} Senior Data Researcher",
    goal="Uncover cutting-edge developments in {topic}",
    backstory=(
        "You're a seasoned researcher with a knack for uncovering the latest "
        "developments in {topic}. Known for finding the most relevant information "
        "and presenting it clearly and concisely."
    ),
    llm="openai/gpt-4o-mini",
    verbose=False,
)

reporting_analyst = Agent(
    role="{topic} Reporting Analyst",
    goal="Create detailed reports based on {topic} data analysis and research findings",
    backstory=(
        "You're a meticulous analyst with a keen eye for detail. You turn complex "
        "data into clear and concise reports that are easy to understand and act on."
    ),
    llm="openai/gpt-4o-mini",
    verbose=False,
)

research_task = Task(
    description=(
        "Conduct a thorough research about {topic}. "
        "Make sure you find any interesting and relevant information given "
        "the current year is 2026."
    ),
    expected_output="A list with 5 bullet points of the most relevant information about {topic}.",
    agent=researcher,
)

reporting_task = Task(
    description=(
        "Review the context you got and expand each topic into a full section for a report. "
        "Make sure the report is detailed and contains any and all relevant information."
    ),
    expected_output="A fully fledged report with the main topics, each with a full section of information.",
    agent=reporting_analyst,
    context=[research_task],
)

sequential_crew = Crew(
    agents=[researcher, reporting_analyst],
    tasks=[research_task, reporting_task],
    process=Process.sequential,
    verbose=False,
)

print("--- Pattern 1: Sequential crew ---")
result = sequential_crew.kickoff(inputs={"topic": "AI Agents"})
print(result)


# --- Pattern 2: Hierarchical crew with tools ---
# https://docs.crewai.com/learn/hierarchical-process
# https://docs.crewai.com/learn/create-custom-tools


@tool("Calculator")
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression like '17 * 3 + 5'."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression).issubset(allowed):
        return "Only basic arithmetic symbols are allowed."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return "Invalid arithmetic expression."


@tool("PolicyLookup")
def policy_lookup(topic: str) -> str:
    """Look up internal company policy by topic. Available topics: soc2, pii, retention."""
    policies = {
        "soc2": "SOC 2 covers security, availability, processing integrity, confidentiality, and privacy.",
        "pii": "PII must be redacted before sharing with external systems. Retain per data policy.",
        "retention": "Default data retention is 30 days unless legal requirements require longer.",
    }
    return policies.get(
        topic.strip().lower(), "No policy found. Try: soc2, pii, retention."
    )


math_expert = Agent(
    role="Math Expert",
    goal="Solve arithmetic problems accurately using the Calculator tool",
    backstory="You are a mathematician. Always use the Calculator tool for calculations.",
    tools=[calculator],
    llm="openai/gpt-4o-mini",
    verbose=False,
)

compliance_expert = Agent(
    role="Compliance Expert",
    goal="Answer policy and compliance questions using the PolicyLookup tool",
    backstory="You are a compliance officer. Always use PolicyLookup for policy questions.",
    tools=[policy_lookup],
    llm="openai/gpt-4o-mini",
    verbose=False,
)

support_task = Task(
    description=(
        "Answer these two questions:\n"
        "1. What is 24 * 7 + 15?\n"
        "2. What does our data retention policy say?"
    ),
    expected_output="Clear answers to both questions, labeled 1 and 2.",
)

hierarchical_crew = Crew(
    agents=[math_expert, compliance_expert],
    tasks=[support_task],
    process=Process.hierarchical,
    manager_llm="openai/gpt-4o-mini",
    verbose=False,
)

print("\n--- Pattern 2: Hierarchical crew with tools ---")
print(hierarchical_crew.kickoff())
