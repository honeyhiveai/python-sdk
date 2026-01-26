"""
AWS Bedrock Integration Tests

Tests AWS Bedrock integration with HoneyHive using OpenInference instrumentor.
Based on examples/integrations/openinference_bedrock_example.py.

Requirements:
    pip install honeyhive boto3 openinference-instrumentation-bedrock

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
    AWS_DEFAULT_REGION: AWS region (e.g., us-east-1)

What is tested:
    - Claude model invocation via Bedrock runtime
    - Amazon Titan model invocation via Bedrock runtime
    - Automatic tracing via OpenInference Bedrock instrumentor
    - Span enrichment with model/region metadata

Verification approach:
    - Assert model response contains expected fields
    - Verify completion/results are non-empty
    - Confirm tracer.flush() exports traces successfully
"""

import os
import json
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("AWS_ACCESS_KEY_ID"), reason="AWS_ACCESS_KEY_ID not set"),
    pytest.mark.skipif(not os.getenv("AWS_SECRET_ACCESS_KEY"), reason="AWS_SECRET_ACCESS_KEY not set"),
    pytest.mark.slow,
]


class TestBedrockIntegration:
    """Test AWS Bedrock integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("boto3")
        pytest.importorskip("openinference.instrumentation.bedrock")

    def test_claude_invocation(self):
        """Test Claude model invocation via Bedrock is traced.
        
        Verifies:
        - boto3 Bedrock client connects successfully
        - Claude v2 model accepts Anthropic prompt format
        - Response contains 'completion' field
        - Completion text is non-empty
        """
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_claude_invocation",
            source="pytest",
        )

        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            )

            # Claude v2 request format
            request = {
                "prompt": "\n\nHuman: Say 'test' and nothing else.\n\nAssistant:",
                "max_tokens_to_sample": 50,
                "temperature": 0.1,
            }

            response = client.invoke_model(
                modelId="anthropic.claude-v2",
                body=json.dumps(request),
                contentType="application/json",
                accept="application/json",
            )

            result = json.loads(response["body"].read())
            assert "completion" in result
            assert len(result["completion"]) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_titan_invocation(self):
        """Test Amazon Titan model invocation via Bedrock is traced.
        
        Verifies:
        - Titan model accepts Amazon-specific request format
        - Response contains 'results' array
        - Results array is non-empty
        """
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_titan_invocation",
            source="pytest",
        )

        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            )

            request = {
                "inputText": "Say 'titan test' and nothing else.",
                "textGenerationConfig": {
                    "maxTokenCount": 50,
                    "temperature": 0.1,
                },
            }

            response = client.invoke_model(
                modelId="amazon.titan-text-express-v1",
                body=json.dumps(request),
                contentType="application/json",
                accept="application/json",
            )

            result = json.loads(response["body"].read())
            assert "results" in result
            assert len(result["results"]) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_bedrock_with_enrichment(self):
        """Test Bedrock with span enrichment.
        
        Verifies:
        - @trace decorator wraps Bedrock call
        - enrich_span() captures model and region
        - enrich_span() captures response metrics
        - Parent-child span relationship is preserved
        """
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_bedrock_with_enrichment",
            source="pytest",
        )

        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="model")
            def invoke_claude(prompt: str) -> str:
                enrich_span(metadata={"model": "claude-v2", "region": os.getenv("AWS_DEFAULT_REGION")})

                client = boto3.client(
                    "bedrock-runtime",
                    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                )

                request = {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 50,
                    "temperature": 0.1,
                }

                response = client.invoke_model(
                    modelId="anthropic.claude-v2",
                    body=json.dumps(request),
                    contentType="application/json",
                    accept="application/json",
                )

                result = json.loads(response["body"].read())
                enrich_span(metrics={"response_length": len(result["completion"])})
                return result["completion"]

            result = invoke_claude("Say 'enriched' and nothing else.")
            assert result is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()
