from honeyhive import evaluate, config, evaluator
from honeyhive.app.ai_app import get_ai_response

# from realign import categor
# ical_mean

from openai import OpenAI

import json

client = OpenAI()

def eval_profanity(output):
    
    prompt = config.profanity_eval.render(output=output)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result['contains_profanity']

results = evaluate(
    function=get_ai_response,
    dataset=[
        {"user_input": "hi"},
        {"user_input": "hello"},
        {"user_input": "how are you?"}
    ] * 5,
    evaluators=[eval_profanity]
)

print(results.data)

# assert categorical_mean(results.data) > 0.5
