import os

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")

from honeyhive import HoneyHiveTracer, trace, enrich_span, enrich_session


HoneyHiveTracer.init(
api_key=MY_HONEYHIVE_API_KEY,
project=MY_HONEYHIVE_PROJECT_NAME,
)

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

if __name__ == "__main__":
    main()