import os
import honeyhive
from honeyhive.utils.llamaindex_tracer import HoneyHiveLlamaIndexTracer
from llama_index.core import Settings, VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.callbacks import CallbackManager
import openai


def run_tracer():
    tracer = HoneyHiveLlamaIndexTracer(
        project=os.environ["HH_PROJECT"],
        name="Paul Graham Q&A",
        source="sdk_li_test",
        api_key=os.environ["HH_API_KEY"],
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
    return tracer.session_id


def test_tracer():
    session_id = run_tracer()
    assert session_id is not None
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
