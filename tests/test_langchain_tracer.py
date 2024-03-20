import os
import honeyhive
from honeyhive.utils.langchain_tracer import HoneyHiveLangChainTracer
from langchain import LLMMathChain, OpenAI, SerpAPIWrapper, Wikipedia
from langchain.agents import Tool, initialize_agent
from langchain.tools import StructuredTool
from langchain.agents.react.base import DocstoreExplorer
from langchain.callbacks import StdOutCallbackHandler


def run_tracer(source, metadata):
    honeyhive_tracer = HoneyHiveLangChainTracer(
        project=os.environ["HH_PROJECT"],
        name="SERP Q&A",
        source=source,
        api_key=os.environ["HH_API_KEY"],
        metadata=metadata,
    )

    # Initialise the OpenAI LLM and required callables for our tools
    llm = OpenAI(temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"])
    search = SerpAPIWrapper(serpapi_api_key=os.environ["SERP_API_KEY"])
    llm_math_chain = LLMMathChain.from_llm(llm=llm)
    docstore = DocstoreExplorer(Wikipedia())

    # Define the tools to be fed to the agent
    tools = [
        Tool(
            name="Google",
            func=search.run,
            description="Useful for when you need to answer questions about current events. You should ask targeted questions.",
        ),
        Tool(
            name="Wikipedia",
            func=docstore.search,
            description="Useful for when you need factual information. Ask search terms for Wikipedia",
        ),
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="Useful for when you need to answer questions about math.",
        ),
    ]

    # Initialise the agent with HoneyHive callback handler
    agent = initialize_agent(tools=tools, llm=llm)
    agent(
        "Which city is closest to London as the crow flies, Berlin or Munich?",
        callbacks=[honeyhive_tracer],
    )
    return honeyhive_tracer


def test_tracer():
    tracer = run_tracer("sdk_lc_test", None)
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
