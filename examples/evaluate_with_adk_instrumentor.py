"""
Example: Running evaluations with Google ADK Instrumentor

This example demonstrates how to use the `instrumentors` argument in the
`evaluate()` function to automatically trace Google ADK agent calls.

The key concept is that each datapoint in the evaluation gets its own
tracer and instrumentor instance, ensuring traces are routed correctly
to the right session.

Requirements:
    pip install google-adk openinference-instrumentation-google-adk

Environment variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    GOOGLE_API_KEY: Your Google API key for Gemini
"""

import asyncio
import datetime
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from honeyhive.experiments import evaluate

load_dotenv()


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}."),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)


async def run_agent(query: str) -> str:
    """Run the ADK agent with a query and return the response."""
    session_service = InMemorySessionService()
    app_name = "eval_demo"
    user_id = "eval_user"
    session_id = f"{app_name}_{user_id}_{datetime.datetime.now().timestamp()}"

    runner = Runner(
        agent=root_agent, app_name=app_name, session_service=session_service
    )

    try:
        await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
    except Exception:
        pass

    user_content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response = ""

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    return final_response


dataset = [
    {
        "inputs": {"query": "What is the weather in New York?"},
        "ground_truth": {"contains": "sunny", "city": "New York"},
    },
    {
        "inputs": {"query": "What time is it in New York?"},
        "ground_truth": {"contains": "current time", "city": "New York"},
    },
    {
        "inputs": {"query": "What is the weather in Los Angeles?"},
        "ground_truth": {"contains": "not available", "city": "Los Angeles"},
    },
]


def evaluation_function(datapoint):
    """
    Evaluation function that runs the ADK agent for each datapoint.

    The instrumentors passed to evaluate() will automatically trace
    all ADK agent calls within this function.
    """
    query = datapoint.get("inputs", {}).get("query", "")
    response = asyncio.run(run_agent(query))
    return {"response": response}


def check_response_contains(outputs, inputs, ground_truth):
    """Evaluator that checks if the response contains expected content."""
    response = outputs.get("response", "").lower()
    expected = ground_truth.get("contains", "").lower()
    return {"contains_expected": 1 if expected in response else 0}


if __name__ == "__main__":
    result = evaluate(
        function=evaluation_function,
        dataset=dataset,
        evaluators=[check_response_contains],
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        name=f"adk-eval-{datetime.datetime.now().isoformat()}",
        instrumentors=[lambda: GoogleADKInstrumentor()],
        verbose=True,
    )

    print(f"\nEvaluation complete!")
    print(f"Success: {result.success}")
    print(f"Passed: {len(result.passed)}")
    print(f"Failed: {len(result.failed)}")
