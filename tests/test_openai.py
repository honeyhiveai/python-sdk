import openai
from openai import OpenAI
import os
import honeyhive
import time
import uuid
from honeyhive.models import components, operations
from honeyhive.tracer import HoneyHiveTracer

session_name = f"HoneyHive Tracer Test {str(uuid.uuid4())}"
HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    source="OpenAI Tracer Test",
    session_name=session_name,
)

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)
openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def run_tracer():
    chat_completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Say hello."},
        ]
    )
    print(chat_completion.choices[0].message.content)

def test_tracer():
    run_tracer()

    # Get session
    time.sleep(5)
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="event_name",
                value=session_name,
                operator=components.Operator.IS,
            ),
            components.EventFilter(
                field="event_type",
                value="session",
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) == 1

if __name__ == "__main__":
    test_tracer()
