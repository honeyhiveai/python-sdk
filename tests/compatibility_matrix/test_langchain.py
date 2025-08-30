#!/usr/bin/env python3
"""
LangChain Compatibility Test for HoneyHive SDK

Tests LangChain integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional

def test_langchain_integration():
    """Test LangChain integration with HoneyHive via OpenInference instrumentation."""
    
    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not all([api_key, project, openai_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - OPENAI_API_KEY (OpenAI API key for LangChain)")
        return False
    
    try:
        # Import dependencies
        from honeyhive import HoneyHiveTracer
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        
        print("🔧 Setting up LangChain with HoneyHive integration...")
        
        # 1. Initialize OpenInference instrumentor
        langchain_instrumentor = LangChainInstrumentor()
        print("✓ LangChain instrumentor initialized")
        
        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[langchain_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test"
        )
        print("✓ HoneyHive tracer initialized with LangChain instrumentor")
        
        # 3. Initialize LangChain LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=openai_key
        )
        print("✓ LangChain ChatOpenAI initialized")
        
        # 4. Test direct LLM call (automatically traced)
        print("🚀 Testing LangChain direct LLM call...")
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Say hello and confirm this is a LangChain compatibility test.")
        ]
        
        response = llm.invoke(messages)
        result_text = response.content
        print(f"✓ LangChain response: {result_text}")
        
        # 5. Test LangChain chain (automatically traced)
        print("🔧 Testing LangChain chain...")
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Write a one sentence summary about {topic}."
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "langchain"},
            outputs={"chain_type": "LLMChain"},
        ) as span:
            chain_response = chain.run(topic="artificial intelligence")
            
            span_data = {
                "chain_input": "artificial intelligence",
                "chain_output": chain_response,
                "chain_components": ["PromptTemplate", "ChatOpenAI"]
            }
            print(f"✓ Chain response: {chain_response}")
        
        # 6. Test batch processing
        print("🔧 Testing LangChain batch processing...")
        topics = ["machine learning", "natural language processing"]
        
        with tracer.enrich_span(
            metadata={"test_type": "batch", "provider": "langchain"},
        ) as span:
            batch_results = []
            for topic in topics:
                result = chain.run(topic=topic)
                batch_results.append({"topic": topic, "summary": result})
            
            span_data = {
                "batch_size": len(topics),
                "results": batch_results
            }
            print(f"✓ Batch processing completed: {len(batch_results)} results")
        
        # 7. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")
        
        print("🎉 LangChain integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-langchain")
        print("   pip install langchain langchain-openai")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the LangChain compatibility test."""
    print("🧪 HoneyHive + LangChain Compatibility Test")
    print("=" * 50)
    
    success = test_langchain_integration()
    
    if success:
        print("\n✅ LangChain compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ LangChain compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
