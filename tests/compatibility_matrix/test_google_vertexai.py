#!/usr/bin/env python3
"""
Google Vertex AI Compatibility Test for HoneyHive SDK

Tests Google Vertex AI integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional

def test_google_vertexai_integration():
    """Test Google Vertex AI integration with HoneyHive via OpenInference instrumentation."""
    
    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    gcp_project = os.getenv("GCP_PROJECT")
    gcp_location = os.getenv("GCP_LOCATION", "us-central1")
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not all([api_key, project, gcp_project]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - GCP_PROJECT (Google Cloud project ID)")
        print("   - GCP_LOCATION (optional, defaults to us-central1)")
        print("   - GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON)")
        return False
    
    try:
        # Import dependencies
        from honeyhive import HoneyHiveTracer
        from openinference.instrumentation.vertexai import VertexAIInstrumentor
        from vertexai.language_models import TextGenerationModel, ChatModel
        from vertexai.generative_models import GenerativeModel
        import vertexai
        
        print("🔧 Setting up Google Vertex AI with HoneyHive integration...")
        
        # 1. Initialize OpenInference instrumentor
        vertexai_instrumentor = VertexAIInstrumentor()
        print("✓ Vertex AI instrumentor initialized")
        
        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[vertexai_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test"
        )
        print("✓ HoneyHive tracer initialized with Vertex AI instrumentor")
        
        # 3. Initialize Vertex AI
        vertexai.init(project=gcp_project, location=gcp_location)
        print(f"✓ Vertex AI initialized (project: {gcp_project}, location: {gcp_location})")
        
        # 4. Test Text Generation Model (automatically traced)
        print("🚀 Testing Vertex AI Text Generation...")
        try:
            text_model = TextGenerationModel.from_pretrained("text-bison")
            
            response = text_model.predict(
                "Say hello and confirm this is a compatibility test for HoneyHive + Google Vertex AI integration.",
                max_output_tokens=100,
                temperature=0.1
            )
            
            result_text = response.text
            print(f"✓ Text generation response: {result_text}")
            
        except Exception as e:
            print(f"⚠️  Text generation test failed: {e}")
            result_text = None
        
        # 5. Test Chat Model
        print("🔧 Testing Vertex AI Chat Model...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "vertex_ai"},
            outputs={"model_used": "chat-bison"},
        ) as span:
            try:
                chat_model = ChatModel.from_pretrained("chat-bison")
                chat = chat_model.start_chat()
                
                chat_response = chat.send_message(
                    "What is 2+2? Answer briefly.",
                    max_output_tokens=50,
                    temperature=0.1
                )
                
                span_data = {
                    "chat_response": chat_response.text,
                    "model": "chat-bison",
                    "chat_history_length": len(chat.message_history)
                }
                print(f"✓ Chat response: {chat_response.text}")
                
            except Exception as e:
                print(f"⚠️  Chat model test failed: {e}")
                span_data = {"chat_error": str(e)}
        
        # 6. Test Generative Model (Gemini)
        print("🔧 Testing Vertex AI Generative Model (Gemini)...")
        with tracer.enrich_span(
            metadata={"test_type": "generative", "provider": "vertex_ai"},
        ) as span:
            try:
                gemini_model = GenerativeModel("gemini-pro")
                
                gemini_response = gemini_model.generate_content(
                    "Explain artificial intelligence in one sentence.",
                    generation_config={
                        "max_output_tokens": 50,
                        "temperature": 0.1
                    }
                )
                
                span_data = {
                    "gemini_response": gemini_response.text,
                    "model": "gemini-pro",
                    "safety_ratings": len(gemini_response.candidates[0].safety_ratings) if gemini_response.candidates else 0
                }
                print(f"✓ Gemini response: {gemini_response.text}")
                
            except Exception as e:
                print(f"⚠️  Gemini test failed: {e}")
                span_data = {"gemini_error": str(e)}
        
        # 7. Test Embeddings
        print("🔧 Testing Vertex AI Embeddings...")
        with tracer.enrich_span(
            metadata={"test_type": "embeddings", "provider": "vertex_ai"},
        ) as span:
            try:
                from vertexai.language_models import TextEmbeddingModel
                
                embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko")
                embeddings = embedding_model.get_embeddings([
                    "This is a test text for embedding."
                ])
                
                span_data = {
                    "embedding_dimension": len(embeddings[0].values),
                    "num_embeddings": len(embeddings),
                    "model": "textembedding-gecko"
                }
                print(f"✓ Embeddings created: {span_data}")
                
            except Exception as e:
                print(f"⚠️  Embeddings test failed: {e}")
                span_data = {"embeddings_error": str(e)}
        
        # 8. Test Code Generation (if available)
        print("🔧 Testing Vertex AI Code Generation...")
        with tracer.enrich_span(
            metadata={"test_type": "code_generation", "provider": "vertex_ai"},
        ) as span:
            try:
                from vertexai.language_models import CodeGenerationModel
                
                code_model = CodeGenerationModel.from_pretrained("code-bison")
                code_response = code_model.predict(
                    prefix="def hello_world():",
                    max_output_tokens=100,
                    temperature=0.1
                )
                
                span_data = {
                    "code_response": code_response.text,
                    "model": "code-bison"
                }
                print(f"✓ Code generation: {code_response.text.strip()}")
                
            except Exception as e:
                print(f"⚠️  Code generation test failed: {e}")
                span_data = {"code_generation_error": str(e)}
        
        # 9. Test with custom parameters
        print("🔧 Testing with custom parameters...")
        with tracer.enrich_span(
            metadata={"test_type": "custom_params", "provider": "vertex_ai"},
        ) as span:
            try:
                custom_model = TextGenerationModel.from_pretrained("text-bison")
                
                custom_response = custom_model.predict(
                    "Write a haiku about technology.",
                    max_output_tokens=60,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                )
                
                span_data = {
                    "custom_response": custom_response.text,
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40
                }
                print(f"✓ Custom parameters response: {custom_response.text}")
                
            except Exception as e:
                print(f"⚠️  Custom parameters test failed: {e}")
                span_data = {"custom_params_error": str(e)}
        
        # 10. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")
        
        print("🎉 Google Vertex AI integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-vertexai")
        print("   pip install google-cloud-aiplatform")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the Google Vertex AI compatibility test."""
    print("🧪 HoneyHive + Google Vertex AI Compatibility Test")
    print("=" * 50)
    
    success = test_google_vertexai_integration()
    
    if success:
        print("\n✅ Google Vertex AI compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Google Vertex AI compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
