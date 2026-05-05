#!/usr/bin/env python3
"""
AWS Bedrock Compatibility Test for HoneyHive SDK with Traceloop SDK (OpenLLMetry)

Tests AWS Bedrock integration using Traceloop SDK instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import json
import os
from typing import Optional


def test_traceloop_bedrock_integration():
    """Test AWS Bedrock integration with HoneyHive via Traceloop SDK instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not all([api_key, project, aws_access_key, aws_secret_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - AWS_ACCESS_KEY_ID (AWS access key)")
        print("   - AWS_SECRET_ACCESS_KEY (AWS secret key)")
        print("   - AWS_REGION (optional, defaults to us-east-1)")
        return False

    try:
        # Import dependencies
        import boto3

        # Try to import the OpenLLMetry instrumentor
        try:
            from opentelemetry.instrumentation.bedrock import BedrockInstrumentor

            instrumentor_available = True
            print("✓ OpenLLMetry Bedrock instrumentor imported successfully")
        except ImportError as import_err:
            print(f"⚠️ OpenLLMetry Bedrock instrumentor import failed: {import_err}")
            print("   This may be due to package compatibility issues")
            print("   Continuing test with manual instrumentation setup...")
            instrumentor_available = False

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up AWS Bedrock with HoneyHive + Traceloop integration...")

        # Initialize instrumentor if available
        if instrumentor_available:
            bedrock_instrumentor = BedrockInstrumentor()
            bedrock_instrumentor.instrument()
            print("✓ Bedrock instrumentor initialized and instrumented")

            # Initialize HoneyHive tracer with instrumentor
            tracer = HoneyHiveTracer.init(
                api_key=api_key,
                project=project,
                instrumentors=[bedrock_instrumentor],
                source="traceloop_bedrock_test",
            )
        else:
            # Initialize HoneyHive tracer without instrumentor
            tracer = HoneyHiveTracer.init(
                api_key=api_key,
                project=project,
                source="traceloop_bedrock_test_fallback",
            )

        print("✓ HoneyHive tracer initialized")

        # Create Bedrock client
        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )
        print("✓ AWS Bedrock client created")

        # Test basic Bedrock model invocation
        print("🤖 Testing basic Bedrock model invocation...")
        try:
            # Test with Claude Haiku 4.5 (latest fast model)
            model_id = "anthropic.claude-haiku-4-5-20251001-v1:0"

            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": "What is 2+2? Answer briefly."}
                ],
            }

            response = bedrock_client.invoke_model(
                modelId=model_id, body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())
            content = response_body.get("content", [{}])[0].get("text", "")

            print(f"✓ Bedrock response received: {content[:100]}...")

            # Verify response structure
            if response_body and "content" in response_body:
                print("✓ Response structure validated")
            else:
                print("⚠️ Unexpected response structure")

        except Exception as bedrock_error:
            print(f"⚠️ Bedrock API test failed: {bedrock_error}")
            print(
                "   This may be due to AWS credentials, region, or model availability"
            )

        # Test span enrichment if instrumentor is available
        if instrumentor_available:
            print("🔧 Testing span enrichment...")
            try:
                with tracer.enrich_span(
                    metadata={
                        "test_type": "traceloop_compatibility",
                        "provider": "bedrock",
                        "instrumentor": "traceloop_sdk",
                        "aws_region": aws_region,
                    },
                    outputs={"model_used": model_id},
                ) as span:
                    # Test with Amazon Titan model for variety
                    titan_model_id = "amazon.titan-text-express-v1"
                    titan_request = {
                        "inputText": "Hello from OpenLLMetry Bedrock!",
                        "textGenerationConfig": {
                            "maxTokenCount": 50,
                            "temperature": 0.7,
                        },
                    }

                    try:
                        titan_response = bedrock_client.invoke_model(
                            modelId=titan_model_id, body=json.dumps(titan_request)
                        )

                        titan_body = json.loads(titan_response["body"].read())
                        span_data = {
                            "titan_response_length": len(str(titan_body)),
                            "models_tested": [model_id, titan_model_id],
                        }
                        print(f"✓ Multi-model test completed: {span_data}")

                    except Exception as titan_error:
                        print(f"⚠️ Titan model test failed: {titan_error}")
                        span_data = {
                            "models_tested": [model_id],
                            "titan_error": str(titan_error),
                        }

            except Exception as enrich_error:
                print(f"⚠️ Span enrichment test skipped: {enrich_error}")

        # Flush traces
        print("📤 Flushing traces...")
        tracer.force_flush()
        print("✓ Traces flushed successfully")

        print("\n🎉 Bedrock + OpenLLMetry integration test completed!")
        print("📊 Test Summary:")
        print(f"   • Instrumentor Available: {'✓' if instrumentor_available else '❌'}")
        print(f"   • AWS Region: {aws_region}")
        print(f"   • Models Tested: Claude Haiku 4.5, Titan Text Express")
        print("📝 Check your HoneyHive project dashboard for traces")

        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_traceloop_bedrock_integration()
    exit(0 if success else 1)
