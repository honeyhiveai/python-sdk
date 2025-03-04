from honeyhive import evaluate, HoneyHiveTracer, trace
import time
import openai

client = openai.OpenAI()



# result = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[{"role": "user", "content": "Tell me a joke."}],
#     max_tokens=50
# )

# print(result.choices[0].message.content)

# def evaluator(*args, **kwargs):
#     time.sleep(1)
#     return True

@trace
def my_pipeline(inputs, ground_truth=None):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Tell me a joke."}],
        max_tokens=50
    )
    content = resp.choices[0].message.content
    return content

def main(inputs):
    return my_pipeline(inputs)

def evaluator(outputs):
    time.sleep(1)
    return True

dataset = [{"parameter_1": i, "parameter_2": i} for i in range(0, 1)]

if __name__ == "__main__":
    # hh = HoneyHiveTracer(
    #     project="agi",
    #     session_name="test_evals",
    #     source="dev",
    #     # server_url="https://nationwide.api.honeyhive.ai",
    #     server_url="http://localhost:3000",
    #     # verbose=True
    # )
    result = evaluate(
        name = 'Sample Experiment',
        hh_project="e2e",
        function=main, 
        dataset=dataset,
        evaluators=[evaluator],
        verbose=True,
        run_concurrently=True,
        server_url="https://nationwide.api.honeyhive.ai"
        # server_url="http://localhost:3000"
    )

    print(result)
    HoneyHiveTracer.flush()

    # my_pipeline("hi")
