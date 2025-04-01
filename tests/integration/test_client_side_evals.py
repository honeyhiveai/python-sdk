import os
from honeyhive import HoneyHiveTracer, enrich_session

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")


if __name__ == "__main__":
    HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
    )

    # ...

    enrich_session(metrics={
    "json_validated": True,
    "num_actions": 10,
    # any other custom fields and values as you need
    "step_evals": [
        {
        "invalid_grammar": False,
        "unable_to_locate_UI": True
        }
    ],
    })