#!/usr/bin/env python3
"""
Enriching Traces Tutorial - Test Script

Tests the code examples from tutorials/enriching-traces.mdx
"""

import os
from dotenv import load_dotenv
from honeyhive import HoneyHiveTracer, enrich_span, trace
from openinference.instrumentation import using_attributes
from openinference.instrumentation.openai import OpenAIInstrumentor
import openai

load_dotenv()


def main():
    """Run tutorial examples."""
    print("Enriching Traces Tutorial")
    print("=" * 50)
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY required")
        return
    
    # Initialize tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.environ.get("HH_API_KEY"),
        project=os.environ.get("HH_PROJECT", "enrichment-tutorial"),
        source="enrichment-tutorial"
    )
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    # Session context (applies to all traces)
    tracer.enrich_session({
        "tenant_id": "acme_corp",
        "user_tier": "enterprise",
        "app_version": "2.1.0"
    })
    
    client = openai.OpenAI()
    
    # Option 1: using_attributes - enrich LLM spans directly
    print("\n--- Option 1: using_attributes ---")
    print("(Enriches LLM span directly, no parent span)")
    
    with using_attributes(
        session_id="session_123",
        user_id="user_oi_123",
        metadata={"feature": "chat_support", "custom_key": "custom_value"},
        tags=["tutorial", "test"]
    ):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(f"Response: {response.choices[0].message.content}")
    
    # Option 2: @trace + enrich_span() - create parent span for pipeline
    def retrieve_documents(question: str) -> str:
        """Simulate document retrieval."""
        return "Our refund policy allows returns within 30 days."
    
    def save_to_history(user_id: str, question: str, answer: str):
        """Simulate saving to history."""
        pass
    
    @trace
    def answer_question(question: str, user_id: str) -> str:
        enrich_span({
            "user_id": user_id,
            "feature": "qa_pipeline"
        })
        
        # Step 1: Retrieve relevant context
        context = retrieve_documents(question)
        
        # Step 2: Generate answer with context
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Context: {context}"},
                {"role": "user", "content": question}
            ]
        )
        
        # Step 3: Log the answer
        answer = response.choices[0].message.content
        save_to_history(user_id, question, answer)
        
        return answer
    
    print("\n--- Option 2: @trace + enrich_span() ---")
    print("(Creates parent span for pipeline)")
    result = answer_question("What's our refund policy?", user_id="user_123")
    print(f"Response: {result}")
    
    print("\n" + "=" * 50)
    print("✅ Done! Check traces at app.honeyhive.ai")
    print("\nOption 1: ChatCompletion has session_id, user_id, metadata, tags")
    print("Option 2: Parent 'answer_question' span groups retrieval + LLM + logging")
    print("Both: Session metadata (tenant_id, user_tier, app_version) on all traces")


if __name__ == "__main__":
    main()
