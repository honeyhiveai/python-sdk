import http
from honeyhive import HoneyHiveTracer, trace, evaluate, enrich_session, enrich_span, evaluator
import openai
import httpx
import requests
import time
import logging
import os

oai_client = openai.OpenAI()

hh = HoneyHiveTracer(
    api_key='MGc0cnl6MWh3MDk5OXhndGgycm92Y3A=',
    project='agi',
    server_url='https://api.staging.honeyhive.ai',
    session_name='Mar 26',
    source='test',
)

model = 'gpt-4o-mini'
iterations = 1

@evaluator(
    # repeat=3, aggregate='mean', checker='value in target', asserts=True, target=1.0
)
def check_answer(output, input, ground_truth):
    print('repeat')
    # Ask OpenAI client to compare the output with ground truth
    response = oai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an evaluator. Compare the output with the ground truth and return True if they match semantically, False otherwise."},
            {"role": "user", "content": f"Output: {output}\nGround Truth: {ground_truth}\nDo these match semantically? Answer with True or False only."}
        ],
        # max_completion_tokens=10
    )
    
    result = response.choices[0].message.content.strip().lower() == "true"
    return result


def pipeline(input, ground_truth):
    prompt = f'Answer this question: {input["query"]}'
    for i in range(iterations):
        print('i', i)
        response = oai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    
    enrich_session(metadata={"test": "test"*5})

    return response.choices[0].message.content, ground_truth["response"]


dataset = [
    {
        "inputs": {
            "query": "How does exercise affect diabetes?",
        },
        "ground_truths": {
            "response": "Regular exercise reduces diabetes risk by 30%. Daily walking is recommended.",
        }
    },
    {
        "inputs": {
            "query": "What is the capital of France?",
        },
        "ground_truths": {
            "response": "Paris",
        }
    },
    {
        "inputs": {
            "query": "What is the capital of France?",
        },
        "ground_truths": {
            "response": "Paris",
        }
    }
]

if __name__ == "__main__":
    evaluate(
        function = pipeline,
        dataset = dataset * 3,
        api_key = 'MGc0cnl6MWh3MDk5OXhndGgycm92Y3A=',
        project = 'agi',
        evaluators = [check_answer],
        server_url = 'https://api.staging.honeyhive.ai'
    )
