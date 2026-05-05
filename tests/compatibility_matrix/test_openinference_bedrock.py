#!/usr/bin/env python3
"""
AWS Bedrock Compatibility Test for HoneyHive SDK

Tests AWS Bedrock integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import json
import os
import sys
from typing import Optional


def test_bedrock_integration():
    """Test AWS Bedrock integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    if not all([api_key, project, aws_access_key, aws_secret_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - AWS_ACCESS_KEY_ID (AWS access key)")
        print("   - AWS_SECRET_ACCESS_KEY (AWS secret key)")
        print("   - AWS_DEFAULT_REGION (optional, defaults to us-east-1)")
        return False

    try:
        # Import dependencies
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up AWS Bedrock with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        bedrock_instrumentor = BedrockInstrumentor()
        print("✓ Bedrock instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[bedrock_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Bedrock instrumentor")

        # 3. Initialize AWS Bedrock client
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        client = session.client("bedrock-runtime")
        print(f"✓ AWS Bedrock client initialized (region: {aws_region})")

        # 4. Test Claude model via Bedrock (automatically traced)
        print("🚀 Testing AWS Bedrock with Claude model...")

        # Prepare request for Claude
        claude_request = {
            "prompt": "\n\nHuman: Say hello and confirm this is a compatibility test for HoneyHive + AWS Bedrock integration.\n\nAssistant:",
            "max_tokens_to_sample": 100,
            "temperature": 0.1,
            "top_p": 0.9,
        }

        response = client.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps(claude_request),
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        result_text = response_body.get("completion", "")
        print(f"✓ Claude via Bedrock response: {result_text.strip()}")

        # 5. Test Amazon Titan model (if available)
        print("🔧 Testing Amazon Titan model...")

        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "aws_bedrock"},
            outputs={"model_used": "amazon.titan-text-express-v1"},
        ) as span:
            titan_request = {
                "inputText": "What is 2+2? Answer briefly.",
                "textGenerationConfig": {
                    "maxTokenCount": 50,
                    "temperature": 0.1,
                    "topP": 0.9,
                },
            }

            try:
                titan_response = client.invoke_model(
                    modelId="amazon.titan-text-express-v1",
                    body=json.dumps(titan_request),
                    contentType="application/json",
                    accept="application/json",
                )

                titan_body = json.loads(titan_response["body"].read())
                titan_text = titan_body.get("results", [{}])[0].get("outputText", "")

                span_data = {
                    "model": "amazon.titan-text-express-v1",
                    "input_tokens": len(titan_request["inputText"].split()),
                    "output": titan_text.strip(),
                }
                print(f"✓ Titan response: {titan_text.strip()}")

            except Exception as e:
                print(f"⚠️  Titan model not available or error: {e}")
                span_data = {"model": "amazon.titan-text-express-v1", "error": str(e)}

        # 6. Test Cohere model via Bedrock
        print("🔧 Testing Cohere model via Bedrock...")

        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "aws_bedrock_cohere"},
        ) as span:
            cohere_request = {
                "prompt": "Translate 'Hello World' to French:",
                "max_tokens": 30,
                "temperature": 0.1,
            }

            try:
                cohere_response = client.invoke_model(
                    modelId="cohere.command-text-v14",
                    body=json.dumps(cohere_request),
                    contentType="application/json",
                    accept="application/json",
                )

                cohere_body = json.loads(cohere_response["body"].read())
                cohere_text = cohere_body.get("generations", [{}])[0].get("text", "")

                span_data = {
                    "model": "cohere.command-text-v14",
                    "response": cohere_text.strip(),
                }
                print(f"✓ Cohere via Bedrock response: {cohere_text.strip()}")

            except Exception as e:
                print(f"⚠️  Cohere model not available or error: {e}")
                span_data = {"model": "cohere.command-text-v14", "error": str(e)}

        # 7. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 AWS Bedrock integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-bedrock")
        print("   pip install boto3")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the AWS Bedrock compatibility test."""
    print("🧪 HoneyHive + AWS Bedrock Compatibility Test")
    print("=" * 50)

    success = test_bedrock_integration()

    if success:
        print("\n✅ AWS Bedrock compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ AWS Bedrock compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
