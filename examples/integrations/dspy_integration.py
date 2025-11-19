#!/usr/bin/env python3
"""
DSPy Integration Example with HoneyHive

This example demonstrates how to integrate DSPy with HoneyHive using the
OpenInference OpenAI instrumentor for comprehensive observability and tracing.

DSPy is a framework for programming language models with declarative modules.

Requirements:
    pip install honeyhive dspy openinference-instrumentation-dspy openinference-instrumentation-openai

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    OPENAI_API_KEY: Your OpenAI API key
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional


async def main():
    """Main example demonstrating DSPy integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([hh_api_key, hh_project, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        print("\nSet these environment variables and try again.")
        return False

    try:
        # Import required packages
        import dspy
        from openinference.instrumentation.dspy import DSPyInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.instrumentation.decorators import trace

        print("🚀 DSPy + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the DSPy instrumentor
        print("🔧 Setting up DSPy instrumentor...")
        dspy_instrumentor = DSPyInstrumentor()
        print("✓ DSPy instrumentor initialized")

        # 2. Initialize the OpenAI instrumentor (DSPy uses OpenAI under the hood)
        print("🔧 Setting up OpenAI instrumentor...")
        openai_instrumentor = OpenAIInstrumentor()
        print("✓ OpenAI instrumentor initialized")

        # 3. Initialize HoneyHive tracer
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,
            source="dspy_integration",
            verbose=True,
        )
        print("✓ HoneyHive tracer initialized")

        # 4. Instrument DSPy and OpenAI with HoneyHive tracer
        dspy_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ DSPy instrumented with HoneyHive tracer")
        
        openai_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ OpenAI instrumented with HoneyHive tracer")

        # 5. Configure DSPy with OpenAI
        print("\n🤖 Configuring DSPy...")
        lm = dspy.LM(model="openai/gpt-4o-mini", api_key=openai_api_key)
        dspy.configure(lm=lm)
        print("✓ DSPy configured with OpenAI")

        # Run test scenarios
        print("\n" + "=" * 50)
        print("Running DSPy Integration Tests")
        print("=" * 50)

        # 6. Test basic Predict module
        print("\n💬 Testing basic Predict module...")
        result1 = await test_basic_predict(tracer)
        print(f"✓ Basic Predict completed: {result1[:100]}...")

        # 7. Test ChainOfThought
        print("\n🧠 Testing ChainOfThought...")
        result2 = await test_chain_of_thought(tracer)
        print(f"✓ ChainOfThought completed: {result2[:100]}...")

        # 8. Test custom signature
        print("\n📋 Testing custom signature...")
        result3 = await test_custom_signature(tracer)
        print(f"✓ Custom signature completed: {result3[:100]}...")

        # 9. Test ReAct agent
        print("\n🤖 Testing ReAct agent...")
        result4 = await test_react_agent(tracer)
        print(f"✓ ReAct agent completed: {result4[:100]}...")

        # 10. Test multi-step reasoning
        print("\n🎯 Testing multi-step reasoning...")
        result5 = await test_multi_step_reasoning(tracer)
        print(f"✓ Multi-step reasoning completed: {result5[:100]}...")

        # 11. Test custom module
        print("\n🔧 Testing custom module...")
        result6 = await test_custom_module(tracer)
        print(f"✓ Custom module completed: {result6[:100]}...")

        # 12. Test classification
        print("\n🏷️ Testing classification...")
        result7 = await test_classification(tracer)
        print(f"✓ Classification completed: {result7}")

        # 13. Test retrieval (RAG simulation)
        print("\n📚 Testing retrieval simulation...")
        result8 = await test_retrieval(tracer)
        print(f"✓ Retrieval completed: {result8[:100]}...")

        # 14. Test optimization with BootstrapFewShot
        print("\n🎓 Testing BootstrapFewShot optimizer...")
        result9 = await test_bootstrap_optimizer(tracer)
        print(f"✓ BootstrapFewShot completed: optimized with {result9} examples")

        # 15. Test GEPA optimizer
        print("\n🧬 Testing GEPA optimizer...")
        result10 = await test_gepa_optimizer(tracer)
        print(f"✓ GEPA optimizer completed: {result10}")

        # 16. Test evaluation with metrics
        print("\n📊 Testing evaluation with metrics...")
        result11 = await test_evaluation_metrics(tracer)
        print(f"✓ Evaluation completed: score = {result11}")

        # 17. Clean up
        print("\n🧹 Cleaning up...")
        dspy_instrumentor.uninstrument()
        openai_instrumentor.uninstrument()
        tracer.force_flush()
        print("✓ Cleanup completed")

        print("\n🎉 DSPy integration example completed successfully!")
        print(f"📊 Check your HoneyHive project '{hh_project}' for trace data")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive dspy openinference-instrumentation-dspy openinference-instrumentation-openai")
        return False

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic_predict(tracer: "HoneyHiveTracer") -> str:
    """Test 1: Basic Predict module."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    @trace(event_type="chain", event_name="test_basic_predict", tracer=tracer)
    def _test():
        # Simple string signature
        predict = dspy.Predict("question -> answer")
        
        response = predict(question="What is the capital of France?")
        return response.answer
    
    return await asyncio.to_thread(_test)


async def test_chain_of_thought(tracer: "HoneyHiveTracer") -> str:
    """Test 2: ChainOfThought module for reasoning."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    @trace(event_type="chain", event_name="test_chain_of_thought", tracer=tracer)
    def _test():
        # ChainOfThought adds reasoning steps
        cot = dspy.ChainOfThought("question -> answer")
        
        response = cot(question="If a train travels at 60 mph for 2.5 hours, how far does it go?")
        return response.answer
    
    return await asyncio.to_thread(_test)


async def test_custom_signature(tracer: "HoneyHiveTracer") -> str:
    """Test 3: Custom signature with typed fields."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    class SummarizeSignature(dspy.Signature):
        """Summarize a piece of text into a concise summary."""
        text: str = dspy.InputField(desc="The text to summarize")
        summary: str = dspy.OutputField(desc="A concise summary of the text")

    @trace(event_type="chain", event_name="test_custom_signature", tracer=tracer)
    def _test():
        summarizer = dspy.Predict(SummarizeSignature)
        
        text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals.
        """
        
        response = summarizer(text=text)
        return response.summary
    
    return await asyncio.to_thread(_test)


async def test_react_agent(tracer: "HoneyHiveTracer") -> str:
    """Test 4: ReAct agent with tools."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    def get_weather(city: str) -> str:
        """Get the current weather for a city."""
        # Mock weather data
        return f"The weather in {city} is sunny and 75°F"

    def calculate(expression: str) -> str:
        """Calculate a mathematical expression."""
        try:
            result = eval(expression)
            return f"The result is {result}"
        except Exception as e:
            return f"Error: {e}"

    @trace(event_type="chain", event_name="test_react_agent", tracer=tracer)
    def _test():
        # ReAct combines reasoning and acting
        react = dspy.ReAct("question -> answer", tools=[get_weather, calculate])
        
        response = react(question="What is 15 * 8?")
        return response.answer
    
    return await asyncio.to_thread(_test)


async def test_multi_step_reasoning(tracer: "HoneyHiveTracer") -> str:
    """Test 5: Multi-step reasoning with intermediate steps."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    @trace(event_type="chain", event_name="test_multi_step_reasoning", tracer=tracer)
    def _test():
        # Use ChainOfThought for complex reasoning
        cot = dspy.ChainOfThought("problem -> solution")
        
        problem = """
        A farmer has chickens and rabbits. In total, there are 35 heads and 94 legs.
        How many chickens and how many rabbits does the farmer have?
        """
        
        response = cot(problem=problem)
        return response.solution
    
    return await asyncio.to_thread(_test)


async def test_custom_module(tracer: "HoneyHiveTracer") -> str:
    """Test 6: Custom DSPy module."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    class QuestionAnswerModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.generate_answer = dspy.ChainOfThought("context, question -> answer")

        def forward(self, context, question):
            return self.generate_answer(context=context, question=question)

    @trace(event_type="chain", event_name="test_custom_module", tracer=tracer)
    def _test():
        qa_module = QuestionAnswerModule()
        
        context = """
        The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.
        It is named after the engineer Gustave Eiffel, whose company designed and built the tower.
        Constructed from 1887 to 1889, it was initially criticized but has become a global 
        cultural icon of France and one of the most recognizable structures in the world.
        """
        
        question = "Who designed the Eiffel Tower?"
        
        response = qa_module(context=context, question=question)
        return response.answer
    
    return await asyncio.to_thread(_test)


async def test_classification(tracer: "HoneyHiveTracer") -> str:
    """Test 7: Text classification."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    class ClassifySignature(dspy.Signature):
        """Classify text into a sentiment category."""
        text: str = dspy.InputField(desc="The text to classify")
        sentiment: str = dspy.OutputField(desc="The sentiment: positive, negative, or neutral")

    @trace(event_type="chain", event_name="test_classification", tracer=tracer)
    def _test():
        classifier = dspy.Predict(ClassifySignature)
        
        text = "I absolutely loved this product! It exceeded all my expectations."
        
        response = classifier(text=text)
        return response.sentiment
    
    return await asyncio.to_thread(_test)


async def test_retrieval(tracer: "HoneyHiveTracer") -> str:
    """Test 8: Simulated retrieval-augmented generation."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    class RAGModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.generate_answer = dspy.ChainOfThought("context, query -> answer")

        def forward(self, query):
            # Simulate retrieval
            context = """
            Python was created by Guido van Rossum and first released in 1991.
            It emphasizes code readability with significant indentation.
            Python is dynamically-typed and garbage-collected.
            """
            
            return self.generate_answer(context=context, query=query)

    @trace(event_type="chain", event_name="test_retrieval", tracer=tracer)
    def _test():
        rag = RAGModule()
        
        response = rag(query="Who created Python and when?")
        return response.answer
    
    return await asyncio.to_thread(_test)


async def test_bootstrap_optimizer(tracer: "HoneyHiveTracer") -> int:
    """Test 9: BootstrapFewShot optimizer for program optimization."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    class QASignature(dspy.Signature):
        """Answer questions accurately."""
        question: str = dspy.InputField()
        answer: str = dspy.OutputField()

    @trace(event_type="chain", event_name="test_bootstrap_optimizer", tracer=tracer)
    def _test():
        # Create a simple QA program
        qa_program = dspy.Predict(QASignature)
        
        # Create training examples
        trainset = [
            dspy.Example(
                question="What is the capital of France?",
                answer="Paris"
            ).with_inputs("question"),
            dspy.Example(
                question="What is 2+2?",
                answer="4"
            ).with_inputs("question"),
            dspy.Example(
                question="What color is the sky?",
                answer="Blue"
            ).with_inputs("question"),
        ]
        
        # Define a simple metric
        def qa_metric(example, pred, trace=None):
            return example.answer.lower() in pred.answer.lower()
        
        # Use BootstrapFewShot optimizer
        try:
            optimizer = dspy.BootstrapFewShot(metric=qa_metric, max_bootstrapped_demos=2)
            optimized_program = optimizer.compile(qa_program, trainset=trainset)
            
            # Test the optimized program
            result = optimized_program(question="What is the capital of Italy?")
            print(f"   Optimized answer: {result.answer}")
            
            return len(trainset)
        except Exception as e:
            print(f"   Note: Bootstrap optimization requires more examples in practice. Error: {e}")
            return 3  # Return number of training examples
    
    return await asyncio.to_thread(_test)


async def test_gepa_optimizer(tracer: "HoneyHiveTracer") -> str:
    """Test 10: GEPA (Generalized Evolutionary Prompt Adaptation) optimizer."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    class FacilitySupportSignature(dspy.Signature):
        """Classify facility support requests by urgency and category."""
        request: str = dspy.InputField(desc="The facility support request")
        urgency: str = dspy.OutputField(desc="Urgency level: low, medium, high, critical")
        category: str = dspy.OutputField(desc="Request category: maintenance, IT, security, cleaning")

    @trace(event_type="chain", event_name="test_gepa_optimizer", tracer=tracer)
    def _test():
        # Create a facility support classifier
        classifier = dspy.ChainOfThought(FacilitySupportSignature)
        
        # Create training examples for GEPA
        trainset = [
            dspy.Example(
                request="The server room AC is completely down",
                urgency="critical",
                category="maintenance"
            ).with_inputs("request"),
            dspy.Example(
                request="Need new desk lamp for office 203",
                urgency="low",
                category="maintenance"
            ).with_inputs("request"),
            dspy.Example(
                request="Cannot access company database",
                urgency="high",
                category="IT"
            ).with_inputs("request"),
            dspy.Example(
                request="Suspicious person in parking lot",
                urgency="critical",
                category="security"
            ).with_inputs("request"),
        ]
        
        # Define metric for facility support
        def facility_metric(example, pred, trace=None):
            urgency_match = example.urgency.lower() == pred.urgency.lower()
            category_match = example.category.lower() == pred.category.lower()
            return (urgency_match + category_match) / 2  # Average score
        
        # Try to use GEPA optimizer
        try:
            # GEPA uses evolutionary techniques for prompt optimization
            gepa_optimizer = dspy.GEPA(
                metric=facility_metric,
                max_iterations=2,
                population_size=2
            )
            optimized_classifier = gepa_optimizer.compile(classifier, trainset=trainset)
            
            # Test the optimized classifier
            test_request = "Broken window in conference room B"
            result = optimized_classifier(request=test_request)
            
            return f"Urgency: {result.urgency}, Category: {result.category}"
        except AttributeError:
            # GEPA might not be available in all DSPy versions
            print("   Note: GEPA optimizer not available in this DSPy version")
            # Fall back to testing the base classifier
            result = classifier(request="Broken window in conference room B")
            return f"Urgency: {result.urgency}, Category: {result.category} (unoptimized)"
        except Exception as e:
            print(f"   Note: GEPA optimization requires more configuration. Error: {e}")
            result = classifier(request="Broken window in conference room B")
            return f"Urgency: {result.urgency}, Category: {result.category} (fallback)"
    
    return await asyncio.to_thread(_test)


async def test_evaluation_metrics(tracer: "HoneyHiveTracer") -> float:
    """Test 11: Evaluation with custom metrics."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import dspy

    @trace(event_type="chain", event_name="test_evaluation_metrics", tracer=tracer)
    def _test():
        # Create a simple math solver
        math_solver = dspy.ChainOfThought("problem -> solution")
        
        # Create test examples
        testset = [
            dspy.Example(
                problem="What is 5 + 3?",
                solution="8"
            ).with_inputs("problem"),
            dspy.Example(
                problem="What is 10 - 4?",
                solution="6"
            ).with_inputs("problem"),
            dspy.Example(
                problem="What is 3 * 4?",
                solution="12"
            ).with_inputs("problem"),
        ]
        
        # Define a metric that checks if the answer contains the correct number
        def math_metric(example, pred, trace=None):
            correct_answer = example.solution
            predicted_answer = pred.solution
            # Simple check: does the prediction contain the correct number?
            return correct_answer in predicted_answer
        
        # Evaluate the program
        try:
            from dspy import Evaluate
            evaluator = Evaluate(
                devset=testset,
                metric=math_metric,
                num_threads=1,
                display_progress=False
            )
            
            score = evaluator(math_solver)
            return float(score)
        except Exception as e:
            print(f"   Note: Evaluation with Evaluate class encountered an issue: {e}")
            # Manual evaluation
            correct = 0
            for example in testset:
                pred = math_solver(problem=example.problem)
                if math_metric(example, pred):
                    correct += 1
            return correct / len(testset)
    
    return await asyncio.to_thread(_test)


if __name__ == "__main__":
    """Run the DSPy integration example."""
    success = asyncio.run(main())

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)

