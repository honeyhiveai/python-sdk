"""Baseline Lambda function WITHOUT HoneyHive SDK for overhead comparison."""

import json
import statistics
import time
from typing import Any, Dict, List


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


def measure_baseline_operations(
    iterations: int = 1000, work_per_iteration_ms: float = 1.0
) -> Dict[str, Any]:
    """Measure baseline operations without any SDK overhead."""
    measurements = {
        "operation_times": [],
        "total_work_times": [],
        "overhead_simulation": [],
    }

    # Run multiple iterations for statistical significance
    for iteration in range(iterations):
        # Simulate span creation overhead (just function call overhead)
        start_time = time.perf_counter()
        operation_start = time.perf_counter()  # Simulate span start
        operation_creation_time = (time.perf_counter() - start_time) * 1000
        measurements["operation_times"].append(operation_creation_time)

        # Simulate span operations overhead
        start_time = time.perf_counter()
        operation_metadata = {  # Simulate setting attributes
            "iteration": iteration,
            "test_type": "baseline_measurement",
            "cpu_work": True,
        }
        operation_ops_time = (time.perf_counter() - start_time) * 1000

        # Do the actual work
        work_start = time.perf_counter()
        actual_work_duration = cpu_intensive_work(work_per_iteration_ms)
        work_time = (time.perf_counter() - work_start) * 1000
        measurements["total_work_times"].append(work_time)

        # Simulate span completion overhead
        start_time = time.perf_counter()
        operation_end = time.perf_counter()  # Simulate span end
        operation_completion_time = (time.perf_counter() - start_time) * 1000

        # Total overhead for this iteration (simulated)
        iteration_overhead = (
            operation_creation_time + operation_ops_time + operation_completion_time
        )
        measurements["overhead_simulation"].append(iteration_overhead)

    return measurements


def measure_bulk_baseline_operations(
    num_requests: int = 50,
    operations_per_request: int = 10,
    work_per_operation_ms: float = 20,
) -> Dict[str, Any]:
    """Measure bulk baseline operations for statistical significance."""
    request_measurements = []

    for request in range(num_requests):
        request_start = time.perf_counter()

        # Simulate multiple operations per request (like multiple spans)
        for operation_num in range(operations_per_request):
            # Simulate operation creation
            operation_start = time.perf_counter()

            # Simulate setting attributes
            operation_metadata = {
                "request_id": request,
                "operation_number": operation_num,
                "test_type": "bulk_baseline",
            }

            # Do actual work
            actual_work_duration = cpu_intensive_work(work_per_operation_ms)

            # Simulate operation completion
            operation_end = time.perf_counter()

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
        "total_operations": num_requests * operations_per_request,
        "expected_work_time_ms": num_requests
        * operations_per_request
        * work_per_operation_ms,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Baseline overhead measurement handler WITHOUT HoneyHive SDK."""
    handler_start = time.perf_counter()

    try:
        # Get test parameters from event
        test_type = event.get("test_type", "bulk")

        if test_type == "bulk":
            # Bulk measurement test
            num_requests = event.get("num_requests", 50)
            operations_per_request = event.get("operations_per_request", 10)
            work_per_operation_ms = event.get("work_per_operation_ms", 20)

            results = measure_bulk_baseline_operations(
                num_requests=num_requests,
                operations_per_request=operations_per_request,
                work_per_operation_ms=work_per_operation_ms,
            )

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "test_type": "baseline_bulk",
                        "parameters": {
                            "num_requests": num_requests,
                            "operations_per_request": operations_per_request,
                            "work_per_operation_ms": work_per_operation_ms,
                        },
                        "results": results,
                        "handler_total_ms": (time.perf_counter() - handler_start)
                        * 1000,
                        "baseline_note": "This is baseline measurement WITHOUT HoneyHive SDK",
                    },
                    indent=2,
                ),
            }

        elif test_type == "detailed":
            # Detailed measurement test
            iterations = event.get("iterations", 1000)
            work_per_iteration_ms = event.get("work_per_iteration_ms", 1.0)

            measurements = measure_baseline_operations(
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
                "operation_overhead_stats": calc_stats(measurements["operation_times"]),
                "work_time_stats": calc_stats(measurements["total_work_times"]),
                "simulated_overhead_stats": calc_stats(
                    measurements["overhead_simulation"]
                ),
                "total_iterations": iterations,
                "work_per_iteration_ms": work_per_iteration_ms,
            }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "test_type": "baseline_detailed",
                        "parameters": {
                            "iterations": iterations,
                            "work_per_iteration_ms": work_per_iteration_ms,
                        },
                        "results": results,
                        "handler_total_ms": (time.perf_counter() - handler_start)
                        * 1000,
                        "baseline_note": "This is baseline measurement WITHOUT HoneyHive SDK",
                    },
                    indent=2,
                ),
            }

        else:
            # Simple work duration test
            work_duration_ms = event.get("work_duration_ms", 1000)

            work_start = time.perf_counter()
            actual_work_duration = cpu_intensive_work(work_duration_ms)
            work_time = (time.perf_counter() - work_start) * 1000

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "test_type": "baseline_simple",
                        "requested_work_ms": work_duration_ms,
                        "actual_work_ms": actual_work_duration,
                        "total_time_ms": work_time,
                        "measurement_overhead_ms": work_time - actual_work_duration,
                        "handler_total_ms": (time.perf_counter() - handler_start)
                        * 1000,
                        "baseline_note": "This is baseline measurement WITHOUT HoneyHive SDK",
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
                    "baseline_note": "This is baseline measurement WITHOUT HoneyHive SDK",
                }
            ),
        }
