import os
import time
from honeyhive import HoneyHive
from honeyhive.models import components, operations

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer, trace, enrich_span

if __name__ == "__main__":

    # Store the tracer instance to access session_id later
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        server_url=HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
    )

    current_session_id = tracer.session_id

    prompt_template = {
        "template": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Write a short poem about programming."}
        ],
        "prompt": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Write a short poem about programming."},
        ]
    }

    # ...

    @trace
    def my_function(input, prompt_template):
        # ...

        enrich_span(config={
            "template": prompt_template["template"],
            "prompt": prompt_template["prompt"],
            "hyperparams": {
                "temperature": 0.5,
                "max_tokens": 100,
                "top_p": 0.9,
                "top_k": 50,
            }
        })

        # ...
        response = "This is a mock response."
        return response

    # ...
    result = my_function("This is a mock input", prompt_template)

    # Allow time for events to be processed
    time.sleep(5)

    # Initialize SDK and fetch events
    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=HONEYHIVE_SERVER_URL
    )

    req = operations.GetEventsRequestBody(
        project=MY_HONEYHIVE_PROJECT_NAME,
        filters=[
            components.EventFilter(
                field="session_id",
                value=current_session_id,  # Use the session_id from the tracer
                operator=components.Operator.IS,
            )
        ],
    )

    res = sdk.events.get_events(request=req)
    # Assertions
    assert res.object is not None
    # Expecting at least 2 events: Session Start, my_function trace
    assert len(res.object.events) >= 2, f"Expected at least 2 events for session {current_session_id}, found {len(res.object.events)}"

    # Find the event for the 'my_function' trace
    my_function_event = next((e for e in res.object.events if e.event_name == 'my_function'), None)
    assert my_function_event is not None, "'my_function' event not found"
    assert my_function_event.config is not None, "Config not found in 'my_function' event"

    # Verify the config contents
    assert my_function_event.config.get("template") == prompt_template["template"]
    assert my_function_event.config.get("prompt") == prompt_template["prompt"]
    assert my_function_event.config.get("hyperparams") == {
        "temperature": 0.5,
        "max_tokens": 100,
        "top_p": 0.9,
        "top_k": 50,
    }