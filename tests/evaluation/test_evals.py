from honeyhive import evaluate
import time
import openai

client = openai.OpenAI()

def evaluator(*args, **kwargs):
    time.sleep(1)
    return True

def my_pipeline(*args, **kwargs):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Tell me a joke."}],
        max_tokens=50
    )
    content = resp.choices[0].message.content
    print(content)
    return content

dataset = [{"parameter_1": i, "parameter_2": i} for i in range(0, 10)]

result = evaluate(
    name = 'Sample Experiment',
    function=my_pipeline, 
    dataset=dataset,
    evaluators=[evaluator]
)

print(result)
