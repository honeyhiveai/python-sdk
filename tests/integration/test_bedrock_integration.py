"""
AWS Bedrock Integration Tests

Tests AWS Bedrock integration with HoneyHive using both OpenInference and
Traceloop (OpenLLMetry) instrumentors. Based on the example scripts in
examples/integrations/.

Requirements:
    pip install honeyhive[openinference-aws-bedrock]
    pip install honeyhive[traceloop-aws-bedrock]

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
    AWS_DEFAULT_REGION: AWS region (default: us-east-1)
"""

import os

import pytest

pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("AWS_ACCESS_KEY_ID"), reason="AWS_ACCESS_KEY_ID not set"
    ),
    pytest.mark.skipif(
        not os.getenv("AWS_SECRET_ACCESS_KEY"), reason="AWS_SECRET_ACCESS_KEY not set"
    ),
    pytest.mark.slow,
]

# Cross-region inference profile: supports on-demand throughput without provisioned capacity.
# Override via BEDROCK_MODEL_ID env var if needed.
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
# Traceloop instrumentor is validated with invoke_model; uses same model family.
TRACELOOP_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
)
REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")


@pytest.mark.bedrock
class TestOpenInferenceBedrockIntegration:
    """Test AWS Bedrock integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pytest.importorskip("boto3")
        pytest.importorskip("openinference.instrumentation.bedrock")

    def test_converse_basic(self):
        """Test basic Converse API call is traced end-to-end."""
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_openinference_converse_basic",
            source="pytest",
        )
        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = boto3.client("bedrock-runtime", region_name=REGION)
            response = client.converse(
                modelId=MODEL_ID,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": "Say 'test' and nothing else."}],
                    }
                ],
                inferenceConfig={"maxTokens": 20},
            )
            text = response["output"]["message"]["content"][0]["text"]
            assert len(text) > 0
            assert response["usage"]["inputTokens"] > 0
            assert response["usage"]["outputTokens"] > 0
            tracer.flush()
        finally:
            instrumentor.uninstrument()

    def test_converse_multi_turn(self):
        """Test multi-turn conversation is traced with all messages."""
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_openinference_converse_multi_turn",
            source="pytest",
        )
        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = boto3.client("bedrock-runtime", region_name=REGION)
            response = client.converse(
                modelId=MODEL_ID,
                messages=[
                    {"role": "user", "content": [{"text": "My name is Alice."}]},
                    {"role": "assistant", "content": [{"text": "Hello, Alice!"}]},
                    {"role": "user", "content": [{"text": "What is my name?"}]},
                ],
                inferenceConfig={"maxTokens": 30},
            )
            text = response["output"]["message"]["content"][0]["text"]
            assert "Alice" in text
            assert response["usage"]["inputTokens"] > 0
            assert response["usage"]["outputTokens"] > 0
            tracer.flush()
        finally:
            instrumentor.uninstrument()

    def test_converse_with_enrichment(self):
        """Test span enrichment alongside Bedrock tracing."""
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor

        from honeyhive import HoneyHiveTracer, enrich_span, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_openinference_converse_enrichment",
            source="pytest",
        )
        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @trace(event_type="model")
            def invoke(prompt: str) -> str:
                enrich_span(metadata={"model": MODEL_ID, "region": REGION})
                client = boto3.client("bedrock-runtime", region_name=REGION)
                response = client.converse(
                    modelId=MODEL_ID,
                    messages=[{"role": "user", "content": [{"text": prompt}]}],
                    inferenceConfig={"maxTokens": 20},
                )
                result = response["output"]["message"]["content"][0]["text"]
                enrich_span(metrics={"response_length": len(result)})
                return result

            result = invoke("Say 'enriched' and nothing else.")
            assert result is not None
            tracer.flush()
        finally:
            instrumentor.uninstrument()


@pytest.mark.bedrock
class TestTraceloopBedrockIntegration:
    """Test AWS Bedrock integration via Traceloop (OpenLLMetry) instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pytest.importorskip("boto3")
        pytest.importorskip("opentelemetry.instrumentation.bedrock")

    def test_invoke_model_basic(self):
        """Test basic invoke_model call is traced via Traceloop instrumentor."""
        import json

        import boto3
        from opentelemetry.instrumentation.bedrock import BedrockInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_traceloop_invoke_basic",
            source="pytest",
        )
        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = boto3.client("bedrock-runtime", region_name=REGION)
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 20,
                "messages": [
                    {"role": "user", "content": "Say 'traceloop' and nothing else."}
                ],
            }
            response = client.invoke_model(
                modelId=TRACELOOP_MODEL_ID,
                body=json.dumps(body),
            )
            result = json.loads(response["body"].read())
            assert "content" in result
            assert len(result["content"]) > 0
            tracer.flush()
        finally:
            instrumentor.uninstrument()

    def test_invoke_model_with_enrichment(self):
        """Test span enrichment works alongside Traceloop Bedrock tracing."""
        import json

        import boto3
        from opentelemetry.instrumentation.bedrock import BedrockInstrumentor

        from honeyhive import HoneyHiveTracer, enrich_span, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "bedrock-integration-test"),
            session_name="test_traceloop_invoke_enrichment",
            source="pytest",
        )
        instrumentor = BedrockInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @trace(event_type="model")
            def invoke(prompt: str) -> str:
                enrich_span(metadata={"instrumentor": "traceloop", "region": REGION})
                client = boto3.client("bedrock-runtime", region_name=REGION)
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 20,
                    "messages": [{"role": "user", "content": prompt}],
                }
                response = client.invoke_model(
                    modelId=TRACELOOP_MODEL_ID,
                    body=json.dumps(body),
                )
                result = json.loads(response["body"].read())
                text = result["content"][0]["text"]
                enrich_span(metrics={"response_length": len(text)})
                return text

            result = invoke("Say 'enriched' and nothing else.")
            assert result is not None
            tracer.flush()
        finally:
            instrumentor.uninstrument()
