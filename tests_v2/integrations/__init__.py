"""
Integration tests for HoneyHive SDK with external providers.

These tests verify that the SDK works correctly with real LLM providers
and make actual API calls. They require environment variables to be set.

Test suites:
- test_openai_integration.py: OpenAI with OpenInference/Traceloop instrumentors
- test_anthropic_integration.py: Anthropic Claude with OpenInference instrumentor
- test_langchain_integration.py: LangChain/LangGraph with OpenInference instrumentor
- test_evaluate_integration.py: evaluate() function with real API
- test_tracing_integration.py: Core tracing functionality with real API

Environment Variables Required:
- HH_API_KEY: HoneyHive API key (required for all tests)
- HH_PROJECT: HoneyHive project name (optional, defaults to test project)
- OPENAI_API_KEY: For OpenAI and LangChain tests
- ANTHROPIC_API_KEY: For Anthropic tests

Run with tox:
    tox -e integrations              # Run all integration tests
    tox -e integrations-openai       # Run only OpenAI tests
    tox -e integrations-anthropic    # Run only Anthropic tests
    tox -e integrations-langchain    # Run only LangChain tests
    tox -e integrations-evaluate     # Run only evaluate() tests
    tox -e integrations-tracing      # Run only tracing tests

Run with pytest directly:
    pytest tests_v2/integrations/ -v
    pytest tests_v2/integrations/ -k openai -v
"""
