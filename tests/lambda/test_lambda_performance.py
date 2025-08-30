"""Performance tests for HoneyHive SDK in AWS Lambda environment."""

import json
import pytest
import requests
import subprocess
import time
import statistics
from typing import Dict, Any, List
import docker
import os


class TestLambdaPerformance:
    """Performance tests for Lambda environment."""

    @pytest.fixture(scope="class")
    def performance_container(self):
        """Start optimized Lambda container for performance testing."""
        client = docker.from_env()

        container = client.containers.run(
            "honeyhive-lambda:bundle-native",
            command="cold_start_test.lambda_handler",
            ports={"8080/tcp": 9100},
            environment={
                "AWS_LAMBDA_FUNCTION_NAME": "honeyhive-performance-test",
                "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "256",
                "HH_API_KEY": "test-key",
                "HH_PROJECT": "lambda-performance-test",
                "HH_SOURCE": "performance-test",
                "HH_TEST_MODE": "true"
            },
            detach=True,
            remove=True,
        )

        # Wait for container to be ready
        time.sleep(5)

        yield container

        try:
            container.stop()
        except:
            pass

    def invoke_lambda_timed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke Lambda and measure timing."""
        url = "http://localhost:9100/2015-03-31/functions/function/invocations"

        start_time = time.time()
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=30
        )
        total_time = (time.time() - start_time) * 1000

        result = response.json()
        result["_test_total_time_ms"] = total_time

        return result

    @pytest.mark.benchmark
    def test_cold_start_performance(self, performance_container):
        """Benchmark cold start performance."""
        # The first invocation should be a cold start
        result = self.invoke_lambda_timed({"test": "cold_start_benchmark"})

        assert result["statusCode"] == 200

        body = json.loads(result["body"])
        timings = body.get("timings", {})

        # Collect metrics
        metrics = {
            "cold_start": body.get("cold_start", True),
            "total_time_ms": result["_test_total_time_ms"],
            "sdk_import_ms": timings.get("sdk_import_ms", 0),
            "tracer_init_ms": timings.get("tracer_init_ms", 0),
            "handler_total_ms": timings.get("handler_total_ms", 0),
            "work_time_ms": timings.get("work_time_ms", 0),
            "flush_time_ms": timings.get("flush_time_ms", 0),
        }

        # Performance assertions
        assert (
            metrics["sdk_import_ms"] < 50
        ), f"SDK import too slow: {metrics['sdk_import_ms']}ms"
        assert (
            metrics["tracer_init_ms"] < 100
        ), f"Tracer init too slow: {metrics['tracer_init_ms']}ms"
        assert (
            metrics["total_time_ms"] < 2000
        ), f"Total time too slow: {metrics['total_time_ms']}ms"

        return metrics

    @pytest.mark.benchmark
    def test_warm_start_performance(self, performance_container):
        """Benchmark warm start performance."""
        # First call to warm up
        self.invoke_lambda_timed({"test": "warmup"})

        # Now measure warm start performance
        warm_start_times = []

        for i in range(5):
            result = self.invoke_lambda_timed({"test": f"warm_start_{i}"})

            assert result["statusCode"] == 200

            body = json.loads(result["body"])
            warm_start_times.append(
                {
                    "total_time_ms": result["_test_total_time_ms"],
                    "handler_time_ms": body.get("timings", {}).get(
                        "handler_total_ms", 0
                    ),
                    "cold_start": body.get("cold_start", False),
                }
            )

        # All should be warm starts
        for timing in warm_start_times:
            assert not timing["cold_start"], "Should be warm start"

        # Calculate statistics
        total_times = [t["total_time_ms"] for t in warm_start_times]
        handler_times = [t["handler_time_ms"] for t in warm_start_times]

        avg_total = statistics.mean(total_times)
        avg_handler = statistics.mean(handler_times)
        p95_total = statistics.quantiles(total_times, n=20)[18]  # 95th percentile

        # Performance assertions
        assert avg_total < 500, f"Average warm start too slow: {avg_total}ms"
        assert avg_handler < 200, f"Average handler time too slow: {avg_handler}ms"
        assert p95_total < 800, f"P95 warm start too slow: {p95_total}ms"

        return {
            "avg_total_ms": avg_total,
            "avg_handler_ms": avg_handler,
            "p95_total_ms": p95_total,
            "count": len(warm_start_times),
        }

    @pytest.mark.benchmark
    def test_throughput_performance(self, performance_container):
        """Test throughput under load."""
        import threading
        import queue

        results_queue = queue.Queue()
        num_requests = 10

        def invoke_worker(worker_id: int):
            try:
                result = self.invoke_lambda_timed(
                    {
                        "test": "throughput",
                        "worker_id": worker_id,
                        "timestamp": time.time(),
                    }
                )
                results_queue.put(("success", result, worker_id))
            except Exception as e:
                results_queue.put(("error", str(e), worker_id))

        # Start all requests simultaneously
        start_time = time.time()
        threads = []

        for i in range(num_requests):
            thread = threading.Thread(target=invoke_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=30)

        total_test_time = time.time() - start_time

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        successful_results = [r for r in results if r[0] == "success"]

        # Calculate throughput metrics
        success_rate = len(successful_results) / num_requests
        requests_per_second = (
            num_requests / total_test_time if total_test_time > 0 else 0
        )

        response_times = []
        for _, result, _ in successful_results:
            if result["statusCode"] == 200:
                response_times.append(result["_test_total_time_ms"])

        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Performance assertions
        assert success_rate >= 0.8, f"Success rate too low: {success_rate * 100}%"
        assert (
            avg_response_time < 1000
        ), f"Average response time too slow: {avg_response_time}ms"

        return {
            "success_rate": success_rate,
            "requests_per_second": requests_per_second,
            "avg_response_time_ms": avg_response_time,
            "total_requests": num_requests,
            "successful_requests": len(successful_results),
        }

    @pytest.mark.benchmark
    def test_memory_efficiency(self, performance_container):
        """Test memory usage efficiency."""
        # Test with varying payload sizes
        payload_sizes = [
            ("small", "x" * 100),  # 100 bytes
            ("medium", "x" * 10000),  # 10KB
            ("large", "x" * 100000),  # 100KB
        ]

        memory_results = []

        for size_name, payload_data in payload_sizes:
            result = self.invoke_lambda_timed(
                {"test": "memory_efficiency", "size": size_name, "data": payload_data}
            )

            assert result["statusCode"] == 200

            body = json.loads(result["body"])

            memory_results.append(
                {
                    "payload_size": size_name,
                    "payload_bytes": len(payload_data),
                    "execution_time_ms": result["_test_total_time_ms"],
                    "flush_success": body.get("flush_success", False),
                }
            )

        # Memory efficiency assertions
        for result in memory_results:
            assert result[
                "flush_success"
            ], f"Flush failed for {result['payload_size']} payload"

            # Execution time should scale reasonably with payload size
            if result["payload_size"] == "large":
                assert (
                    result["execution_time_ms"] < 3000
                ), "Large payload processing too slow"

        return memory_results

    @pytest.mark.benchmark
    def test_sdk_overhead(self, performance_container):
        """Measure SDK overhead compared to baseline."""
        # This would ideally compare with a version without SDK
        # For now, we measure the overhead components

        result = self.invoke_lambda_timed({"test": "overhead_measurement"})

        assert result["statusCode"] == 200

        body = json.loads(result["body"])
        timings = body.get("timings", {})

        # Extract SDK-specific timings
        sdk_overhead = {
            "import_time_ms": timings.get("sdk_import_ms", 0),
            "init_time_ms": timings.get("tracer_init_ms", 0),
            "flush_time_ms": timings.get("flush_time_ms", 0),
        }

        total_sdk_overhead = sum(sdk_overhead.values())
        total_execution = timings.get("handler_total_ms", 0)

        overhead_percentage = (
            (total_sdk_overhead / total_execution * 100) if total_execution > 0 else 0
        )

        # Overhead assertions
        assert (
            total_sdk_overhead < 150
        ), f"Total SDK overhead too high: {total_sdk_overhead}ms"
        assert (
            overhead_percentage < 30
        ), f"SDK overhead percentage too high: {overhead_percentage}%"

        return {
            "sdk_overhead_ms": total_sdk_overhead,
            "overhead_percentage": overhead_percentage,
            "breakdown": sdk_overhead,
        }


class TestLambdaStressTests:
    """Stress tests for Lambda environment."""

    def test_repeated_cold_starts(self):
        """Test performance under repeated cold starts."""
        client = docker.from_env()

        cold_start_results = []

        # Simulate multiple cold starts
        for i in range(3):
            container = client.containers.run(
                "public.ecr.aws/lambda/python:3.11",
                command="cold_start_test.lambda_handler",
                ports={"8080/tcp": None},
                volumes={
                    os.path.abspath("lambda_functions"): {
                        "bind": "/var/task",
                        "mode": "rw",
                    },
                    os.path.abspath("../../src"): {
                        "bind": "/var/task/honeyhive",
                        "mode": "ro",
                    },
                },
                environment={
                    "AWS_LAMBDA_FUNCTION_NAME": f"honeyhive-stress-test-{i}",
                    "HH_API_KEY": "test-key",
                },
                detach=True,
                remove=True,
            )

            try:
                # Get assigned port
                container.reload()
                port_info = container.ports.get("8080/tcp")
                if port_info:
                    port = port_info[0]["HostPort"]

                    time.sleep(2)  # Wait for startup

                    # Invoke Lambda
                    url = f"http://localhost:{port}/2015-03-31/functions/function/invocations"

                    start_time = time.time()
                    response = requests.post(
                        url,
                        json={"stress_test": i},
                        headers={"Content-Type": "application/json"},
                        timeout=30,
                    )
                    total_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        result = response.json()
                        body = json.loads(result["body"])

                        cold_start_results.append(
                            {
                                "iteration": i,
                                "total_time_ms": total_time,
                                "cold_start": body.get("cold_start", True),
                                "timings": body.get("timings", {}),
                            }
                        )

            finally:
                container.stop()

        # Analyze cold start consistency
        if cold_start_results:
            cold_start_times = [r["total_time_ms"] for r in cold_start_results]
            avg_cold_start = statistics.mean(cold_start_times)
            std_dev = (
                statistics.stdev(cold_start_times) if len(cold_start_times) > 1 else 0
            )

            # Cold starts should be consistent
            assert (
                std_dev < avg_cold_start * 0.3
            ), f"Cold start times too variable: {std_dev}ms std dev"
            assert (
                avg_cold_start < 3000
            ), f"Average cold start too slow: {avg_cold_start}ms"

    def test_lambda_timeout_handling(self):
        """Test SDK behavior near Lambda timeout limits."""
        # This would test with very short timeouts to ensure graceful handling
        # For now, we test with reasonable timeouts and ensure completion

        client = docker.from_env()

        container = client.containers.run(
            "public.ecr.aws/lambda/python:3.11",
            command="basic_tracing.lambda_handler",
            ports={"8080/tcp": 9200},
            volumes={
                os.path.abspath("lambda_functions"): {
                    "bind": "/var/task",
                    "mode": "rw",
                },
                os.path.abspath("../../src"): {
                    "bind": "/var/task/honeyhive",
                    "mode": "ro",
                },
            },
            environment={
                "AWS_LAMBDA_FUNCTION_NAME": "honeyhive-timeout-test",
                "AWS_LAMBDA_FUNCTION_TIMEOUT": "5",  # 5 second timeout
                "HH_API_KEY": "test-key",
            },
            detach=True,
            remove=True,
        )

        try:
            time.sleep(2)

            # Test that operations complete well within timeout
            url = "http://localhost:9200/2015-03-31/functions/function/invocations"

            start_time = time.time()
            response = requests.post(
                url,
                json={"test": "timeout_handling", "work_duration": 1.0},
                headers={"Content-Type": "application/json"},
                timeout=4,  # Less than Lambda timeout
            )
            execution_time = time.time() - start_time

            assert response.status_code == 200, "Should complete before timeout"
            assert execution_time < 3.0, f"Execution took too long: {execution_time}s"

            result = response.json()
            body = json.loads(result["body"])
            assert body.get(
                "flush_success", False
            ), "Should successfully flush before timeout"

        finally:
            container.stop()
