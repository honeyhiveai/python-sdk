import os


MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")

from honeyhive import HoneyHiveTracer, trace, enrich_span

if __name__ == "__main__":

    HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
    )

    prompt_template = {
        "template": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Write a short poem about programming."}
        ],
        "prompt": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Write a short poem about programming."},
        ]
    }

    # ...

    @trace
    def my_function(input, prompt_template):
        # ...

        enrich_span(config={
            "template": prompt_template["template"],
            "prompt": prompt_template["prompt"],
            "hyperparams": {
                "temperature": 0.5,
                "max_tokens": 100,
                "top_p": 0.9,
                "top_k": 50,
            }
        })

        # ...
        response = "This is a mock response."
        return response

    # ...
    result = my_function("This is a mock input", prompt_template)