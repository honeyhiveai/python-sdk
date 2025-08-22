#!/usr/bin/env python3
"""Diagnostic test for comprehensive test decorator overhead"""

import time
import os
import sys
from unittest.mock import patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.tracer import HoneyHiveTracer, trace

# Test configuration
TEST_CONFIG = {
    'HH_API_KEY': 'test-key',
    'HH_PROJECT': 'test-project',
    'HH_SOURCE': 'comprehensive-diagnostic'
}

def plain_function():
    """Plain function without decorator"""
    return 42

@trace
def traced_function():
    """Function with trace decorator"""
    return 42

def comprehensive_test_simulation():
    """Simulate the exact comprehensive test conditions"""
    print("🔍 Comprehensive Test Simulation")
    print("=" * 50)
    
    # Initialize tracer exactly like the comprehensive test
    print("🔧 Initializing tracer...")
    tracer = HoneyHiveTracer(
        api_key=TEST_CONFIG['HH_API_KEY'],
        project=TEST_CONFIG['HH_PROJECT'],
        source=TEST_CONFIG['HH_SOURCE'],
        test_mode=True
    )
    
    print(f"  ✅ Tracer initialized: {tracer}")
    
    # Use time.time() like the comprehensive test
    print("\n⏱️  Using time.time() (like comprehensive test)...")
    
    # Measure plain function performance
    start_time = time.time()
    for _ in range(1000):
        plain_function()
    plain_time = time.time() - start_time
    
    print(f"  📊 Plain function time: {plain_time:.6f}s")
    
    # Measure traced function performance
    start_time = time.time()
    for _ in range(1000):
        traced_function()
    traced_time = time.time() - start_time
    
    print(f"  📊 Traced function time: {traced_time:.6f}s")
    
    # Calculate overhead ratio
    overhead_ratio = traced_time / plain_time if plain_time > 0 else float('inf')
    print(f"  ⚡ Overhead ratio: {overhead_ratio:.2f}x")
    
    return overhead_ratio

def time_comparison_test():
    """Compare time.time() vs time.perf_counter()"""
    print("\n" + "="*50)
    print("⏱️  Time Function Comparison")
    print("="*50)
    
    iterations = 1000
    
    # Test with time.time()
    start_time = time.time()
    for _ in range(iterations):
        traced_function()
    time_time_result = time.time() - start_time
    
    # Test with time.perf_counter()
    start_time = time.perf_counter()
    for _ in range(iterations):
        traced_function()
    perf_counter_result = time.perf_counter() - start_time
    
    print(f"  📊 time.time() result:      {time_time_result:.6f}s")
    print(f"  📊 time.perf_counter():     {perf_counter_result:.6f}s")
    print(f"  ⚡ Difference ratio:        {time_time_result/perf_counter_result:.2f}x")
    
    return time_time_result, perf_counter_result

def detailed_timing_analysis():
    """Detailed timing analysis with different iteration counts"""
    print("\n" + "="*50)
    print("🔍 Detailed Timing Analysis")
    print("="*50)
    
    iteration_counts = [100, 500, 1000, 2000, 5000]
    
    for iterations in iteration_counts:
        print(f"\n🔢 Testing with {iterations} iterations...")
        
        # Plain function
        start_time = time.perf_counter()
        for _ in range(iterations):
            plain_function()
        plain_time = time.perf_counter() - start_time
        
        # Traced function
        start_time = time.perf_counter()
        for _ in range(iterations):
            traced_function()
        traced_time = time.perf_counter() - start_time
        
        # Calculate overhead
        overhead_ratio = traced_time / plain_time if plain_time > 0 else float('inf')
        
        print(f"  📊 Plain: {plain_time:.6f}s, Traced: {traced_time:.6f}s")
        print(f"  ⚡ Overhead: {overhead_ratio:.1f}x")
        
        if overhead_ratio > 1000:
            print(f"  ❌ CRITICAL: Extremely high overhead at {iterations} iterations!")

if __name__ == "__main__":
    with patch.dict(os.environ, TEST_CONFIG, clear=True):
        print("🚀 Comprehensive Test Overhead Diagnostic")
        print("=" * 60)
        
        # Run comprehensive test simulation
        comprehensive_overhead = comprehensive_test_simulation()
        
        # Compare time functions
        time_time_result, perf_counter_result = time_comparison_test()
        
        # Detailed analysis
        detailed_timing_analysis()
        
        print("\n" + "="*60)
        print("🎯 SUMMARY")
        print("="*60)
        print(f"  Comprehensive test overhead: {comprehensive_overhead:.1f}x")
        print(f"  time.time() vs perf_counter: {time_time_result/perf_counter_result:.2f}x")
        
        if comprehensive_overhead > 100000:
            print("  ❌ CRITICAL: Reproduced the extremely high overhead!")
            print("  💡 This matches the comprehensive test failure")
