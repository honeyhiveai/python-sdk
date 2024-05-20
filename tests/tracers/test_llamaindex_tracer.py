import os
import honeyhive
from honeyhive.utils.llamaindex_tracer import HoneyHiveLlamaIndexTracer
from llama_index.core.callbacks.schema import CBEventType
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.core.callbacks import CallbackManager
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.readers.web import SimpleWebPageReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.postprocessor.cohere_rerank import CohereRerank
import openai


def run_tracer(source, metadata):
    tracer = HoneyHiveLlamaIndexTracer(
        project=os.environ["HH_PROJECT"],
        name="Paul Graham Q&A",
        source=source,
        api_key=os.environ["HH_API_KEY"],
        metadata=metadata,
        base_url=os.environ["HH_API_URL"],
    )

    openai.api_key = os.environ["OPENAI_API_KEY"]

    Settings.callback_manager = CallbackManager([tracer])

    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["http://paulgraham.com/worked.html"]
    )

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    response = query_engine.query("What did the author do growing up?")
    return tracer


def run_tracer_complex():
    blacklist = [
        CBEventType.CHUNKING,
        CBEventType.NODE_PARSING,
        CBEventType.LLM,
        CBEventType.QUERY,
        CBEventType.SYNTHESIZE,
        CBEventType.TREE,
        CBEventType.SUB_QUESTION,
        CBEventType.TEMPLATING,
        CBEventType.FUNCTION_CALL,
        CBEventType.RERANKING,
        CBEventType.EXCEPTION,
        CBEventType.AGENT_STEP,
    ]
    tracer = HoneyHiveLlamaIndexTracer(
        project=os.environ["HH_PROJECT"],
        name="Complex Trace Example",
        source="sdk_li_test",
        api_key=os.environ["HH_API_KEY"],
        event_types_to_ignore=blacklist,
        base_url=os.environ["HH_API_URL"],
    )

    Settings.callback_manager = CallbackManager([tracer])
    documents = SimpleDirectoryReader("./tests/data/10k/").load_data()

    embed_model = OpenAIEmbedding()
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )

    # also baseline splitter
    base_splitter = SentenceSplitter(chunk_size=512)

    nodes = splitter.get_nodes_from_documents(documents)

    vector_store = MilvusVectorStore(
        dim=1536,
        overwrite=True,
        output_fields=[],
        uri="http://host.docker.internal:19530",
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)

    api_key = os.environ["COHERE_API_KEY"]
    cohere_rerank = CohereRerank(api_key=api_key, top_n=2)
    query_engine = index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=[cohere_rerank],
    )
    response = query_engine.query("What company does the document refer to mainly?")

    return tracer


def test_tracer():
    tracer = run_tracer("sdk_li_test", None)
    session_id = tracer.session_id
    assert session_id is not None
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    tracer.set_metric("cost", 42, (0, 100))


def _test_tracer_complex():
    tracer = run_tracer_complex()
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
