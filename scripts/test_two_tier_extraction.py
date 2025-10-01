"""Test two-tier extraction with multiple instrumentor/provider combinations."""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor


def test_scenario(name: str, attributes: dict, expected_instrumentor: str, expected_provider: str):
    """Test a single scenario."""
    print(f"\n{'='*80}")
    print(f"Scenario: {name}")
    print(f"{'='*80}\n")
    
    # Initialize processor
    processor = UniversalProviderProcessor(tracer_instance=None)
    
    # Test detection
    instrumentor, provider = processor._detect_instrumentor_and_provider(attributes)
    print(f"🔍 Detection Results:")
    print(f"  Instrumentor: {instrumentor} (expected: {expected_instrumentor})")
    print(f"  Provider: {provider} (expected: {expected_provider})")
    
    detection_pass = instrumentor == expected_instrumentor and provider == expected_provider
    print(f"  Status: {'✅ PASS' if detection_pass else '❌ FAIL'}")
    
    # Test extraction
    print(f"\n📤 Extraction Results:")
    result = processor.process_span_attributes(attributes)
    
    print(f"  Inputs populated: {bool(result.get('inputs', {}))}")
    print(f"  Outputs populated: {bool(result.get('outputs', {}))}")
    print(f"  Config populated: {bool(result.get('config', {}))}")
    print(f"  Metadata instrumentor: {result.get('metadata', {}).get('instrumentor', 'unknown')}")
    
    # Show key extracted fields
    print(f"\n  Key Extracted Fields:")
    print(f"    Model: {result.get('config', {}).get('model', 'N/A')}")
    print(f"    Prompt Tokens: {result.get('metadata', {}).get('prompt_tokens', 'N/A')}")
    print(f"    Completion Tokens: {result.get('metadata', {}).get('completion_tokens', 'N/A')}")
    
    return detection_pass, result


def main():
    """Run all test scenarios."""
    print("\n" + "="*80)
    print("TWO-TIER EXTRACTION TEST SUITE")
    print("Testing Instrumentor Detection + Provider-Specific Extraction")
    print("="*80)
    
    results = []
    
    # Scenario 1: Traceloop + OpenAI
    traceloop_openai_attrs = {
        "gen_ai.system": "openai",
        "gen_ai.request.model": "gpt-4",
        "gen_ai.usage.prompt_tokens": 150,
        "gen_ai.usage.completion_tokens": 200,
        "gen_ai.usage.total_tokens": 350,
        "gen_ai.response.model": "gpt-4",
        "gen_ai.request.temperature": 0.7,
        "gen_ai.request.max_tokens": 2000,
        "gen_ai.request.top_p": 0.9,
        "gen_ai.response.finish_reasons": ["stop"],
        "gen_ai.completion": "This is a test response.",
        "gen_ai.prompt": "Test prompt",
    }
    results.append(test_scenario(
        "Traceloop + OpenAI",
        traceloop_openai_attrs,
        "traceloop",
        "openai"
    ))
    
    # Scenario 2: OpenInference + OpenAI
    openinference_openai_attrs = {
        "llm.provider": "openai",
        "llm.model_name": "gpt-4",
        "llm.token_count.prompt": 120,
        "llm.token_count.completion": 180,
        "llm.token_count.total": 300,
        "llm.invocation_parameters.temperature": 0.8,
        "llm.invocation_parameters.max_tokens": 1500,
        "llm.input_messages": [
            {"role": "user", "content": "What is AI?"}
        ],
        "llm.output_messages": [
            {"role": "assistant", "content": "AI is artificial intelligence."}
        ],
    }
    results.append(test_scenario(
        "OpenInference + OpenAI",
        openinference_openai_attrs,
        "openinference",
        "openai"
    ))
    
    # Scenario 3: Traceloop + Anthropic
    traceloop_anthropic_attrs = {
        "gen_ai.system": "anthropic",
        "gen_ai.request.model": "claude-3-opus-20240229",
        "gen_ai.usage.prompt_tokens": 100,
        "gen_ai.usage.completion_tokens": 150,
        "gen_ai.response.model": "claude-3-opus-20240229",
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.max_tokens": 1024,
    }
    results.append(test_scenario(
        "Traceloop + Anthropic",
        traceloop_anthropic_attrs,
        "traceloop",
        "anthropic"
    ))
    
    # Scenario 4: OpenInference + Anthropic
    openinference_anthropic_attrs = {
        "llm.provider": "anthropic",
        "llm.model_name": "claude-3-sonnet-20240229",
        "llm.token_count.prompt": 90,
        "llm.token_count.completion": 120,
    }
    results.append(test_scenario(
        "OpenInference + Anthropic",
        openinference_anthropic_attrs,
        "openinference",
        "anthropic"
    ))
    
    # Scenario 5: OpenLit + OpenAI
    openlit_openai_attrs = {
        "openlit.provider": "openai",
        "openlit.model": "gpt-4-turbo",
        "openlit.usage.prompt_tokens": 200,
        "openlit.usage.completion_tokens": 300,
        "openlit.usage.total_tokens": 500,
        "openlit.cost.prompt_cost": 0.002,
        "openlit.cost.completion_cost": 0.006,
        "openlit.cost.total_cost": 0.008,
        "openlit.request.temperature": 0.9,
        "openlit.request.max_tokens": 2048,
        "openlit.response.finish_reason": "stop",
    }
    results.append(test_scenario(
        "OpenLit + OpenAI",
        openlit_openai_attrs,
        "openlit",
        "openai"
    ))
    
    # Scenario 6: OpenLit + Anthropic
    openlit_anthropic_attrs = {
        "openlit.provider": "anthropic",
        "openlit.model": "claude-3-haiku-20240307",
        "openlit.usage.prompt_tokens": 80,
        "openlit.usage.completion_tokens": 100,
        "openlit.usage.total_tokens": 180,
        "openlit.cost.total_cost": 0.001,
    }
    results.append(test_scenario(
        "OpenLit + Anthropic",
        openlit_anthropic_attrs,
        "openlit",
        "anthropic"
    ))
    
    # Scenario 7: OpenLit + Gemini
    openlit_gemini_attrs = {
        "openlit.provider": "google",
        "openlit.model": "gemini-1.5-pro",
        "openlit.usage.prompt_tokens": 150,
        "openlit.usage.completion_tokens": 250,
        "openlit.cost.total_cost": 0.005,
    }
    results.append(test_scenario(
        "OpenLit + Gemini",
        openlit_gemini_attrs,
        "openlit",
        "gemini"
    ))
    
    # Summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for detection_pass, _ in results if detection_pass)
    total = len(results)
    
    print(f"Detection Tests: {passed}/{total} passed")
    
    scenario_names = [
        "Traceloop+OpenAI", 
        "OpenInference+OpenAI", 
        "Traceloop+Anthropic", 
        "OpenInference+Anthropic",
        "OpenLit+OpenAI",
        "OpenLit+Anthropic",
        "OpenLit+Gemini"
    ]
    
    for i, (detection_pass, result) in enumerate(results, 1):
        scenario_name = scenario_names[i-1]
        print(f"  {i}. {scenario_name}: {'✅' if detection_pass else '❌'}")
    
    print(f"\n{'='*80}")
    if passed == total:
        print(f"🎉 ALL TESTS PASSED")
    else:
        print(f"⚠️  SOME TESTS FAILED")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
