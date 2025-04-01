import os


MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
MY_SOURCE = os.getenv("HH_SOURCE")
MY_SESSION_NAME = os.getenv("HH_SESSION")
MY_HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer

# Add this code at the beginning of your AI pipeline code

if __name__ == "__main__":
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        source=MY_SOURCE, # Optional
        session_name=MY_SESSION_NAME, # Optional
        server_url=MY_HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
    )

    assert tracer.session_id is not None
    assert tracer.project is not None
    assert tracer.source is not None
    assert tracer.session_name is not None
    assert tracer.server_url is not None

# Your LLM and vector database calls will now be automatically instrumented
# Run HoneyHiveTracer.init() again to end the current session and start a new one