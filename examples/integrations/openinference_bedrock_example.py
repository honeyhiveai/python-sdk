#!/usr/bin/env python3
"""
Simple AWS Bedrock Integration with HoneyHive

This example shows the simplest way to add HoneyHive tracing to AWS Bedrock calls.
Zero code changes to your existing Bedrock usage!
"""

import os
import json
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.bedrock import BedrockInstrumentor
import boto3


def main():
    """Simple AWS Bedrock integration example."""
    print("🚀 Simple AWS Bedrock + HoneyHive Integration")
    print("=" * 45)

    # 1. Initialize HoneyHive with Bedrock instrumentor
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "your-honeyhive-key"),
        project=os.getenv("HH_PROJECT", "bedrock-simple-demo"),
        source=os.getenv("HH_SOURCE", "development"),
    )
    print("✓ HoneyHive tracer initialized")

    # Initialize instrumentor separately with tracer_provider
    bedrock_instrumentor = BedrockInstrumentor()
    bedrock_instrumentor.instrument(tracer_provider=tracer.provider)
    print("✓ HoneyHive tracer initialized with Bedrock instrumentor")

    # 2. Set up AWS Bedrock client exactly as you normally would
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    # 3. Make Bedrock calls - they're traced via the Bedrock instrumentor!
    print("\n📞 Making AWS Bedrock API calls...")

    try:
        # Claude via Bedrock
        claude_request = {
            "prompt": "\n\nHuman: What is artificial intelligence?\n\nAssistant:",
            "max_tokens_to_sample": 150,
            "temperature": 0.1,
            "top_p": 0.9,
        }

        response = client.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps(claude_request),
            contentType="application/json",
            accept="application/json",
        )

        result = json.loads(response["body"].read())
        print(f"✓ Claude response: {result['completion'].strip()}")

        # Amazon Titan via Bedrock - also traced via instrumentor
        print("\n🔧 Trying Amazon Titan model...")

        titan_request = {
            "inputText": "Give me a fun fact about space.",
            "textGenerationConfig": {
                "maxTokenCount": 100,
                "temperature": 0.1,
                "topP": 0.9,
            },
        }

        titan_response = client.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=json.dumps(titan_request),
            contentType="application/json",
            accept="application/json",
        )

        titan_result = json.loads(titan_response["body"].read())
        titan_text = titan_result.get("results", [{}])[0].get("outputText", "")
        print(f"✓ Titan response: {titan_text.strip()}")

        print("\n🎉 All calls traced to HoneyHive via Bedrock instrumentor!")
        print("Check your HoneyHive dashboard to see the traces.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to set AWS credentials:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - AWS_DEFAULT_REGION (optional)")


if __name__ == "__main__":
    main()
