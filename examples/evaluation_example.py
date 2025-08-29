#!/usr/bin/env python3
"""
Evaluation Example

This example demonstrates how to use the evaluation framework with
the recommended HoneyHiveTracer.init() initialization pattern.
"""

import os
from honeyhive import evaluate, evaluator, aevaluator, HoneyHiveTracer

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "evaluation-demo"
os.environ["HH_SOURCE"] = "development"

def main():
    """Main evaluation example function."""
    
    print("🚀 HoneyHive Evaluation Framework Example")
    print("=" * 50)
    
    # Initialize tracer using the recommended pattern
    print("1. Initializing HoneyHiveTracer...")
    HoneyHiveTracer.init(
        api_key="your-api-key-here",
        project="evaluation-demo",
        source="development"
    )
    
    # Get tracer instance
    tracer = HoneyHiveTracer._instance
    print(f"✓ Tracer initialized for project: {tracer.project}")
    print(f"✓ Source environment: {tracer.source}")
    print(f"✓ Session ID: {tracer.session_id}")
    print()
    
    # Demonstrate evaluation decorators
    print("2. Testing evaluation decorators...")
    
    @evaluator
    def accuracy_evaluator(inputs, outputs, **kwargs):
        """Simple accuracy evaluator."""
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")
        return {"accuracy": expected == actual}
    
    @evaluator
    def length_evaluator(inputs, outputs, **kwargs):
        """Length evaluator."""
        response = outputs.get("response", "")
        return {"length": len(response)}
    
    # Test synchronous evaluation
    print("3. Testing synchronous evaluation...")
    
    @evaluate(evaluators=[accuracy_evaluator, length_evaluator])
    def simple_function(inputs):
        """Simple function to evaluate."""
        return {"response": "Hello, World!"}
    
    result = simple_function({"expected": "Hello, World!"})
    print(f"✓ Function result: {result}")
    
    # Test async evaluation
    print("4. Testing async evaluation...")
    
    @aevaluator(evaluators=[accuracy_evaluator, length_evaluator])
    async def async_function(inputs):
        """Async function to evaluate."""
        import asyncio
        await asyncio.sleep(0.1)
        return {"response": "Async Hello, World!"}
    
    import asyncio
    async_result = asyncio.run(async_function({"expected": "Async Hello, World!"}))
    print(f"✓ Async function result: {async_result}")
    
    print("\n🎉 Evaluation example completed successfully!")
    print("\nKey features demonstrated:")
    print("✅ Primary initialization using HoneyHiveTracer.init()")
    print("✅ @evaluator decorator for custom evaluators")
    print("✅ @evaluate decorator for synchronous evaluation")
    print("✅ @aevaluator decorator for asynchronous evaluation")
    print("✅ Accessing tracer instance via HoneyHiveTracer._instance")


if __name__ == "__main__":
    main()
