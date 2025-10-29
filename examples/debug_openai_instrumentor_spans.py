#!/usr/bin/env python3
"""
Debug script for OpenAI Instrumentor span issues with HoneyHive tracer.

This script reproduces the customer's setup to diagnose:
1. Dropped/incomplete spans
2. enrich_span functionality issues
3. Decorator vs manual tracing behavior

Run with: python examples/debug_openai_instrumentor_spans.py

To extract span content from logs:
  grep -A 20 "Sending event" output.log | grep -E "(event_type|event_name|inputs|outputs|metrics|error)"
  
Or for full span data:
  grep -B 5 -A 50 "Sending event" output.log
"""

import os
import sys
from typing import Optional, TYPE_CHECKING
from openai import OpenAI
from honeyhive import HoneyHiveTracer, trace, enrich_span, flush
from openinference.instrumentation.openai import OpenAIInstrumentor
from dotenv import load_dotenv

if TYPE_CHECKING:
    from honeyhive.tracer.core.base import HoneyHiveTracerBase

# Load environment variables - try .env.dotenv first, then .env
load_dotenv('.env.dotenv')
load_dotenv()  # Fallback to .env

# Configuration - support both HH_* and HONEYHIVE_* variable names
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HH_API_KEY = os.getenv('HONEYHIVE_API_KEY') or os.getenv('HH_API_KEY')
HH_PROJECT = os.getenv('HONEYHIVE_PROJECT') or os.getenv('HH_PROJECT') or 'debug-project'
HH_SERVER_URL = os.getenv('HONEYHIVE_SERVER_URL') or os.getenv('HH_API_URL')

# Verify required environment variables
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set in environment")
    sys.exit(1)
if not HH_API_KEY:
    print("ERROR: HONEYHIVE_API_KEY not set in environment")
    sys.exit(1)


def init_honeyhive_tracer(session_name: str):
    """Initialize HoneyHive tracer with verbose logging enabled."""
    print(f"\n{'='*80}")
    print(f"INITIALIZING HONEYHIVE TRACER")
    print(f"{'='*80}")
    print(f"Project: {HH_PROJECT}")
    print(f"Session: {session_name}")
    print(f"Server URL: {HH_SERVER_URL or 'default'}")
    print(f"Verbose: True")
    print(f"{'='*80}\n")
    
    tracer = HoneyHiveTracer.init(
        api_key=HH_API_KEY,
        project=HH_PROJECT,
        source='debug',
        session_name=session_name,
        server_url=HH_SERVER_URL,
        verbose=True  # CRITICAL: Enable verbose logging
    )
    
    return tracer


def instrument_openai(tracer):
    """Initialize OpenAI instrumentor with tracer provider."""
    print(f"\n{'='*80}")
    print(f"INSTRUMENTING OPENAI")
    print(f"{'='*80}")
    print(f"Using tracer provider: {tracer.provider}")
    print(f"{'='*80}\n")
    
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)
    return instrumentor


# Test 1: Decorator-based tracing
@trace()
def test_decorator_simple_call(query: str) -> Optional[str]:
    """Test basic decorator tracing with auto-instrumented OpenAI call."""
    print(f"\n[TEST 1] Decorator-based tracing: {query}")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"[TEST 1] Response: {result}")
    
    # Try enrich_span - this should enrich the current span
    print(f"[TEST 1] Attempting enrich_span...")
    success = enrich_span(
        attributes={
            'custom_metric': 0.95,
            'honeyhive_metrics.quality_score': 0.85
        }
    )
    print(f"[TEST 1] enrich_span result: {success}")
    
    return result


# Test 2: Decorator with span enrichment
@trace()
def test_decorator_with_span_enrichment(query: str) -> Optional[str]:
    """Test decorator tracing with span enrichment."""
    print(f"\n[TEST 2] Decorator + enrich_span (multiple calls): {query}")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"[TEST 2] Response: {result}")
    
    # Enrich span multiple times with different attributes
    print(f"[TEST 2] Attempting enrich_span (call 1)...")
    success1 = enrich_span(
        attributes={
            'session_metric_1': 3.0,
            'session_metric_2': 6.0,
            'honeyhive_metrics.bleu_score': 3.0,
            'honeyhive_metrics.embed_score': 6.0,
        }
    )
    print(f"[TEST 2] enrich_span result (call 1): {success1}")
    
    # Also try enrich_span again
    print(f"[TEST 2] Attempting enrich_span (call 2)...")
    success2 = enrich_span(
        attributes={
            'span_level_metric': 0.75,
            'honeyhive_metrics.response_quality': 0.90
        }
    )
    print(f"[TEST 2] enrich_span result (call 2): {success2}")
    
    return result


# Test 3: Manual context manager tracing
def test_manual_tracing(query: str, tracer) -> Optional[str]:
    """Test manual tracing with nested spans."""
    print(f"\n[TEST 3] Manual tracing with nested spans: {query}")
    
    with tracer.trace("parent_operation") as parent_span:
        parent_span.set_attribute('honeyhive_inputs.query', query)
        parent_span.set_attribute('step', 'parent')
        
        # Nested span for retrieval
        with tracer.trace("retrieval_step") as retrieval_span:
            retrieval_span.set_attribute('honeyhive_inputs.query', query)
            retrieval_span.set_attribute('step', 'retrieval')
            
            # Simulate retrieval
            docs = [
                f"Document 1 about {query}",
                f"Document 2 related to {query}"
            ]
            
            retrieval_span.set_attribute('honeyhive_outputs.retrieved_docs', docs)
            retrieval_span.set_attribute('honeyhive_metrics.num_docs', len(docs))
            print(f"[TEST 3] Retrieved {len(docs)} documents")
        
        # Nested span for generation
        with tracer.trace("generation_step") as generation_span:
            generation_span.set_attribute('honeyhive_inputs.query', query)
            generation_span.set_attribute('honeyhive_inputs.retrieved_docs', docs)
            generation_span.set_attribute('step', 'generation')
            
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Given these docs: {docs}\n\nAnswer: {query}"}
                ],
                max_tokens=50
            )
            
            result = response.choices[0].message.content
            generation_span.set_attribute('honeyhive_outputs.response', result)
            if result:
                generation_span.set_attribute('honeyhive_metrics.response_length', len(result))
            print(f"[TEST 3] Generated response: {result}")
            
            # Try enrich_span within nested context
            print(f"[TEST 3] Attempting enrich_span in nested context...")
            success = enrich_span(
                attributes={
                    'nested_metric': 0.88,
                    'honeyhive_metrics.generation_quality': 0.92
                }
            )
            print(f"[TEST 3] enrich_span result: {success}")
        
        parent_span.set_attribute('honeyhive_outputs.final_result', result)
        parent_span.set_attribute('honeyhive_metrics.total_steps', 2)
        
        return result


# Test 4: Multiple sequential calls
@trace()
def test_multiple_sequential_calls(queries: list) -> list:
    """Test multiple sequential OpenAI calls within one span."""
    print(f"\n[TEST 4] Multiple sequential calls: {len(queries)} queries")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    results = []
    
    for i, query in enumerate(queries):
        print(f"[TEST 4] Processing query {i+1}/{len(queries)}: {query}")
        
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=30
        )
        
        result = response.choices[0].message.content
        if result:
            results.append(result)
            print(f"[TEST 4] Response {i+1}: {result}")
        else:
            print(f"[TEST 4] Response {i+1}: <empty>")
    
    # Enrich with aggregated metrics
    print(f"[TEST 4] Attempting enrich_span with aggregated metrics...")
    avg_length = sum(len(r) for r in results) / len(results) if results else 0.0
    success = enrich_span(
        attributes={
            'total_calls': len(queries),
            'honeyhive_metrics.avg_response_length': avg_length
        }
    )
    print(f"[TEST 4] enrich_span result: {success}")
    
    return results


def main():
    """Run all debug tests."""
    print(f"\n{'#'*80}")
    print(f"# OPENAI INSTRUMENTOR SPAN DEBUG SCRIPT")
    print(f"{'#'*80}\n")
    
    # Initialize tracer
    tracer = init_honeyhive_tracer('Debug Session - OpenAI Instrumentor Spans')
    
    # Instrument OpenAI
    instrumentor = instrument_openai(tracer)
    
    try:
        # Test 1: Simple decorator
        test_decorator_simple_call("What is 2+2?")
        
        # Test 2: Decorator with span enrichment
        test_decorator_with_span_enrichment("What is the capital of France?")
        
        # Test 3: Manual tracing with nested spans
        test_manual_tracing("Explain quantum computing in simple terms", tracer)
        
        # Test 4: Multiple sequential calls
        test_multiple_sequential_calls([
            "What is AI?",
            "What is ML?",
            "What is DL?"
        ])
        
        print(f"\n{'='*80}")
        print(f"ALL TESTS COMPLETED")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n{'!'*80}")
        print(f"ERROR OCCURRED: {e}")
        print(f"{'!'*80}\n")
        import traceback
        traceback.print_exc()
    
    finally:
        # Flush tracer to ensure all spans are sent
        print(f"\n{'='*80}")
        print(f"FLUSHING TRACER")
        print(f"{'='*80}\n")
        flush(tracer)
        
        # Uninstrument to clean up
        instrumentor.uninstrument()


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    HONEYHIVE DEBUG SCRIPT                                  ║
║                                                                            ║
║ This script tests OpenAI Instrumentor integration with HoneyHive tracer   ║
║ to diagnose span issues.                                                  ║
║                                                                            ║
║ REQUIRED ENVIRONMENT VARIABLES:                                            ║
║   - OPENAI_API_KEY                                                        ║
║   - HONEYHIVE_API_KEY                                                     ║
║   - HONEYHIVE_PROJECT (optional, defaults to 'debug-project')            ║
║                                                                            ║
║ GREP COMMANDS TO EXTRACT SPAN DATA:                                       ║
║                                                                            ║
║   1. See all events being sent:                                           ║
║      grep "Sending event" output.log                                      ║
║                                                                            ║
║   2. Extract span content summary:                                        ║
║      grep -A 20 "Sending event" output.log | grep -E \\                   ║
║        "(event_type|event_name|inputs|outputs|metrics|error)"            ║
║                                                                            ║
║   3. Full span details with context:                                      ║
║      grep -B 5 -A 50 "Sending event" output.log                          ║
║                                                                            ║
║   4. Extract only HoneyHive-specific attributes:                          ║
║      grep -E "honeyhive_(inputs|outputs|metrics)" output.log             ║
║                                                                            ║
║   5. See tracer state and flush info:                                     ║
║      grep -E "(INITIALIZING|INSTRUMENTING|FLUSHING)" output.log          ║
║                                                                            ║
║   6. Filter by test number:                                               ║
║      grep "\\[TEST 1\\]" output.log                                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    main()

