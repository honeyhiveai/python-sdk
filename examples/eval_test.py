from honeyhive.experiments import evaluate, evaluator
import os
from openai import OpenAI
import random
from openinference.instrumentation.openai import OpenAIInstrumentor

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def function_to_evaluate(datapoint):
    """Evaluation function that receives a single datapoint dict."""
    inputs = datapoint.get("inputs", {})
    ground_truth = datapoint.get("ground_truth", {})

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are an expert analyst specializing in {inputs['product_type']} market trends."},
            {"role": "user", "content": f"Could you provide an analysis of the current market performance and consumer reception of {inputs['product_type']} in {inputs['region']}? Please include any notable trends or challenges specific to this region."}
        ]
    )
    return completion.choices[0].message.content

dataset = [
    {
        "inputs": {
            "product_type": "electric vehicles",
            "region": "western europe",
            "time_period": "first half of 2023",
            "metric_1": "total revenue",
            "metric_2": "market share"
        },
        "ground_truth": {
            "response": "As of 2023, the electric vehicle (EV) market in Western Europe is experiencing significant growth, with the region maintaining its status as a global leader in EV adoption. [continue...]",
        }
    },
    {
        "inputs": {
            "product_type": "gaming consoles",
            "region": "north america",
            "time_period": "holiday season 2022",
            "metric_1": "units sold",
            "metric_2": "gross profit margin"
        },
        "ground_truth": {
            "response": "As of 2023, the gaming console market in North America is characterized by intense competition, steady consumer demand, and evolving trends influenced by technological advancements and changing consumer preferences. [continue...]",
        }
    }
]

@evaluator
def sample_evaluator(outputs, inputs, ground_truth):
    """Evaluator that receives outputs, inputs, and ground_truth (singular)."""
    return random.randint(1, 5)

if __name__ == "__main__":
    result = evaluate(
        function = function_to_evaluate,                         # Function that will be evaluated
        api_key = os.getenv("HH_API_KEY"),                       # Your HoneyHive API key
        name = 'Sample Experiment',                              # Name for this experiment run
        dataset = dataset,
        evaluators=[sample_evaluator],                           # Custom client-side evaluators to compute metrics on each run
        instrumentors=[lambda: OpenAIInstrumentor()],
        server_url="https://api.testing-dp-1.honeyhive.ai",
        verbose=True,
    )

    print(f"\nEvaluation complete!")
    print(f"Success: {result.success}")
    print(f"Passed: {len(result.passed)}")
    print(f"Failed: {len(result.failed)}")