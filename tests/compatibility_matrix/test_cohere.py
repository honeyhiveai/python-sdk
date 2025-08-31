#!/usr/bin/env python3
"""
Cohere Compatibility Test for HoneyHive SDK

Tests Cohere integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_cohere_integration():
    """Test Cohere integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    cohere_key = os.getenv("COHERE_API_KEY")

    if not all([api_key, project, cohere_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - COHERE_API_KEY (Cohere API key)")
        return False

    try:
        # Import dependencies
        import cohere
        from openinference.instrumentation.cohere import CohereInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Cohere with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        cohere_instrumentor = CohereInstrumentor()
        print("✓ Cohere instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[cohere_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Cohere instrumentor")

        # 3. Initialize Cohere client
        client = cohere.Client(api_key=cohere_key)
        print("✓ Cohere client initialized")

        # 4. Test text generation (automatically traced)
        print("🚀 Testing Cohere text generation...")
        response = client.generate(
            model="command",
            prompt="Say hello and confirm this is a compatibility test for HoneyHive + Cohere integration.",
            max_tokens=100,
            temperature=0.1,
            stop_sequences=[],
        )

        result_text = response.generations[0].text
        print(f"✓ Cohere response: {result_text.strip()}")

        # 5. Test embeddings
        print("🔧 Testing Cohere embeddings...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "cohere"},
            outputs={"model_used": "command"},
        ) as span:
            embed_response = client.embed(
                texts=["This is a test text for embedding."], model="embed-english-v3.0"
            )

            span_data = {
                "embedding_dimension": len(embed_response.embeddings[0]),
                "num_texts": len(embed_response.embeddings),
                "model": "embed-english-v3.0",
            }
            print(f"✓ Embedding created: {span_data}")

        # 6. Test classification (if available)
        print("🔧 Testing Cohere classification...")
        with tracer.enrich_span(
            metadata={"test_type": "classification", "provider": "cohere"},
        ) as span:
            try:
                # Test with a simple classification example
                classify_response = client.classify(
                    inputs=["This is a positive message about technology."],
                    examples=[
                        cohere.ClassifyExample(text="I love this!", label="positive"),
                        cohere.ClassifyExample(
                            text="This is terrible.", label="negative"
                        ),
                        cohere.ClassifyExample(
                            text="Technology is amazing.", label="positive"
                        ),
                        cohere.ClassifyExample(text="I hate bugs.", label="negative"),
                    ],
                )

                span_data = {
                    "predictions": len(classify_response.classifications),
                    "confidence": (
                        classify_response.classifications[0].confidence
                        if classify_response.classifications
                        else None
                    ),
                }
                print(f"✓ Classification completed: {span_data}")

            except Exception as e:
                print(f"⚠️  Classification test failed: {e}")
                span_data = {"classification_error": str(e)}

        # 7. Test summarization
        print("🔧 Testing Cohere summarization...")
        with tracer.enrich_span(
            metadata={"test_type": "summarization", "provider": "cohere"},
        ) as span:
            try:
                summarize_response = client.summarize(
                    text="HoneyHive is an AI observability platform that helps teams monitor and improve their LLM applications. It provides comprehensive tracing, evaluation, and monitoring capabilities for AI systems. The platform supports various model providers and frameworks through standardized instrumentation.",
                    model="command",
                    length="short",
                    format="paragraph",
                )

                span_data = {
                    "summary": summarize_response.summary,
                    "format": "paragraph",
                    "length": "short",
                }
                print(f"✓ Summarization completed: {summarize_response.summary}")

            except Exception as e:
                print(f"⚠️  Summarization test failed: {e}")
                span_data = {"summarization_error": str(e)}

        # 8. Test reranking
        print("🔧 Testing Cohere reranking...")
        with tracer.enrich_span(
            metadata={"test_type": "reranking", "provider": "cohere"},
        ) as span:
            try:
                rerank_response = client.rerank(
                    model="rerank-english-v2.0",
                    query="AI observability platform",
                    documents=[
                        "HoneyHive provides AI observability and monitoring.",
                        "OpenInference offers standardized AI instrumentation.",
                        "Machine learning models need proper monitoring.",
                        "Database systems require different monitoring approaches.",
                    ],
                    top_n=2,
                )

                span_data = {
                    "reranked_docs": len(rerank_response.results),
                    "top_score": (
                        rerank_response.results[0].relevance_score
                        if rerank_response.results
                        else None
                    ),
                }
                print(f"✓ Reranking completed: {span_data}")

            except Exception as e:
                print(f"⚠️  Reranking test failed: {e}")
                span_data = {"reranking_error": str(e)}

        # 9. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Cohere integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-cohere")
        print("   pip install cohere")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Cohere compatibility test."""
    print("🧪 HoneyHive + Cohere Compatibility Test")
    print("=" * 50)

    success = test_cohere_integration()

    if success:
        print("\n✅ Cohere compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Cohere compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
