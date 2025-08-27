from honeyhive import HoneyHiveTracer, trace, enrich_session, enrich_span
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI()

@trace
def simple_function(a, b):
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
    print("🚀 Initializing HoneyHive tracer...")
    
    # Initialize HoneyHive tracer with the refactored OpenTelemetry implementation
    # This maintains backward compatibility with the old HoneyHiveTracer.init() API
    tracer = HoneyHiveTracer.init(
        session_name="Python SDK Test",
        source="integration"
    )
    
    print(f"✅ Tracer initialized with session_id: {tracer.session_id}")
    
    # Enrich the session with metadata
    enrich_session(metadata={"test": "integration_test", "version": "refactored"})
    
    print("📊 Running traced function...")
    result = random_function()
    
    print("🤖 Calling OpenAI...")
    response = call_openai()
    
    print(f"Simple function result: {result}")
    print(f"OpenAI response: {response}")
    
    print('✅ Test completed successfully!')

if __name__ == "__main__":
    handler({}, {})