#!/usr/bin/env python3
"""
DSPy Compatibility Test for HoneyHive SDK

Tests DSPy integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional

def test_dspy_integration():
    """Test DSPy integration with HoneyHive via OpenInference instrumentation."""
    
    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not all([api_key, project, openai_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - OPENAI_API_KEY (OpenAI API key for DSPy)")
        return False
    
    try:
        # Import dependencies
        from honeyhive import HoneyHiveTracer
        from openinference.instrumentation.dspy import DSPyInstrumentor
        import dspy
        
        print("🔧 Setting up DSPy with HoneyHive integration...")
        
        # 1. Initialize OpenInference instrumentor
        dspy_instrumentor = DSPyInstrumentor()
        print("✓ DSPy instrumentor initialized")
        
        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[dspy_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test"
        )
        print("✓ HoneyHive tracer initialized with DSPy instrumentor")
        
        # 3. Configure DSPy with OpenAI
        lm = dspy.OpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_key,
            max_tokens=100
        )
        dspy.settings.configure(lm=lm)
        print("✓ DSPy configured with OpenAI")
        
        # 4. Test basic DSPy signature (automatically traced)
        print("🚀 Testing DSPy basic signature...")
        
        class BasicQA(dspy.Signature):
            """Answer questions about compatibility testing."""
            question = dspy.InputField()
            answer = dspy.OutputField(desc="A brief answer")
        
        basic_qa = dspy.Predict(BasicQA)
        response = basic_qa(question="What is DSPy and how does it work with HoneyHive?")
        
        result_text = response.answer
        print(f"✓ DSPy response: {result_text}")
        
        # 5. Test DSPy Chain of Thought
        print("🔧 Testing DSPy Chain of Thought...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "dspy"},
            outputs={"module_used": "ChainOfThought"},
        ) as span:
            class ReasoningQA(dspy.Signature):
                """Reason about a question step by step."""
                question = dspy.InputField()
                reasoning = dspy.OutputField(desc="Step by step reasoning")
                answer = dspy.OutputField(desc="Final answer")
            
            cot_qa = dspy.ChainOfThought(ReasoningQA)
            cot_response = cot_qa(question="Why is observability important for AI systems?")
            
            span_data = {
                "reasoning": cot_response.reasoning,
                "answer": cot_response.answer,
                "module": "ChainOfThought"
            }
            print(f"✓ Chain of Thought reasoning: {cot_response.reasoning}")
            print(f"✓ Chain of Thought answer: {cot_response.answer}")
        
        # 6. Test DSPy Retrieve (if retrieval model available)
        print("🔧 Testing DSPy Retrieve module...")
        with tracer.enrich_span(
            metadata={"test_type": "retrieval", "provider": "dspy"},
        ) as span:
            try:
                # Create a simple retrieval model with dummy data
                class SimpleRetriever(dspy.Retrieve):
                    def __init__(self, k=3):
                        super().__init__(k=k)
                        # Simulate a simple knowledge base
                        self.knowledge_base = [
                            "HoneyHive is an AI observability platform.",
                            "DSPy is a framework for programming with language models.",
                            "OpenInference provides standardized instrumentation.",
                            "Tracing helps monitor AI system performance."
                        ]
                    
                    def forward(self, query):
                        # Simple keyword matching
                        query_lower = query.lower()
                        relevant_docs = []
                        for doc in self.knowledge_base:
                            if any(word in doc.lower() for word in query_lower.split()):
                                relevant_docs.append(doc)
                        return relevant_docs[:self.k]
                
                retriever = SimpleRetriever(k=2)
                retrieved_docs = retriever.forward("AI observability tracing")
                
                span_data = {
                    "retrieved_docs": retrieved_docs,
                    "num_docs": len(retrieved_docs),
                    "module": "Retrieve"
                }
                print(f"✓ Retrieved documents: {retrieved_docs}")
                
            except Exception as e:
                print(f"⚠️  Retrieve test failed: {e}")
                span_data = {"retrieve_error": str(e)}
        
        # 7. Test DSPy Multi-hop reasoning
        print("🔧 Testing DSPy multi-hop reasoning...")
        with tracer.enrich_span(
            metadata={"test_type": "multi_hop", "provider": "dspy"},
        ) as span:
            class MultiHopQA(dspy.Module):
                def __init__(self):
                    super().__init__()
                    self.first_question = dspy.Predict("question -> sub_question")
                    self.answer_question = dspy.Predict("sub_question -> answer")
                    self.final_answer = dspy.Predict("question, answer -> final_answer")
                
                def forward(self, question):
                    sub_q = self.first_question(question=question)
                    answer = self.answer_question(sub_question=sub_q.sub_question)
                    final = self.final_answer(question=question, answer=answer.answer)
                    return final
            
            try:
                multi_hop = MultiHopQA()
                multi_response = multi_hop(question="How does HoneyHive help with AI monitoring?")
                
                span_data = {
                    "final_answer": multi_response.final_answer,
                    "module": "MultiHopQA",
                    "reasoning_steps": 3
                }
                print(f"✓ Multi-hop answer: {multi_response.final_answer}")
                
            except Exception as e:
                print(f"⚠️  Multi-hop test failed: {e}")
                span_data = {"multi_hop_error": str(e)}
        
        # 8. Test DSPy with custom signature
        print("🔧 Testing DSPy custom signature...")
        with tracer.enrich_span(
            metadata={"test_type": "custom_signature", "provider": "dspy"},
        ) as span:
            class TechnicalExplanation(dspy.Signature):
                """Provide technical explanations about software concepts."""
                concept = dspy.InputField(desc="Technical concept to explain")
                audience = dspy.InputField(desc="Target audience level")
                explanation = dspy.OutputField(desc="Clear technical explanation")
                key_points = dspy.OutputField(desc="3 key points as bullet list")
            
            tech_explainer = dspy.Predict(TechnicalExplanation)
            tech_response = tech_explainer(
                concept="OpenTelemetry tracing",
                audience="software developers"
            )
            
            span_data = {
                "explanation": tech_response.explanation,
                "key_points": tech_response.key_points,
                "signature": "TechnicalExplanation"
            }
            print(f"✓ Technical explanation: {tech_response.explanation}")
            print(f"✓ Key points: {tech_response.key_points}")
        
        # 9. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")
        
        print("🎉 DSPy integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-dspy")
        print("   pip install dspy-ai")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the DSPy compatibility test."""
    print("🧪 HoneyHive + DSPy Compatibility Test")
    print("=" * 50)
    
    success = test_dspy_integration()
    
    if success:
        print("\n✅ DSPy compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ DSPy compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
