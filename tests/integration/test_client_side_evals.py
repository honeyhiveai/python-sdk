import os
import time
from honeyhive import HoneyHiveTracer, enrich_session, HoneyHive
from honeyhive.models import components, operations

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
MY_HONEYHIVE_API_URL = os.getenv("HH_API_URL")

if __name__ == "__main__":
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
    )

    current_session_id = tracer.session_id
    # ...

    enrich_session(metrics={
    "json_validated": True,
    "num_actions": 10,
    # any other custom fields and values as you need
    "step_evals": [
        {
        "invalid_grammar": False,
        "unable_to_locate_UI": True
        }
    ],
    })

    time.sleep(5)
    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=MY_HONEYHIVE_API_URL
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
    assert res.object.events[0].metrics.get("json_validated") == True
    assert res.object.events[0].metrics.get("num_actions") == 10
    assert res.object.events[0].metrics.get("step_evals")[0].get("invalid_grammar") == False
    assert res.object.events[0].metrics.get("step_evals")[0].get("unable_to_locate_UI") == True
