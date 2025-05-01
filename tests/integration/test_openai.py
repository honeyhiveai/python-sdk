from honeyhive import HoneyHiveTracer, trace, enrich_session, enrich_span
from openai import OpenAI

client = OpenAI()

@trace
def simple_function(a, b):
    enrich_session(metadata={"test": "session"})
    enrich_span(metadata={"test": "span"})
    return a + b


def random_function():
    return simple_function(5, 10)


def call_openai():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello, world!"}]
    )
    return response.choices[0].message.content

def handler(event, context):
    # Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        session_name="Python SDK Test",
        source="integration"
    )
    tracer.enrich_session(metadata={"test": "sessionsssssss"})
    
    # Test a simple trace
    result = random_function()
    response = call_openai()
    print(f"Simple function result: {result}")
    print(f"OpenAI response: {response}")

    print('Completed test')

if __name__ == "__main__":
    handler({}, {})