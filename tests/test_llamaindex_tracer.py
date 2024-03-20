import os
import honeyhive
from honeyhive.utils.llamaindex_tracer import HoneyHiveLlamaIndexTracer
from llama_index.core import Settings, VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.callbacks import CallbackManager
import openai


def run_tracer(source, metadata):
    tracer = HoneyHiveLlamaIndexTracer(
        project=os.environ["HH_PROJECT"],
        name="Paul Graham Q&A",
        source=source,
        api_key=os.environ["HH_API_KEY"],
        metadata=metadata,
    )

    openai.api_key = os.environ["OPENAI_API_KEY"]

    Settings.callback_manager = CallbackManager([tracer])

    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["http://paulgraham.com/worked.html"]
    )

    # Pass the service_context to the index that you will query1
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    response = query_engine.query("What did the author do growing up?")
    return tracer


def test_tracer():
    tracer = run_tracer("sdk_li_test", None)
    session_id = tracer.session_id
    assert session_id is not None
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None


def test_tracer_eval():
    # Do initial eval run
    tracer = run_tracer("evaluation", {"dataset_name": os.environ["HH_DATASET"]})
    session_id = tracer.session_id
    eval_info = tracer.eval_info
    assert session_id is not None
    assert eval_info is not None
    assert "run_id" in eval_info
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None

    # Append to eval run
    tracer = run_tracer("evaluation", {"run_id": eval_info["run_id"]})
    session_id = tracer.session_id
    eval_info = tracer.eval_info
    assert session_id is not None
    assert eval_info is not None
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
