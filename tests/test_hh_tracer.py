import openai
import os
import honeyhive
import time
import uuid
from honeyhive.models import components, operations
from honeyhive.tracer import HoneyHiveTracer
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader

session_name = f"HoneyHive Tracer Test {str(uuid.uuid4())}"
HoneyHiveTracer.init(
    server_url=os.environ["HH_API_URL"],
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    source="HoneyHive Tracer Test",
    session_name=session_name,
)
sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)

def run_tracer():
    openai.api_key = os.environ["OPENAI_API_KEY"]

    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["http://paulgraham.com/worked.html"]
    )

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    response = query_engine.query("What did the author do growing up?")


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

    session_id = res.object.events[0].session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=session_id,
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) > 1

    # Run it a second time in a new session
    HoneyHiveTracer.init(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="HoneyHive Tracer Test",
        session_name=session_name,
    )
    run_tracer()

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
    assert len(res.object.events) == 2

    new_session_id = None
    for event in res.object.events:
      if event.session_id is not None and event.session_id != session_id:
        new_session_id = event.session_id
    assert new_session_id is not None

    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=session_id,
                operator=components.Operator.IS,
            ),
            components.EventFilter(
                field="event_name",
                value="openai.chat",
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) == 1

    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=new_session_id,
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) > 1

def test_tracer_metadata_update():
    run_tracer()

    HoneyHiveTracer.set_metadata({ "test": "value" })

    session_id = HoneyHiveTracer.session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=session_id,
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

    logged_event = res.object.events[0]
    assert logged_event.metadata == { "test": "value" }

def test_tracer_feedback_update():
    run_tracer()

    HoneyHiveTracer.set_feedback({ "comment": "test feedback" })

    session_id = HoneyHiveTracer.session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=session_id,
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

    logged_event = res.object.events[0]
    assert logged_event.feedback == { "comment": "test feedback" }

def test_tracer_evaluator_update():
    run_tracer()

    HoneyHiveTracer.set_evaluator({ "tps": 1.78 })

    session_id = HoneyHiveTracer.session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=session_id,
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

    logged_event = res.object.events[0]
    assert logged_event.metrics == { "tps": 1.78 }

def test_distributed_tracing():
    pre_existing_session_id = "fb0a4180-c998-45a6-ba0a-b19bf46e966b"
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=pre_existing_session_id,
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) > 1
    prev_event_count = len(res.object.events)

    HoneyHiveTracer.init_from_session_id(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        session_id=pre_existing_session_id,
    )
    run_tracer()

    time.sleep(20)
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=pre_existing_session_id,
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) > prev_event_count
