import os

MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")

from honeyhive import HoneyHiveTracer, enrich_session

if __name__ == "__main__":

    HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
    )


    enrich_session(user_properties={
    "user_id": "12345",
    "user_email": "user@example.com",
    "user_properties": {
        "is_premium": True,
        "subscription_plan": "pro",
        "last_login": "2024-01-01T12:00:00Z"
    }
    })