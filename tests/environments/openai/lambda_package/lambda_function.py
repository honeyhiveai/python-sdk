from honeyhive import HoneyHiveTracer, trace
import os

@trace
def simple_function(a, b):
    return a + b

if __name__ == "__main__":
    # Initialize HoneyHive tracer
    tracer = HoneyHiveTracer(
        api_key=os.environ.get("HH_API_KEY"),
        project=os.environ.get("HH_PROJECT"),
        server_url=os.environ.get("HH_SERVER_URL", "https://api.honeyhive.ai"),
        session_name="Python SDK Test",
        source="integration_test"
    )
    
    # Test a simple trace
    result = simple_function(5, 10)
    print(f"Simple function result: {result}")
    
    # Print some diagnostic info
    print(f"HoneyHive SDK Test successful!")
    print(f"Environment variables:")
    print(f"  HH_PROJECT: {os.environ.get('HH_PROJECT')}")
    print(f"  HH_SERVER_URL: {os.environ.get('HH_SERVER_URL')}")
