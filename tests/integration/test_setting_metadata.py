import os

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")

from honeyhive import HoneyHiveTracer, trace, enrich_span

if __name__ == "__main__":

    HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
    )

    # ...

    @trace
    def my_function(input, something):
    # ...

        enrich_span(metadata={
            "experiment-id": 12345,
            "something": something,
            # any other custom fields and values as you need
        })

        # ...
        response = "This is a mock response."
        return response

    # ...

    my_function("This is a mock input", "some-metadata")