#!/usr/bin/env python3
"""
LlamaIndex Compatibility Test for HoneyHive SDK

Tests LlamaIndex integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_llama_index_integration():
    """Test LlamaIndex integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not all([api_key, project, openai_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - OPENAI_API_KEY (OpenAI API key for LlamaIndex)")
        return False

    try:
        # Import dependencies
        from llama_index.core import Document, Settings, VectorStoreIndex
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up LlamaIndex with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        llama_index_instrumentor = LlamaIndexInstrumentor()
        print("✓ LlamaIndex instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[llama_index_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with LlamaIndex instrumentor")

        # 3. Configure LlamaIndex settings
        Settings.llm = OpenAI(model="gpt-3.5-turbo", api_key=openai_key)
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-ada-002", api_key=openai_key
        )
        print("✓ LlamaIndex settings configured")

        # 4. Create sample documents
        print("🚀 Creating sample documents...")
        documents = [
            Document(
                text="HoneyHive is an AI observability platform that helps teams monitor and improve their LLM applications."
            ),
            Document(
                text="OpenInference provides standardized instrumentation for AI applications using OpenTelemetry."
            ),
            Document(
                text="LlamaIndex is a data framework for building RAG applications with large language models."
            ),
            Document(
                text="Vector stores enable semantic search and retrieval for AI applications."
            ),
        ]
        print(f"✓ Created {len(documents)} sample documents")

        # 5. Build vector index (automatically traced)
        print("🔧 Building vector index...")
        index = VectorStoreIndex.from_documents(documents)
        print("✓ Vector index built successfully")

        # 6. Test query engine (automatically traced)
        print("🚀 Testing query engine...")
        query_engine = index.as_query_engine()

        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "llama_index"},
            outputs={"query_type": "basic_query"},
        ) as span:
            response = query_engine.query("What is HoneyHive?")

            span_data = {
                "query": "What is HoneyHive?",
                "response": str(response),
                "source_nodes": (
                    len(response.source_nodes)
                    if hasattr(response, "source_nodes")
                    else 0
                ),
            }
            print(f"✓ Query response: {response}")

        # 7. Test retriever (automatically traced)
        print("🔧 Testing retriever...")
        retriever = index.as_retriever(similarity_top_k=2)

        with tracer.enrich_span(
            metadata={"test_type": "retrieval", "provider": "llama_index"},
        ) as span:
            retrieved_nodes = retriever.retrieve("AI observability platform")

            span_data = {
                "query": "AI observability platform",
                "retrieved_count": len(retrieved_nodes),
                "top_score": retrieved_nodes[0].score if retrieved_nodes else None,
            }
            print(f"✓ Retrieved {len(retrieved_nodes)} nodes")

        # 8. Test chat engine
        print("🔧 Testing chat engine...")
        chat_engine = index.as_chat_engine()

        with tracer.enrich_span(
            metadata={"test_type": "chat", "provider": "llama_index"},
        ) as span:
            chat_response = chat_engine.chat("Explain LlamaIndex in one sentence.")

            span_data = {
                "message": "Explain LlamaIndex in one sentence.",
                "response": str(chat_response),
                "chat_history_length": (
                    len(chat_engine.chat_history)
                    if hasattr(chat_engine, "chat_history")
                    else 0
                ),
            }
            print(f"✓ Chat response: {chat_response}")

        # 9. Test with custom prompt
        print("🔧 Testing with custom prompt...")
        from llama_index.core import PromptTemplate

        custom_prompt = PromptTemplate(
            "Context information:\n{context_str}\n\n"
            "Query: {query_str}\n\n"
            "Please provide a concise answer based on the context: "
        )

        custom_query_engine = index.as_query_engine(text_qa_template=custom_prompt)

        with tracer.enrich_span(
            metadata={"test_type": "custom_prompt", "provider": "llama_index"},
        ) as span:
            custom_response = custom_query_engine.query(
                "What technologies are mentioned?"
            )

            span_data = {
                "custom_prompt": True,
                "query": "What technologies are mentioned?",
                "response": str(custom_response),
            }
            print(f"✓ Custom prompt response: {custom_response}")

        # 10. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 LlamaIndex integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-llama-index")
        print(
            "   pip install llama-index llama-index-llms-openai llama-index-embeddings-openai"
        )
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the LlamaIndex compatibility test."""
    print("🧪 HoneyHive + LlamaIndex Compatibility Test")
    print("=" * 50)

    success = test_llama_index_integration()

    if success:
        print("\n✅ LlamaIndex compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ LlamaIndex compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
