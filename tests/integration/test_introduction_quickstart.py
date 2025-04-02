import os
from honeyhive.models import components, operations
from honeyhive import HoneyHive


MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
MY_SOURCE = os.getenv("HH_SOURCE")
MY_SESSION_NAME = os.getenv("HH_SESSION")
MY_HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer

# Add this code at the beginning of your AI pipeline code

if __name__ == "__main__":
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        source=MY_SOURCE, # Optional
        session_name=MY_SESSION_NAME, # Optional
        server_url=MY_HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
    )

    current_session_id = tracer.session_id

    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=MY_HONEYHIVE_SERVER_URL
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

    # Assert that at least one event (session start) exists for this session ID
    assert res.object is not None
    assert len(res.object.events) > 0
    assert res.object.events[0].session_id == current_session_id


# Your LLM and vector database calls will now be automatically instrumented
# Run HoneyHiveTracer.init() again to end the current session and start a new one