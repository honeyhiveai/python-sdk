from honeyhive import evaluate, config, evaluator
from honeyhive.app.ai_app import get_ai_response

from openai import OpenAI

import json

client = OpenAI()

@evaluator(
    target=0.5,
    range=[0, 1],
)
def eval_profanity(output, input, ground_truth):
    
    prompt = config.profanity_eval.render(output=output)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result['contains_profanity']

@evaluator
def eval_hate(output):
    return 0

results = evaluate(
    function=get_ai_response,
    dataset=[
        {"inputs": {"user_input": "hi"}},
        {"inputs": {"user_input": "hello"}},
        {"inputs": {"user_input": "how are you?"}}
    ] * 3,
    evaluators=[eval_profanity]
)

print(results.data)

# assert categorical_mean(results.data) > 0.5
# inputs x evaluators
