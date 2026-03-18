#!/usr/bin/env python3
"""
AWS Bedrock + HoneyHive integration example.

Demonstrates simple AWS Bedrock Converse API calls with HoneyHive tracing.
All Bedrock calls are automatically traced via the OpenInference instrumentor.

Install:
    pip install honeyhive openinference-instrumentation-bedrock boto3

Run:
    python examples/integrations/openinference_bedrock_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION  (optional, defaults to "us-east-1")
"""

import os

import boto3
from openinference.instrumentation.bedrock import BedrockInstrumentor

from honeyhive import HoneyHiveTracer

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"


def main() -> None:
    """Run simple Bedrock Converse calls with HoneyHive tracing."""
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_bedrock_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument the Bedrock SDK
    instrumentor = BedrockInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use Bedrock as usual — all calls are traced automatically
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "What is the capital of France?"}],
                }
            ],
            inferenceConfig={"maxTokens": 100},
        )
        print(f"Response: {response['output']['message']['content'][0]['text']}")

        # A follow-up call — also traced
        response2 = client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Tell me a fun fact about that city."}],
                }
            ],
            inferenceConfig={"maxTokens": 100},
        )
        print(f"Follow-up: {response2['output']['message']['content'][0]['text']}")
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
