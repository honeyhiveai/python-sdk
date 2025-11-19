"""Dedicated test for measuring HoneyHive SDK overhead with minimal variance."""

import json
import os
import statistics
import sys
import time
from typing import Any, Dict, List

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


def measure_bulk_sdk_operations(
    num_requests: int = 50, spans_per_request: int = 10, work_per_span_ms: float = 20
) -> Dict[str, Any]:
    """Measure bulk SDK operations for statistical significance (optimal approach)."""
    request_measurements = []

    for request in range(num_requests):
        request_start = time.perf_counter()

        # Do substantial work with multiple spans
        for span_num in range(spans_per_request):
            with tracer.start_span(f"request_{request}_span_{span_num}") as span:
                span.set_attribute("request_id", request)
                span.set_attribute("span_number", span_num)
                span.set_attribute("test_type", "bulk_sdk_measurement")

                # CPU-intensive work
                actual_work_duration = cpu_intensive_work(work_per_span_ms)
                span.set_attribute("work_duration_ms", actual_work_duration)

        request_time = (time.perf_counter() - request_start) * 1000
        request_measurements.append(request_time)

    return {
        "request_times_ms": request_measurements,
        "mean_time_ms": statistics.mean(request_measurements),
        "std_dev_ms": (
            statistics.stdev(request_measurements)
            if len(request_measurements) > 1
            else 0
        ),
        "coefficient_of_variation": (
            statistics.stdev(request_measurements)
            / statistics.mean(request_measurements)
            * 100
            if statistics.mean(request_measurements) > 0
            else 0
        ),
        "total_spans": num_requests * spans_per_request,
        "expected_work_time_ms": num_requests * spans_per_request * work_per_span_ms,
    }


def measure_detailed_sdk_operations(
    iterations: int = 1000, work_per_iteration_ms: float = 1.0
) -> Dict[str, Any]:
    """Measure detailed SDK operations for precision analysis."""
    measurements = {
        "span_creation": [],
        "span_operations": [],
        "span_completion": [],
        "flush_operations": [],
        "total_overhead": [],
        "work_times": [],
    }

    # Run multiple iterations for statistical significance
    for iteration in range(iterations):
        # Measure span creation
        start_time = time.perf_counter()
        with tracer.start_span(f"detailed_test_{iteration}") as span:
            span_creation_time = (time.perf_counter() - start_time) * 1000
            measurements["span_creation"].append(span_creation_time)

            # Measure span operations
            start_time = time.perf_counter()
            span.set_attribute("iteration", iteration)
            span.set_attribute("test_type", "detailed_measurement")
            span.set_attribute("cpu_work", True)
            span_ops_time = (time.perf_counter() - start_time) * 1000
            measurements["span_operations"].append(span_ops_time)

            # Do actual work and measure it
            work_start = time.perf_counter()
            actual_work_duration = cpu_intensive_work(work_per_iteration_ms)
            work_time = (time.perf_counter() - work_start) * 1000
            measurements["work_times"].append(work_time)

            # Measure span completion timing (the with block exit)
            start_time = time.perf_counter()

        span_completion_time = (time.perf_counter() - start_time) * 1000
        measurements["span_completion"].append(span_completion_time)

        # Total overhead for this iteration
        iteration_overhead = span_creation_time + span_ops_time + span_completion_time
        measurements["total_overhead"].append(iteration_overhead)

    # Measure flush operations (separate from iterations)
    flush_times = []
    for _ in range(
        min(100, iterations // 10)
    ):  # Reasonable number of flush measurements
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
            "body": json.dumps(
                {
                    "error": "Tracer not available",
                    "sdk_import_time_ms": (
                        SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                    ),
                    "tracer_init_time_ms": (
                        TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                    ),
                }
            ),
        }

    try:
        # Get test parameters from event
        test_type = event.get("test_type", "bulk")

        if test_type == "bulk":
            # Bulk measurement test (optimal approach)
            num_requests = event.get("num_requests", 50)
            spans_per_request = event.get("spans_per_request", 10)
            work_per_span_ms = event.get("work_per_span_ms", 20)

            results = measure_bulk_sdk_operations(
                num_requests=num_requests,
                spans_per_request=spans_per_request,
                work_per_span_ms=work_per_span_ms,
            )

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "test_type": "sdk_bulk",
                        "parameters": {
                            "num_requests": num_requests,
                            "spans_per_request": spans_per_request,
                            "work_per_span_ms": work_per_span_ms,
                        },
                        "results": results,
                        "initialization_overhead": {
                            "sdk_import_ms": (
                                SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                            ),
                            "tracer_init_ms": (
                                TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                            ),
                            "total_init_ms": (
                                (SDK_IMPORT_TIME + TRACER_INIT_TIME) * 1000
                                if SDK_IMPORT_TIME > 0 and TRACER_INIT_TIME > 0
                                else -1
                            ),
                        },
                        "handler_total_ms": (time.perf_counter() - handler_start)
                        * 1000,
                        "sdk_note": "This measurement includes HoneyHive SDK overhead",
                    },
                    indent=2,
                ),
            }

        elif test_type == "detailed":
            # Detailed measurement test
            iterations = event.get("iterations", 1000)
            work_per_iteration_ms = event.get("work_per_iteration_ms", 1.0)

            sdk_measurements = measure_detailed_sdk_operations(
                iterations=iterations, work_per_iteration_ms=work_per_iteration_ms
            )

            # Calculate statistics
            def calc_stats(values: List[float]) -> Dict[str, float]:
                if not values:
                    return {
                        "mean": 0,
                        "median": 0,
                        "std_dev": 0,
                        "min": 0,
                        "max": 0,
                        "cv": 0,
                    }
                mean_val = statistics.mean(values)
                return {
                    "mean": mean_val,
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "cv": (
                        (statistics.stdev(values) / mean_val * 100)
                        if mean_val > 0
                        else 0
                    ),
                }

            results = {
                "sdk_overhead_stats": {
                    "span_creation": calc_stats(sdk_measurements["span_creation"]),
                    "span_operations": calc_stats(sdk_measurements["span_operations"]),
                    "span_completion": calc_stats(sdk_measurements["span_completion"]),
                    "flush_operations": calc_stats(
                        sdk_measurements["flush_operations"]
                    ),
                    "total_per_span": calc_stats(sdk_measurements["total_overhead"]),
                    "work_times": calc_stats(sdk_measurements["work_times"]),
                },
                "overhead_analysis": {
                    "avg_per_span_overhead_ms": statistics.mean(
                        sdk_measurements["total_overhead"]
                    ),
                    "avg_flush_overhead_ms": statistics.mean(
                        sdk_measurements["flush_operations"]
                    ),
                    "avg_work_time_ms": statistics.mean(sdk_measurements["work_times"]),
                    "overhead_vs_work_percentage": (
                        statistics.mean(sdk_measurements["total_overhead"])
                        / statistics.mean(sdk_measurements["work_times"])
                        * 100
                        if statistics.mean(sdk_measurements["work_times"]) > 0
                        else 0
                    ),
                    "coefficient_of_variation": calc_stats(
                        sdk_measurements["total_overhead"]
                    )["cv"],
                },
                "total_iterations": iterations,
                "work_per_iteration_ms": work_per_iteration_ms,
            }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "test_type": "sdk_detailed",
                        "parameters": {
                            "iterations": iterations,
                            "work_per_iteration_ms": work_per_iteration_ms,
                        },
                        "results": results,
                        "initialization_overhead": {
                            "sdk_import_ms": (
                                SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                            ),
                            "tracer_init_ms": (
                                TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                            ),
                            "total_init_ms": (
                                (SDK_IMPORT_TIME + TRACER_INIT_TIME) * 1000
                                if SDK_IMPORT_TIME > 0 and TRACER_INIT_TIME > 0
                                else -1
                            ),
                        },
                        "handler_total_ms": (time.perf_counter() - handler_start)
                        * 1000,
                        "sdk_note": "This measurement includes HoneyHive SDK overhead",
                    },
                    indent=2,
                ),
            }

        else:
            # Simple work duration test (legacy compatibility)
            work_duration_ms = event.get("work_duration_ms", 1000)

            work_start = time.perf_counter()
            actual_work_duration = cpu_intensive_work(work_duration_ms)
            work_time = (time.perf_counter() - work_start) * 1000

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "test_type": "sdk_simple",
                        "requested_work_ms": work_duration_ms,
                        "actual_work_ms": actual_work_duration,
                        "total_time_ms": work_time,
                        "measurement_overhead_ms": work_time - actual_work_duration,
                        "initialization_overhead": {
                            "sdk_import_ms": (
                                SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                            ),
                            "tracer_init_ms": (
                                TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                            ),
                            "total_init_ms": (
                                (SDK_IMPORT_TIME + TRACER_INIT_TIME) * 1000
                                if SDK_IMPORT_TIME > 0 and TRACER_INIT_TIME > 0
                                else -1
                            ),
                        },
                        "handler_total_ms": (time.perf_counter() - handler_start)
                        * 1000,
                        "sdk_note": "This measurement includes HoneyHive SDK overhead",
                    }
                ),
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                    "handler_time_ms": (time.perf_counter() - handler_start) * 1000,
                }
            ),
        }
