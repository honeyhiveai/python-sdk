#!/usr/bin/env python3
"""Repro script for 400 error in update_run_with_results.

This script reproduces the customer issue where:
- input_function and evaluator run successfully
- HTTP request to update_run_with_results returns 400
- No results logged in experiment UI

Based on integration test patterns from test_experiments_integration.py
"""

import os
import sys
import time
from typing import Any, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from honeyhive import HoneyHive
from honeyhive.experiments import evaluate


def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
    """Simple test function that echoes input."""
    inputs = datapoint.get("inputs", {})
    question = inputs.get("question", "")
    return {"answer": f"Answer to: {question}"}


def accuracy_evaluator(
    outputs: Dict[str, Any],
    _inputs: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> float:
    """Simple evaluator that checks if answer matches."""
    expected = ground_truth.get("expected_answer", "")
    actual = outputs.get("answer", "")
    return 1.0 if expected in actual else 0.0


def main():
    """Run experiment with verbose logging to catch 400 error."""
    # Get credentials from environment
    api_key = os.environ.get("HH_API_KEY") or os.environ.get("HONEYHIVE_API_KEY")
    project = os.environ.get("HH_PROJECT") or os.environ.get("HONEYHIVE_PROJECT", "default")
    
    if not api_key:
        print("ERROR: HH_API_KEY or HONEYHIVE_API_KEY environment variable not set")
        sys.exit(1)
    
    # Create dataset
    dataset = [
        {
            "inputs": {"question": "What is 2+2?"},
            "ground_truth": {"expected_answer": "4"},
        },
        {
            "inputs": {"question": "What is the capital of France?"},
            "ground_truth": {"expected_answer": "Paris"},
        },
    ]
    
    run_name = f"repro-400-error-{int(time.time())}"
    
    print(f"\n{'='*70}")
    print("REPRODUCING 400 ERROR IN update_run_with_results")
    print(f"{'='*70}")
    print(f"Run name: {run_name}")
    print(f"Dataset size: {len(dataset)} datapoints")
    print(f"Project: {project}")
    print(f"Verbose: True (to see detailed logs)")
    print(f"{'='*70}\n")
    
    # Create client with verbose logging
    client = HoneyHive(api_key=api_key, verbose=True)
    
    try:
        # Execute evaluate() - this should trigger the 400 error
        print("Executing evaluate()...")
        print("Watch for 'HTTP request completed with status: 400' in logs")
        print("Watch for 'Failed to update run:' warning\n")
        
        result_summary = evaluate(
            function=simple_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=api_key,
            project=project,
            name=run_name,
            max_workers=2,
            aggregate_function="average",
            verbose=True,  # Enable verbose logging
        )
        
        print(f"\n{'='*70}")
        print("EXPERIMENT COMPLETED")
        print(f"{'='*70}")
        print(f"Run ID: {result_summary.run_id}")
        print(f"Status: {result_summary.status}")
        print(f"Success: {result_summary.success}")
        print(f"Passed: {len(result_summary.passed)} datapoints")
        print(f"Failed: {len(result_summary.failed)} datapoints")
        
        # Try to fetch run from backend to verify state
        print(f"\n{'='*70}")
        print("VERIFYING BACKEND STATE")
        print(f"{'='*70}")
        
        try:
            backend_run = client.evaluations.get_run(result_summary.run_id)
            
            if hasattr(backend_run, "evaluation") and backend_run.evaluation:
                run_data = backend_run.evaluation
                
                # Check if results are present
                metadata = getattr(run_data, "metadata", {}) or {}
                evaluator_metrics = metadata.get("evaluator_metrics", {})
                
                print(f"✅ Run exists in backend")
                print(f"   Status: {getattr(run_data, 'status', 'NOT SET')}")
                print(f"   Events: {len(getattr(run_data, 'event_ids', []))}")
                print(f"   Evaluator metrics: {len(evaluator_metrics)} datapoints")
                
                if len(evaluator_metrics) == 0:
                    print("\n⚠️  WARNING: No evaluator metrics found!")
                    print("   This indicates the 400 error prevented metrics from being saved")
                else:
                    print("✅ Evaluator metrics found in backend")
            else:
                print("⚠️  Backend response missing evaluation data")
                
        except Exception as e:
            print(f"❌ Error fetching run from backend: {e}")
            print("   This might indicate the run wasn't properly created/updated")
        
    except Exception as e:
        print(f"\n❌ Error during experiment execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

