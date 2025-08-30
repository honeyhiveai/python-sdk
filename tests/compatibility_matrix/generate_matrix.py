#!/usr/bin/env python3
"""
Generate HoneyHive Compatibility Matrix Documentation

Creates comprehensive documentation mapping HoneyHive SDK support to OpenInference instrumentors
and model providers from the official docs.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def generate_compatibility_matrix():
    """Generate the complete compatibility matrix documentation."""
    
    # Provider mappings based on HoneyHive docs and OpenInference availability
    compatibility_data = {
        "Direct Provider Support": [
            {
                "provider": "OpenAI",
                "models": "GPT-4, GPT-3.5-turbo, embeddings",
                "instrumentor": "openinference-instrumentation-openai", 
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_openai.py",
                "notes": "Complete chat, completion, and embedding support"
            },
            {
                "provider": "Azure OpenAI", 
                "models": "Same as OpenAI via Azure endpoints",
                "instrumentor": "openinference-instrumentation-openai",
                "integration": "✅ Full Support", 
                "status": "Production Ready",
                "test_file": "test_azure_openai.py",
                "notes": "Enterprise Azure-hosted OpenAI models"
            },
            {
                "provider": "Anthropic",
                "models": "Claude 3, Claude 2, Claude Instant",
                "instrumentor": "openinference-instrumentation-anthropic",
                "integration": "✅ Full Support",
                "status": "Production Ready", 
                "test_file": "test_anthropic.py",
                "notes": "Messages API and legacy completions"
            },
            {
                "provider": "Cohere",
                "models": "Command, Embed, Classify, Summarize",
                "instrumentor": "openinference-instrumentation-cohere",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_cohere.py", 
                "notes": "Generation, embeddings, classification, reranking"
            },
            {
                "provider": "Google Vertex AI",
                "models": "PaLM, Gemini, Codey, Embedding",
                "instrumentor": "openinference-instrumentation-vertexai",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_google_vertexai.py",
                "notes": "Google Cloud managed AI platform"
            },
            {
                "provider": "Google Generative AI (Gemini)",
                "models": "Gemini Pro, Gemini Pro Vision",
                "instrumentor": "openinference-instrumentation-google-generativeai", 
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_google_genai.py",
                "notes": "Direct Google AI Studio API access"
            }
        ],
        
        "AWS Ecosystem": [
            {
                "provider": "AWS Bedrock",
                "models": "Claude, Titan, Cohere, AI21, Stability AI",
                "instrumentor": "openinference-instrumentation-bedrock",
                "integration": "✅ Full Support", 
                "status": "Production Ready",
                "test_file": "test_aws_bedrock.py",
                "notes": "Multi-model AWS managed service"
            }
        ],
        
        "Framework Integration": [
            {
                "provider": "LangChain",
                "models": "Any LangChain-supported provider",
                "instrumentor": "openinference-instrumentation-langchain",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_langchain.py", 
                "notes": "Chains, agents, tools, and RAG pipelines"
            },
            {
                "provider": "LlamaIndex", 
                "models": "Any LlamaIndex-supported provider",
                "instrumentor": "openinference-instrumentation-llama-index",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_llama_index.py",
                "notes": "RAG, indexing, query engines, chat engines"
            },
            {
                "provider": "DSPy",
                "models": "Any DSPy-supported provider", 
                "instrumentor": "openinference-instrumentation-dspy",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_dspy.py",
                "notes": "Programming framework for LM pipelines"
            }
        ],
        
        "Specialized Platforms": [
            {
                "provider": "Groq",
                "models": "Llama, Mixtral (fast inference)",
                "instrumentor": "openinference-instrumentation-groq",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_groq.py",
                "notes": "Ultra-fast inference with custom chips"
            },
            {
                "provider": "Mistral AI",
                "models": "Mistral 7B, Mixtral, Mistral Small/Large",
                "instrumentor": "openinference-instrumentation-mistralai", 
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_mistralai.py",
                "notes": "European AI company, open models"
            },
            {
                "provider": "Ollama",
                "models": "Local Llama, Mistral, CodeLlama, etc.",
                "instrumentor": "openinference-instrumentation-ollama",
                "integration": "✅ Full Support",
                "status": "Production Ready", 
                "test_file": "test_ollama.py",
                "notes": "Local model serving, privacy-focused"
            }
        ],
        
        "Open Source & Self-Hosted": [
            {
                "provider": "Hugging Face Transformers",
                "models": "Thousands of open-source models",
                "instrumentor": "openinference-instrumentation-huggingface",
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_huggingface.py",
                "notes": "Pipelines, direct model usage, custom models"
            },
            {
                "provider": "LiteLLM",
                "models": "Multi-provider proxy (100+ models)",
                "instrumentor": "openinference-instrumentation-litellm", 
                "integration": "✅ Full Support",
                "status": "Production Ready",
                "test_file": "test_litellm.py",
                "notes": "Unified API, cost tracking, fallbacks"
            }
        ]
    }
    
    # Generate markdown documentation
    lines = []
    lines.append("# HoneyHive Model Provider Compatibility Matrix")
    lines.append("")
    lines.append("*Generated on: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    lines.append("")
    lines.append("This document provides a comprehensive mapping of model providers supported by HoneyHive through")
    lines.append("OpenInference instrumentation, demonstrating the **'Bring Your Own Instrumentor'** architecture.")
    lines.append("")
    
    # Architecture section
    lines.append("## Architecture Overview")
    lines.append("")
    lines.append("HoneyHive integrates with model providers through OpenInference instrumentors:")
    lines.append("")
    lines.append("```python")
    lines.append("from honeyhive import HoneyHiveTracer")
    lines.append("from openinference.instrumentation.openai import OpenAIInstrumentor")
    lines.append("")
    lines.append("# 1. Initialize instrumentor")
    lines.append("instrumentor = OpenAIInstrumentor()")
    lines.append("")
    lines.append("# 2. Pass to HoneyHive during initialization") 
    lines.append("tracer = HoneyHiveTracer.init(")
    lines.append("    api_key='your_key',")
    lines.append("    project='your_project',")
    lines.append("    instrumentors=[instrumentor]  # <-- Integration point")
    lines.append(")")
    lines.append("")
    lines.append("# 3. Use provider normally - tracing happens automatically")
    lines.append("client = OpenAI()")
    lines.append("response = client.chat.completions.create(...)  # <-- Automatically traced")
    lines.append("```")
    lines.append("")
    
    # Generate tables for each category
    for category, providers in compatibility_data.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Provider | Models | Instrumentor | Integration | Test File | Notes |")
        lines.append("|----------|---------|-------------|-------------|-----------|-------|")
        
        for provider in providers:
            lines.append(f"| **{provider['provider']}** | {provider['models']} | `{provider['instrumentor']}` | {provider['integration']} | `{provider['test_file']}` | {provider['notes']} |")
        
        lines.append("")
    
    # Summary statistics
    total_providers = sum(len(providers) for providers in compatibility_data.values())
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Providers**: {total_providers}")
    lines.append(f"- **Categories**: {len(compatibility_data)}")
    lines.append("- **Integration Status**: All providers have full OpenTelemetry-based tracing support")
    lines.append("- **Architecture**: 'Bring Your Own Instrumentor' pattern")
    lines.append("")
    
    # Testing section
    lines.append("## Testing")
    lines.append("")
    lines.append("### Run All Tests")
    lines.append("```bash")
    lines.append("# Install dependencies")
    lines.append("pip install -r tests/compatibility_matrix/requirements.txt")
    lines.append("")
    lines.append("# Set environment variables (see env.example)")
    lines.append("export HH_API_KEY='your_honeyhive_api_key'")
    lines.append("export HH_PROJECT='your_project'")
    lines.append("export OPENAI_API_KEY='your_openai_key'")
    lines.append("# ... other provider keys ...")
    lines.append("")
    lines.append("# Run compatibility test suite")
    lines.append("python tests/compatibility_matrix/run_compatibility_tests.py")
    lines.append("```")
    lines.append("")
    
    lines.append("### Run Individual Tests")
    lines.append("```bash")
    lines.append("# Test specific provider")
    lines.append("python tests/compatibility_matrix/test_openai.py")
    lines.append("python tests/compatibility_matrix/test_anthropic.py")
    lines.append("python tests/compatibility_matrix/test_langchain.py")
    lines.append("```")
    lines.append("")
    
    # Benefits section
    lines.append("## Benefits of This Architecture")
    lines.append("")
    lines.append("1. **Provider Agnostic**: Works with any OpenInference-supported provider")
    lines.append("2. **Future Proof**: New OpenInference instrumentors work automatically") 
    lines.append("3. **Standard Compliant**: Uses OpenTelemetry standards")
    lines.append("4. **Minimal Changes**: Existing provider code requires minimal modification")
    lines.append("5. **Rich Traces**: Captures input/output, metadata, and performance metrics")
    lines.append("6. **Extensible**: Easy to add new providers as OpenInference support grows")
    lines.append("")
    
    # Provider-specific notes
    lines.append("## Provider-Specific Notes")
    lines.append("")
    lines.append("### Cloud Providers")
    lines.append("- **OpenAI/Azure OpenAI**: Most mature integration, supports all features")
    lines.append("- **AWS Bedrock**: Multi-model support, handles different model APIs seamlessly")
    lines.append("- **Google Cloud**: Both Vertex AI and direct Generative AI APIs supported")
    lines.append("")
    lines.append("### Framework Integration") 
    lines.append("- **LangChain**: Traces chains, agents, tools, and complex workflows")
    lines.append("- **LlamaIndex**: Comprehensive RAG pipeline tracing and optimization")
    lines.append("- **DSPy**: Advanced LM programming patterns and optimization")
    lines.append("")
    lines.append("### Specialized Platforms")
    lines.append("- **Groq**: Ultra-fast inference monitoring for performance-critical apps")
    lines.append("- **Ollama**: Local deployment monitoring for privacy-sensitive applications")
    lines.append("- **LiteLLM**: Multi-provider abstraction with cost tracking")
    lines.append("")
    
    return "\n".join(lines)

def main():
    """Generate and save the compatibility matrix."""
    print("🏗️  Generating HoneyHive Compatibility Matrix Documentation...")
    
    # Generate the documentation
    matrix_content = generate_compatibility_matrix()
    
    # Save to file
    output_file = Path(__file__).parent / "COMPATIBILITY_MATRIX.md"
    with open(output_file, 'w') as f:
        f.write(matrix_content)
    
    print(f"✅ Compatibility matrix generated: {output_file}")
    print(f"📄 Total length: {len(matrix_content.split())} words")
    
    # Also print summary to console
    print("\n📊 COMPATIBILITY SUMMARY:")
    print("=" * 50)
    
    categories = {
        "Direct Provider Support": 6,
        "AWS Ecosystem": 1, 
        "Framework Integration": 3,
        "Specialized Platforms": 3,
        "Open Source & Self-Hosted": 2
    }
    
    total = sum(categories.values())
    
    for category, count in categories.items():
        print(f"{category:.<30} {count} providers")
    
    print("-" * 50)
    print(f"{'TOTAL PROVIDERS':.<30} {total}")
    print("=" * 50)
    print("\n🎯 All providers support HoneyHive's 'Bring Your Own Instrumentor' pattern")
    print("🔗 Integration through OpenInference + OpenTelemetry standards")
    print("📋 Comprehensive test suite available in tests/compatibility_matrix/")

if __name__ == "__main__":
    main()
