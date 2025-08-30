#!/usr/bin/env python3
"""
Ollama Compatibility Test for HoneyHive SDK

Tests Ollama integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional

def test_ollama_integration():
    """Test Ollama integration with HoneyHive via OpenInference instrumentation."""
    
    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
    
    if not all([api_key, project]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - OLLAMA_BASE_URL (optional, defaults to http://localhost:11434)")
        print("   - OLLAMA_MODEL (optional, defaults to llama2)")
        return False
    
    try:
        # Import dependencies
        from honeyhive import HoneyHiveTracer
        from openinference.instrumentation.ollama import OllamaInstrumentor
        import ollama
        
        print("🔧 Setting up Ollama with HoneyHive integration...")
        
        # 1. Initialize OpenInference instrumentor
        ollama_instrumentor = OllamaInstrumentor()
        print("✓ Ollama instrumentor initialized")
        
        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[ollama_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test"
        )
        print("✓ HoneyHive tracer initialized with Ollama instrumentor")
        
        # 3. Configure Ollama client
        client = ollama.Client(host=ollama_base_url)
        print(f"✓ Ollama client initialized (host: {ollama_base_url})")
        
        # 4. Check if Ollama is running and model is available
        print("🔍 Checking Ollama status...")
        try:
            models = client.list()
            available_models = [model['name'] for model in models['models']]
            print(f"✓ Available models: {available_models}")
            
            if ollama_model not in available_models:
                print(f"⚠️  Model '{ollama_model}' not found. Attempting to pull...")
                client.pull(ollama_model)
                print(f"✓ Model '{ollama_model}' pulled successfully")
            
        except Exception as e:
            print(f"❌ Ollama server not running or error: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            print(f"💡 Pull the model: ollama pull {ollama_model}")
            return False
        
        # 5. Test chat completion (automatically traced)
        print("🚀 Testing Ollama chat completion...")
        response = client.chat(
            model=ollama_model,
            messages=[
                {
                    'role': 'user',
                    'content': 'Say hello and confirm this is a compatibility test for HoneyHive + Ollama integration. Keep it brief.'
                }
            ]
        )
        
        result_text = response['message']['content']
        print(f"✓ Ollama response: {result_text}")
        
        # 6. Test generation (automatically traced)
        print("🔧 Testing Ollama generation...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "ollama"},
            outputs={"model_used": ollama_model},
        ) as span:
            generation_response = client.generate(
                model=ollama_model,
                prompt="What is 2+2? Answer briefly."
            )
            
            span_data = {
                "model": ollama_model,
                "response": generation_response['response'],
                "done": generation_response.get('done', False)
            }
            print(f"✓ Generation response: {generation_response['response']}")
        
        # 7. Test streaming (automatically traced)
        print("🔧 Testing Ollama streaming...")
        with tracer.enrich_span(
            metadata={"test_type": "streaming", "provider": "ollama"},
        ) as span:
            stream_response = client.chat(
                model=ollama_model,
                messages=[
                    {'role': 'user', 'content': 'Count from 1 to 3.'}
                ],
                stream=True
            )
            
            streamed_content = ""
            chunk_count = 0
            for chunk in stream_response:
                if 'message' in chunk and 'content' in chunk['message']:
                    streamed_content += chunk['message']['content']
                    chunk_count += 1
            
            span_data = {
                "chunks_received": chunk_count,
                "streamed_content": streamed_content.strip(),
                "streaming": True,
                "model": ollama_model
            }
            print(f"✓ Streaming completed: {chunk_count} chunks, content: {streamed_content.strip()}")
        
        # 8. Test embeddings (if supported)
        print("🔧 Testing Ollama embeddings...")
        with tracer.enrich_span(
            metadata={"test_type": "embeddings", "provider": "ollama"},
        ) as span:
            try:
                embeddings_response = client.embeddings(
                    model=ollama_model,
                    prompt="This is a test text for embedding."
                )
                
                span_data = {
                    "embedding_dimension": len(embeddings_response['embedding']),
                    "model": ollama_model
                }
                print(f"✓ Embeddings created: {span_data}")
                
            except Exception as e:
                print(f"⚠️  Embeddings test failed (model may not support embeddings): {e}")
                span_data = {"embeddings_error": str(e)}
        
        # 9. Test conversation context
        print("🔧 Testing Ollama conversation context...")
        with tracer.enrich_span(
            metadata={"test_type": "conversation", "provider": "ollama"},
        ) as span:
            conversation_response = client.chat(
                model=ollama_model,
                messages=[
                    {'role': 'user', 'content': 'I am testing AI observability.'},
                    {'role': 'assistant', 'content': 'That sounds great! Observability helps monitor AI systems.'},
                    {'role': 'user', 'content': 'What tools are commonly used for this?'}
                ]
            )
            
            span_data = {
                "conversation_length": 3,
                "response": conversation_response['message']['content'],
                "model": ollama_model
            }
            print(f"✓ Conversation response: {conversation_response['message']['content']}")
        
        # 10. Test with custom options
        print("🔧 Testing Ollama with custom options...")
        with tracer.enrich_span(
            metadata={"test_type": "custom_options", "provider": "ollama"},
        ) as span:
            try:
                custom_response = client.generate(
                    model=ollama_model,
                    prompt="Write a haiku about technology.",
                    options={
                        'temperature': 0.8,
                        'top_p': 0.9,
                        'top_k': 40
                    }
                )
                
                span_data = {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "top_k": 40,
                    "response": custom_response['response']
                }
                print(f"✓ Custom options response: {custom_response['response']}")
                
            except Exception as e:
                print(f"⚠️  Custom options test failed: {e}")
                span_data = {"custom_options_error": str(e)}
        
        # 11. Test model information
        print("🔧 Testing Ollama model information...")
        with tracer.enrich_span(
            metadata={"test_type": "model_info", "provider": "ollama"},
        ) as span:
            try:
                model_info = client.show(ollama_model)
                
                span_data = {
                    "model_name": model_info.get('details', {}).get('family', 'unknown'),
                    "parameter_size": model_info.get('details', {}).get('parameter_size', 'unknown'),
                    "quantization_level": model_info.get('details', {}).get('quantization_level', 'unknown')
                }
                print(f"✓ Model info retrieved: {span_data}")
                
            except Exception as e:
                print(f"⚠️  Model info test failed: {e}")
                span_data = {"model_info_error": str(e)}
        
        # 12. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")
        
        print("🎉 Ollama integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-ollama")
        print("   pip install ollama")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the Ollama compatibility test."""
    print("🧪 HoneyHive + Ollama Compatibility Test")
    print("=" * 50)
    
    success = test_ollama_integration()
    
    if success:
        print("\n✅ Ollama compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Ollama compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
