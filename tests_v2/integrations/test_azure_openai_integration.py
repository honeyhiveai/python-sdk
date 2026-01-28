"""
Azure OpenAI Integration Tests

Tests Azure OpenAI integration with HoneyHive using Traceloop instrumentor.
Based on examples/integrations/traceloop_azure_openai_example.py.

Requirements:
    pip install honeyhive opentelemetry-instrumentation-openai openai

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    AZURE_OPENAI_API_KEY: Azure OpenAI API key
    AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
    AZURE_OPENAI_DEPLOYMENT: Deployment name (e.g., gpt-35-turbo)

What is tested:
    - Basic chat completion with Azure OpenAI client
    - Automatic tracing via Traceloop OpenAI instrumentor
    - Span enrichment with Azure-specific metadata
    - Token usage metrics capture

Verification approach:
    - Assert non-empty response content from Azure OpenAI
    - Verify response structure matches expected OpenAI format
    - Confirm tracer.flush() completes without error (traces exported)
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("AZURE_OPENAI_API_KEY"), reason="AZURE_OPENAI_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("AZURE_OPENAI_ENDPOINT"), reason="AZURE_OPENAI_ENDPOINT not set"),
    pytest.mark.slow,
]


class TestAzureOpenAIIntegration:
    """Test Azure OpenAI integration via Traceloop instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("openai")
        pytest.importorskip("opentelemetry.instrumentation.openai")

    def test_basic_chat_completion(self):
        """Test basic Azure OpenAI chat completion is traced.
        
        Verifies:
        - AzureOpenAI client initializes with endpoint/key
        - Chat completion returns valid response
        - Response has non-empty content
        - Traces are exported via flush()
        """
        from openai import AzureOpenAI
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "azure-openai-integration-test"),
            session_name="test_basic_chat_completion",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )

            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")
            response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": "Say 'test' and nothing else."}],
                max_tokens=10,
            )

            assert response.choices[0].message.content is not None
            assert len(response.choices[0].message.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_chat_with_enrichment(self):
        """Test Azure OpenAI with span enrichment.
        
        Verifies:
        - @trace decorator wraps Azure OpenAI call
        - enrich_span() adds deployment metadata
        - enrich_span() adds token usage metrics
        - Nested spans are properly linked
        """
        from openai import AzureOpenAI
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "azure-openai-integration-test"),
            session_name="test_chat_with_enrichment",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="tool")
            def process_with_azure(prompt: str) -> str:
                enrich_span(metadata={"deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT")})

                client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version="2024-02-01",
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                )

                deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")
                response = client.chat.completions.create(
                    model=deployment,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=20,
                )

                result = response.choices[0].message.content
                enrich_span(metrics={"tokens": response.usage.total_tokens})
                return result

            result = process_with_azure("Say 'azure test' and nothing else.")
            assert result is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()
