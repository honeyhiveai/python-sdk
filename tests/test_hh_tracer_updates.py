import openai
import os
import honeyhive
import time
import uuid
from honeyhive.models import components, operations
from honeyhive.tracer import HoneyHiveTracer
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader


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

def test_tracer_metadata_update():
    session_name = f"HoneyHive Tracer Test {str(uuid.uuid4())}"
    HoneyHiveTracer.init(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="HoneyHive Tracer Test",
        session_name=session_name,
    )

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
    session_name = f"HoneyHive Tracer Test {str(uuid.uuid4())}"
    HoneyHiveTracer.init(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="HoneyHive Tracer Test",
        session_name=session_name,
    )


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
    session_name = f"HoneyHive Tracer Test {str(uuid.uuid4())}"
    HoneyHiveTracer.init(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="HoneyHive Tracer Test",
        session_name=session_name,
    )

    run_tracer()

    HoneyHiveTracer.set_metric({ "tps": 1.78 })

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
