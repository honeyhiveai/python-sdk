import os


MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer


if __name__ == "__main__":
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        session_name="Session Name",
        source="source_identifier"
    )

    # Set feedback, metrics, and metadata during the session
    tracer.enrich_session(feedback={'some_domain_expert': "Session feedback"})
    tracer.enrich_session(metrics={"metric_name": "metric_value"})
    tracer.enrich_session(metadata={"key": "value"})

    # Set two or more of the following at once
    tracer.enrich_session(
        feedback={'some_domain_expert': "Session feedback"},
        metrics={"metric_name": "metric_value"},
        metadata={"key": "value"}
    )
    assert tracer.session_id is not None