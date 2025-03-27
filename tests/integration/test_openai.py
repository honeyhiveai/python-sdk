from honeyhive import HoneyHiveTracer, trace
from openai import OpenAI

client = OpenAI()

@trace
def simple_function(a, b):
    return a + b

def call_openai():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello, world!"}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Initialize HoneyHive tracer
    tracer = HoneyHiveTracer(
        session_name="Python SDK Test",
        source="integration"
    )
    
    # Test a simple trace
    result = simple_function(5, 10)
    response = call_openai()
    print(f"Simple function result: {result}")
    print(f"OpenAI response: {response}")

    print('Completed test')
