import os
import time
from honeyhive import HoneyHive
from honeyhive.models import components, operations

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import evaluate, evaluator
from honeyhive import trace, enrich_span

def retrieval_relevance_evaluator(query, docs):
    # code here
    avg_relevance = 0.5
    return avg_relevance

@evaluator()
def consistency_evaluator(outputs, inputs, ground_truths):
    # code here
    consistency_score = 0.66
    return consistency_score


@trace
def get_relevant_docs(query):
    retrieved_docs = [
        "Regular exercise reduces diabetes risk by 30%. Daily walking is recommended.",
        "Studies show morning exercises have better impact on blood sugar levels."
    ]
    retrieval_relevance = retrieval_relevance_evaluator(query, retrieved_docs)
    enrich_span(metrics={"retrieval_relevance": retrieval_relevance})
    return retrieved_docs

def generate_response(docs, query):
    prompt = f"Question: {query}\nContext: {docs}\nAnswer:"
    response = "This is a test response"
    return response

def rag_pipeline(inputs, ground_truths):
    query = inputs["query"]
    docs = get_relevant_docs(query)
    response = generate_response(docs, query)

    return response

dataset = [
    {
        "inputs": {
            "query": "How does exercise affect diabetes?",
        },
        "ground_truths": {
            "response": "Regular exercise reduces diabetes risk by 30%. Daily walking is recommended.",
        }
    },
]


if __name__ == "__main__":
    # Run experiment
    evaluation_results = evaluate(
        function = rag_pipeline,               # Function to be evaluated
        api_key = MY_HONEYHIVE_API_KEY,
        project = MY_HONEYHIVE_PROJECT_NAME,
        name = 'Multi Step Evals',
        dataset = dataset,
        evaluators=[consistency_evaluator],                 # to compute client-side metrics on each run
        server_url=HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
    )
    time.sleep(5)
    session_ids = evaluation_results.session_ids
    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=HONEYHIVE_SERVER_URL
    )

    session_id = session_ids[0]
    req = operations.GetEventsRequestBody(
        project=MY_HONEYHIVE_PROJECT_NAME,
            filters=[
                components.EventFilter(
                    field="session_id",
                    value=session_id,
                    operator=components.Operator.IS,
                )
            ],
        )
    res = sdk.events.get_events(request=req)
    assert len(res.object.events) >= 3, f"Expected at least 3 events for session {session_id}, found {len(res.object.events)}"

    # Check if at least one event has the 'retrieval_relevance' metric from enrich_span
    assert any('retrieval_relevance' in event.metrics for event in res.object.events if event.metrics), \
        f"No event found with 'retrieval_relevance' metric for session {session_id}"

    # Check if at least one event has the 'consistency_evaluator' metric from the evaluator
    assert any('consistency_evaluator' in event.metrics for event in res.object.events if event.metrics), \
        f"No event found with 'consistency_evaluator' metric for session {session_id}"