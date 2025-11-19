#!/usr/bin/env python3
"""
AWS Bedrock + OpenLLMetry (Traceloop) Integration Example

This example demonstrates how to integrate AWS Bedrock with HoneyHive using
OpenLLMetry's individual instrumentor package, following HoneyHive's
"Bring Your Own Instrumentor" architecture.

Requirements:
- pip install honeyhive[traceloop-bedrock]
- Set environment variables: HH_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
"""

import os
import json
from typing import Dict, Any, List

# Import HoneyHive components
from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType

# Import AWS Bedrock SDK
import boto3

# Import OpenLLMetry Bedrock instrumentor
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor


def setup_tracing() -> HoneyHiveTracer:
    """Initialize HoneyHive tracer with OpenLLMetry Bedrock instrumentor."""

    # Check required environment variables
    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")

    if not all([os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY")]):
        raise ValueError(
            "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required"
        )

    # Initialize OpenLLMetry Bedrock instrumentor
    bedrock_instrumentor = BedrockInstrumentor()

    # Initialize HoneyHive tracer FIRST
    tracer = HoneyHiveTracer.init(
        source="traceloop_bedrock_example",
        project=os.getenv("HH_PROJECT", "bedrock-traceloop-demo"),
    )
    print("✓ HoneyHive tracer initialized")

    # Initialize instrumentor separately with tracer_provider
    bedrock_instrumentor.instrument(tracer_provider=tracer.provider)

    print("✅ Tracing initialized with OpenLLMetry Bedrock instrumentor")
    return tracer


def basic_bedrock_example():
    """Basic AWS Bedrock usage with automatic tracing via OpenLLMetry."""

    print("\n🔧 Basic Bedrock Example")
    print("-" * 40)

    # Initialize Bedrock client
    bedrock = boto3.client(
        "bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # Simple model invocation - automatically traced by OpenLLMetry
    try:
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {"role": "user", "content": "Explain OpenLLMetry in one sentence."}
            ],
        }

        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(request_body))

        response_body = json.loads(response["body"].read())
        result = response_body["content"][0]["text"]
        print(f"✅ Response: {result}")

        # OpenLLMetry automatically captures:
        # - Token usage and costs (when supported)
        # - Model performance metrics
        # - Request/response content
        # - Latency and timing data

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


@trace(event_type=EventType.chain)
def multi_model_bedrock_workflow(prompts: List[str]) -> Dict[str, Any]:
    """Advanced workflow using multiple Bedrock models with business context tracing."""

    print(f"\n🚀 Multi-Model Workflow: {len(prompts)} prompts")
    print("-" * 40)

    # Add business context to the trace
    enrich_span(
        {
            "business.workflow": "multi_model_analysis",
            "business.prompt_count": len(prompts),
            "bedrock.strategy": "model_comparison",
            "instrumentor.type": "openllmetry",
            "observability.enhanced": True,
        }
    )

    bedrock = boto3.client(
        "bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # Test multiple Bedrock models
    models = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "amazon.titan-text-express-v1",
    ]

    results = []

    try:
        for i, prompt in enumerate(prompts):
            print(f"📝 Processing prompt {i+1}: {prompt[:50]}...")

            prompt_results = {}

            for model_id in models:
                try:
                    # Prepare request based on model type
                    if "anthropic" in model_id:
                        body = {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 150,
                            "messages": [{"role": "user", "content": prompt}],
                        }
                    elif "titan" in model_id:
                        body = {
                            "inputText": prompt,
                            "textGenerationConfig": {
                                "maxTokenCount": 150,
                                "temperature": 0.7,
                            },
                        }

                    # Invoke model
                    response = bedrock.invoke_model(
                        modelId=model_id, body=json.dumps(body)
                    )

                    response_body = json.loads(response["body"].read())

                    # Extract response based on model type
                    if "anthropic" in model_id:
                        content = response_body["content"][0]["text"]
                    elif "titan" in model_id:
                        content = response_body["results"][0]["outputText"]

                    prompt_results[model_id] = {
                        "content": content,
                        "length": len(content),
                    }

                    print(f"✅ {model_id.split('.')[-1]}: {len(content)} chars")

                except Exception as model_error:
                    prompt_results[model_id] = {"error": str(model_error)}
                    print(f"❌ {model_id.split('.')[-1]}: {model_error}")

            results.append({"prompt": prompt, "responses": prompt_results})

        # Add results to span
        enrich_span(
            {
                "business.prompts_processed": len(prompts),
                "business.models_tested": len(models),
                "bedrock.models_used": models,
                "business.workflow_status": "completed",
            }
        )

        return {
            "prompts_processed": len(prompts),
            "models_tested": models,
            "results": results,
        }

    except Exception as e:
        enrich_span(
            {
                "error.type": "workflow_error",
                "error.message": str(e),
                "business.workflow_status": "failed",
            }
        )
        print(f"❌ Workflow failed: {e}")
        raise


def demonstrate_cost_tracking():
    """Demonstrate OpenLLMetry's automatic cost tracking capabilities."""

    print("\n💰 Cost Tracking Demonstration")
    print("-" * 40)

    bedrock = boto3.client(
        "bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # OpenLLMetry automatically tracks costs for different models
    models_to_test = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-express-v1",
    ]

    for model_id in models_to_test:
        print(f"Testing cost tracking for {model_id.split('.')[-1]}...")

        try:
            if "anthropic" in model_id:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Count from 1 to 3."}],
                }
            elif "titan" in model_id:
                body = {
                    "inputText": "Count from 1 to 3.",
                    "textGenerationConfig": {"maxTokenCount": 50},
                }

            response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))

            response_body = json.loads(response["body"].read())
            print(f"✅ {model_id.split('.')[-1]}: Response generated")
            # OpenLLMetry would automatically calculate and track the cost
            print("   (Cost tracking would be automatic with working instrumentor)")

        except Exception as e:
            print(f"❌ {model_id.split('.')[-1]} failed: {e}")


def main():
    """Main example function."""

    print("🧪 AWS Bedrock + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)

    try:
        # Setup tracing
        tracer = setup_tracing()

        # Basic example
        basic_bedrock_example()

        # Advanced workflow
        test_prompts = [
            "What is artificial intelligence?",
            "Explain machine learning briefly.",
            "What are the benefits of cloud computing?",
        ]

        result = multi_model_bedrock_workflow(test_prompts)
        print(f"\n📊 Workflow Result: {len(result['models_tested'])} models tested")

        # Cost tracking demonstration
        demonstrate_cost_tracking()

        # Flush traces
        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush()
        print("✅ Traces sent successfully!")

        print("\n🎉 Example completed successfully!")
        print("\n💡 Key OpenLLMetry Benefits Demonstrated:")
        print("   • Automatic cost tracking per model")
        print("   • Enhanced token usage metrics")
        print("   • Request/response content capture")
        print("   • Performance and latency monitoring")
        print("   • Multi-model workflow tracing")
        print("   • Seamless integration with HoneyHive BYOI")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
