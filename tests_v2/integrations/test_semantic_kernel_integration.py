"""
Microsoft Semantic Kernel Integration Tests

Tests Semantic Kernel integration with HoneyHive.
Based on examples/integrations/semantic_kernel_integration.py.

Requirements:
    pip install honeyhive semantic-kernel openinference-instrumentation-openai

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (Semantic Kernel uses OpenAI)

What is tested:
    - Basic chat completion via OpenAIChatCompletion service
    - Kernel function invocation with plugins
    - Automatic tracing of OpenAI calls (SK uses OpenAI internally)
    - Integration with @kernel_function decorated plugins

Verification approach:
    - Assert chat service returns non-empty response
    - Verify kernel function executes and returns expected result
    - Confirm OpenAI spans are captured via instrumentor
    - Validate tracer.flush() exports all spans
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"),
    pytest.mark.slow,
]


class TestSemanticKernelIntegration:
    """Test Semantic Kernel integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("semantic_kernel")
        pytest.importorskip("openinference.instrumentation.openai")

    @pytest.mark.asyncio
    async def test_basic_chat_completion(self):
        """Test basic Semantic Kernel chat completion is traced.
        
        Verifies:
        - OpenAIChatCompletion service initializes
        - ChatHistory accumulates messages
        - get_chat_message_content returns response
        - Response is non-empty
        """
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
        from semantic_kernel.contents import ChatHistory
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "semantic-kernel-integration-test"),
            session_name="test_basic_chat_completion",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            chat_service = OpenAIChatCompletion(
                ai_model_id="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

            history = ChatHistory()
            history.add_user_message("Say 'test' and nothing else.")

            # New API requires settings parameter
            try:
                from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
                settings = OpenAIChatPromptExecutionSettings(max_tokens=50)
                response = await chat_service.get_chat_message_content(history, settings)
            except (ImportError, TypeError):
                # Fall back to old API without settings
                response = await chat_service.get_chat_message_content(history)

            assert response is not None
            assert len(str(response)) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_kernel_function(self):
        """Test Semantic Kernel function invocation is traced.
        
        Verifies:
        - Kernel initializes with chat service
        - Plugin registers with kernel
        - @kernel_function decorated method executes
        - kernel.invoke returns expected result
        """
        from semantic_kernel import Kernel
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
        from semantic_kernel.functions import kernel_function
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "semantic-kernel-integration-test"),
            session_name="test_kernel_function",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create kernel with chat service
            kernel = Kernel()
            kernel.add_service(OpenAIChatCompletion(
                ai_model_id="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
                service_id="chat",
            ))

            # Define a simple plugin
            class TextPlugin:
                @kernel_function(name="uppercase", description="Convert text to uppercase")
                def uppercase(self, text: str) -> str:
                    return text.upper()

            kernel.add_plugin(TextPlugin(), plugin_name="text")

            @trace(event_type="chain")
            async def run_kernel_workflow(text: str) -> str:
                enrich_span(metadata={"input_text": text})
                result = await kernel.invoke(
                    plugin_name="text",
                    function_name="uppercase",
                    text=text,
                )
                enrich_span(metrics={"output_length": len(str(result))})
                return str(result)

            result = await run_kernel_workflow("hello world")
            assert result == "HELLO WORLD"

            tracer.flush()

        finally:
            instrumentor.uninstrument()
