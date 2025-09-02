"""Dedicated test for measuring HoneyHive SDK overhead with minimal variance."""

import json
import os
import sys
import time
from typing import Any, Dict, List
import statistics

sys.path.insert(0, "/var/task")

# Track initialization timing
INITIALIZATION_TIME = time.time()

try:
    from honeyhive.tracer import HoneyHiveTracer

    SDK_IMPORT_TIME = time.time() - INITIALIZATION_TIME
    print(f"✅ SDK import took: {SDK_IMPORT_TIME * 1000:.2f}ms")
except ImportError as e:
    print(f"❌ SDK import failed: {e}")
    SDK_IMPORT_TIME = -1

# Initialize tracer and measure time
tracer = None
TRACER_INIT_TIME = -1

if "honeyhive" in sys.modules:
    init_start = time.time()
    try:
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "test-key"),
            project="lambda-overhead-test",
            source="aws-lambda",
            session_name="overhead-benchmark",
            test_mode=True,
            disable_http_tracing=True,
        )
        TRACER_INIT_TIME = time.time() - init_start
        print(f"✅ Tracer initialization took: {TRACER_INIT_TIME * 1000:.2f}ms")
    except Exception as e:
        print(f"❌ Tracer initialization failed: {e}")
        TRACER_INIT_TIME = -1


def cpu_intensive_work(duration_ms: float) -> float:
    """Perform CPU-intensive work for precise timing without sleep variance."""
    start_time = time.perf_counter()
    target_duration = duration_ms / 1000.0
    
    # CPU-bound work that's deterministic
    counter = 0
    while (time.perf_counter() - start_time) < target_duration:
        counter += 1
        # Simple arithmetic to consume CPU cycles
        _ = sum(i * i for i in range(100))
    
    actual_duration = time.perf_counter() - start_time
    return actual_duration * 1000


def measure_sdk_operations() -> Dict[str, Any]:
    """Measure SDK operations with high precision."""
    measurements = {
        "span_creation": [],
        "span_operations": [],
        "span_completion": [],
        "flush_operations": [],
        "total_overhead": [],
    }
    
    # Run multiple iterations for statistical significance
    for iteration in range(10):
        # Measure span creation
        start_time = time.perf_counter()
        with tracer.start_span(f"overhead_test_{iteration}") as span:
            span_creation_time = (time.perf_counter() - start_time) * 1000
            measurements["span_creation"].append(span_creation_time)
            
            # Measure span operations
            start_time = time.perf_counter()
            span.set_attribute("iteration", iteration)
            span.set_attribute("test_type", "overhead_measurement")
            span.set_attribute("cpu_work", True)
            span_ops_time = (time.perf_counter() - start_time) * 1000
            measurements["span_operations"].append(span_ops_time)
            
            # Measure span completion timing (the with block exit)
            start_time = time.perf_counter()
        
        span_completion_time = (time.perf_counter() - start_time) * 1000
        measurements["span_completion"].append(span_completion_time)
        
        # Total overhead for this iteration
        iteration_overhead = span_creation_time + span_ops_time + span_completion_time
        measurements["total_overhead"].append(iteration_overhead)
    
    # Measure flush operations (separate from iterations)
    flush_times = []
    for _ in range(5):
        start_time = time.perf_counter()
        tracer.force_flush(timeout_millis=100)
        flush_time = (time.perf_counter() - start_time) * 1000
        flush_times.append(flush_time)
    
    measurements["flush_operations"] = flush_times
    
    return measurements


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Dedicated SDK overhead measurement handler."""
    handler_start = time.perf_counter()
    
    if not tracer:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Tracer not available",
                "sdk_import_time_ms": SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1,
                "tracer_init_time_ms": TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1,
            }),
        }

    try:
        # Get work duration from event (default 50ms)
        work_duration_ms = event.get("work_duration_ms", 50)
        
        # Measure baseline work without SDK
        baseline_start = time.perf_counter()
        actual_work_duration = cpu_intensive_work(work_duration_ms)
        baseline_time = (time.perf_counter() - baseline_start) * 1000
        
        # Measure SDK operations
        sdk_measurements = measure_sdk_operations()
        
        # Calculate statistics
        def calc_stats(values: List[float]) -> Dict[str, float]:
            if not values:
                return {"mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0}
            return {
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
            }
        
        # Compile comprehensive results
        results = {
            "baseline_work": {
                "requested_ms": work_duration_ms,
                "actual_ms": actual_work_duration,
                "measurement_overhead_ms": baseline_time - actual_work_duration,
            },
            "sdk_overhead_stats": {
                "span_creation": calc_stats(sdk_measurements["span_creation"]),
                "span_operations": calc_stats(sdk_measurements["span_operations"]),
                "span_completion": calc_stats(sdk_measurements["span_completion"]),
                "flush_operations": calc_stats(sdk_measurements["flush_operations"]),
                "total_per_span": calc_stats(sdk_measurements["total_overhead"]),
            },
            "overhead_analysis": {
                "avg_per_span_overhead_ms": statistics.mean(sdk_measurements["total_overhead"]),
                "avg_flush_overhead_ms": statistics.mean(sdk_measurements["flush_operations"]),
                "overhead_vs_work_percentage": (
                    statistics.mean(sdk_measurements["total_overhead"]) / actual_work_duration * 100
                    if actual_work_duration > 0 else 0
                ),
                "coefficient_of_variation": (
                    statistics.stdev(sdk_measurements["total_overhead"]) / 
                    statistics.mean(sdk_measurements["total_overhead"]) * 100
                    if statistics.mean(sdk_measurements["total_overhead"]) > 0 else 0
                ),
            },
            "initialization_overhead": {
                "sdk_import_ms": SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1,
                "tracer_init_ms": TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1,
                "total_init_ms": (
                    (SDK_IMPORT_TIME + TRACER_INIT_TIME) * 1000
                    if SDK_IMPORT_TIME > 0 and TRACER_INIT_TIME > 0 else -1
                ),
            },
            "handler_total_ms": (time.perf_counter() - handler_start) * 1000,
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(results, indent=2),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "handler_time_ms": (time.perf_counter() - handler_start) * 1000,
            }),
        }
