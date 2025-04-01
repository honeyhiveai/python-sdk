import os

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")

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
    evaluate(
        function = rag_pipeline,               # Function to be evaluated
        hh_api_key = MY_HONEYHIVE_API_KEY,
        hh_project = MY_HONEYHIVE_PROJECT_NAME,
        name = 'Multi Step Evals',
        dataset = dataset,
        evaluators=[consistency_evaluator],                 # to compute client-side metrics on each run
    )