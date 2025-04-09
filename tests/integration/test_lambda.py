from honeyhive import HoneyHiveTracer, trace, enrich_session, enrich_span
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@trace
def simple_function(a, b):
    enrich_session(metadata={"test": "session"})
    enrich_span(metadata={"test": "span"})
    return a + b

def call_openai():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello, world!"}]
    )
    return response.choices[0].message.content

def lambda_handler(event, context):
    # Initialize HoneyHive tracer
    tracer = HoneyHiveTracer(
        session_name="Lambda Test",
        source="lambda_integration"
    )
    
    # Test a simple trace
    result = simple_function(5, 10)
    response = call_openai()
    
    # Prepare the response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'simple_function_result': result,
            'openai_response': response,
            'message': 'Completed test'
        })
    }
