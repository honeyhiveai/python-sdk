import os
import time
from honeyhive import HoneyHive
from honeyhive.models import components, operations

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer, trace, enrich_span, enrich_session


# Store the tracer instance to access session_id later
tracer = HoneyHiveTracer.init(
    api_key=MY_HONEYHIVE_API_KEY,
    project=MY_HONEYHIVE_PROJECT_NAME,
    server_url=HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
)

current_session_id = tracer.session_id

@trace
def get_relevant_docs(query):
    medical_docs = [
        "Regular exercise reduces diabetes risk by 30%. Daily walking is recommended.",
        "Studies show morning exercises have better impact on blood sugar levels."
    ]
    enrich_span(metrics={"retrieval_relevance": 0.5})
    return medical_docs

@trace
def generate_response(docs, query):
    prompt = f"Question: {query}\nContext: {docs}\nAnswer:"
    response = "This is a test response."
    enrich_span(metrics={"contains_citations": True})
    return response

@trace
def rag_pipeline(query):
    docs = get_relevant_docs(query)
    response = generate_response(docs, query)


    # Add session-level metrics
    enrich_session(metrics={
        "rag_pipeline": {
            "num_retrieved_docs": len(docs),
            "query_length": len(query.split())   
        }
    })

    return docs, response

def main():
    query = "How does exercise affect diabetes?"
    retrieved_docs, generated_response = rag_pipeline(query)
    
    time.sleep(5)

    # Initialize SDK and fetch events
    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=HONEYHIVE_SERVER_URL
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
    print(f"Fetching events for session {current_session_id}...")
    res = sdk.events.get_events(request=req)
    # Assertions
    assert res.object is not None
    # Expecting 4 events: Session Start, rag_pipeline, get_relevant_docs, generate_response
    assert len(res.object.events) >= 4, f"Expected at least 4 events for session {current_session_id}, found {len(res.object.events)}"

    # Check for span-level metrics
    span_metrics_found = {
        'retrieval_relevance': False,
        'contains_citations': False
    }
    for event in res.object.events:
        if event.metrics:
            if 'retrieval_relevance' in event.metrics:
                span_metrics_found['retrieval_relevance'] = True
            if 'contains_citations' in event.metrics:
                 span_metrics_found['contains_citations'] = True

    assert span_metrics_found['retrieval_relevance'], "'retrieval_relevance' metric not found in any event"
    assert span_metrics_found['contains_citations'], "'contains_citations' metric not found in any event"

    # Check for session-level metrics (should be in the first event - Session Start)
    session_event = next((e for e in res.object.events if e.event_type == 'session'), None)
    assert session_event is not None, "Session start event not found"
    assert session_event.metrics is not None, "Metrics not found in session start event"
    assert 'rag_pipeline' in session_event.metrics, "'rag_pipeline' metric not found in session start event"
    assert session_event.metrics['rag_pipeline']['num_retrieved_docs'] == 2
    assert session_event.metrics['rag_pipeline']['query_length'] == 5

if __name__ == "__main__":
    main()