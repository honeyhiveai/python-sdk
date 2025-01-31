import openai
import os
import honeyhive
import time
import uuid
from honeyhive.models import components, operations
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.custom import trace
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader

session_name = f"HoneyHive Tracer Test {str(uuid.uuid4())}"
hhtracer = HoneyHiveTracer.init(
    server_url=os.environ["HH_API_URL"],
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    source="HoneyHive Tracer Test",
    session_name=session_name,
)
sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)


@trace(config={"thing": "stuff"}, metadata={"meta_thing": 42})
def run_tracer_enriched(input, prompt_template):
    openai.api_key = os.environ["OPENAI_API_KEY"]

    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["http://paulgraham.com/worked.html"]
    )

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt_template["prompt"][0]["content"])
    return response


def run_tracer():
    openai.api_key = os.environ["OPENAI_API_KEY"]

    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["http://paulgraham.com/worked.html"]
    )

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    response = query_engine.query("What did the author do growing up?")
    return response

def test_tracer():
    run_tracer_enriched(
        {"a": 3, "b": [1, 2, 3], "c": {"d": [4, 5, 6]}},
        {
            "template": [
                {"role": "user", "content": "What did {{subject}} do {{participial}}?"}
            ],
            "prompt": [
                {"role": "user", "content": "What did the author do growing up?"}
            ],
        },
    )

    # Get session
    time.sleep(10)
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
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
        project=os.environ["HH_PROJECT"],
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

    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=[
            components.EventFilter(
                field="event_name",
                value="run_tracer_enriched",
                operator=components.Operator.IS,
            ),
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
    assert len(res.object.events) == 1
    event = res.object.events[0]
    assert event.inputs is not None
    assert "_params_" in event.inputs
    assert event.outputs is not None
    assert "result" in event.outputs
    assert event.config.get("thing") == "stuff"
    assert event.metadata.get("meta_thing") == 42

    # Run it a second time in a new session
    HoneyHiveTracer.init(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="HoneyHive Tracer Test",
        session_name=session_name,
    )
    run_tracer()

    time.sleep(10)

    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
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
        project=os.environ["HH_PROJECT"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=session_id,
                operator=components.Operator.IS,
            ),
            components.EventFilter(
                field="event_name",
                value="OpenAI.task",
                operator=components.Operator.IS,
            ),
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) == 1

    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
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
    time.sleep(10)

    hhtracer.enrich_session(metadata={"test": "value"})
    time.sleep(10)

    session_id = hhtracer.session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
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
    assert "test" in logged_event.metadata
    assert logged_event.metadata["test"] == "value"

def test_tracer_feedback_update():
    run_tracer()
    time.sleep(10)

    hhtracer.enrich_session(feedback={"comment": "test feedback"})
    time.sleep(10)

    session_id = hhtracer.session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
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
    assert logged_event.feedback == {"comment": "test feedback"}


def test_tracer_evaluator_update():
    run_tracer()
    time.sleep(10)

    hhtracer.enrich_session(metrics={"tps": 1.78})
    time.sleep(10)

    session_id = hhtracer.session_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
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
    assert logged_event.metrics == {"tps": 1.78}


def test_distributed_tracing():
    pre_existing_session_id = "fb0a4180-c998-45a6-ba0a-b19bf46e966b"
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=pre_existing_session_id,
                operator=components.Operator.IS,
            ),
        ],
        limit=7500,
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) > 1
    prev_event_count = len(res.object.events)

    hhtracer.init_from_session_id(
        server_url=os.environ["HH_API_URL"],
        api_key=os.environ["HH_API_KEY"],
        session_id=pre_existing_session_id,
    )
    run_tracer()

    time.sleep(15)
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=[
            components.EventFilter(
                field="session_id",
                value=pre_existing_session_id,
                operator=components.Operator.IS,
            ),
        ],
        limit=7500,
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) > prev_event_count
