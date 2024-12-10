from honeyhive import evaluate, config, evaluator
from honeyhive.app.ai_app import get_ai_response

from openai import OpenAI

import json

client = OpenAI()

@evaluator(repeat=5, aggregate='sum(values)/len(values)')
def eval_sentiment(output):
    
    prompt = config.sentiment_score.render(output=output)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    
    return result['sentiment_score']


# evaluate(
#     function=get_ai_response,
#     dataset=[
#         {"user_input": "I feel great"},
#         {"user_input": "I feel okay"},
#         {"user_input": "I feel terrible"}
#     ],
#     evaluators=[eval_sentiment]
# )

evaluate(
    function=get_ai_response,
    dataset=config.datasets.sentiment,
    evaluators=[eval_sentiment]
)