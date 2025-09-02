"""Performance tests for HoneyHive SDK in AWS Lambda environment."""

import json
import os
import statistics
import subprocess
import time
from typing import Any, Dict, List

import docker
import pytest
import requests


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
                "HH_TEST_MODE": "true",
            },
            detach=True,
            remove=True,
        )

        # Wait for container to be ready with health check
        self._wait_for_performance_container_ready(port=9100, timeout=30)

        yield container

        try:
            container.stop()
        except:
            pass

    def _wait_for_performance_container_ready(self, port: int = 9100, timeout: int = 30) -> None:
        """Wait for performance Lambda container to be ready."""
        import time
        import requests
        
        url = f"http://localhost:{port}/2015-03-31/functions/function/invocations"
        start_time = time.time()
        
        print(f"⏳ Waiting for performance container on port {port}...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.post(
                    url, 
                    json={"health_check": True}, 
                    headers={"Content-Type": "application/json"}, 
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✅ Performance container ready after {time.time() - start_time:.2f}s")
                    return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                time.sleep(2)
                continue
            except Exception as e:
                print(f"⚠️ Unexpected error during performance health check: {e}")
                time.sleep(2)
                continue
        
        raise Exception(f"Performance container failed to become ready within {timeout} seconds")

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

        # Performance assertions - Updated for realistic CI/dev environment expectations
        assert (
            metrics["sdk_import_ms"] < 500
        ), f"SDK import too slow: {metrics['sdk_import_ms']}ms (expected <500ms)"
        assert (
            metrics["tracer_init_ms"] < 300
        ), f"Tracer init too slow: {metrics['tracer_init_ms']}ms (expected <300ms)"
        assert (
            metrics["total_time_ms"] < 5000
        ), f"Total time too slow: {metrics['total_time_ms']}ms (expected <5000ms)"

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

        # Performance assertions - Updated for realistic expectations
        assert avg_total < 2000, f"Average warm start too slow: {avg_total}ms (expected <2000ms)"
        assert avg_handler < 1000, f"Average handler time too slow: {avg_handler}ms (expected <1000ms)"
        assert p95_total < 3000, f"P95 warm start too slow: {p95_total}ms (expected <3000ms)"

        return {
            "avg_total_ms": avg_total,
            "avg_handler_ms": avg_handler,
            "p95_total_ms": p95_total,
            "count": len(warm_start_times),
        }

    @pytest.mark.benchmark
    def test_throughput_performance(self, performance_container):
        """Test throughput with sequential rapid requests."""
        # Use sequential requests instead of threading to avoid connection issues
        results = []
        num_requests = 10
        
        # Run requests sequentially with minimal delay
        start_time = time.time()
        for i in range(num_requests):
            try:
                result = self.invoke_lambda_timed(
                    {
                        "test": "throughput",
                        "worker_id": i,
                        "timestamp": time.time(),
                    }
                )
                results.append(("success", result, i))
                time.sleep(0.05)  # Brief pause to avoid overwhelming container
            except Exception as e:
                print(f"Throughput request {i} failed: {type(e).__name__}: {str(e)}")
                results.append(("error", str(e), i))
                
        total_test_time = time.time() - start_time
        
        successful_results = [r for r in results if r[0] == "success"]
        success_rate = len(successful_results) / num_requests
        requests_per_second = num_requests / total_test_time if total_test_time > 0 else 0
        
        # Calculate response times
        response_times = []
        for _, result, _ in successful_results:
            if result["statusCode"] == 200:
                response_times.append(result["_test_total_time_ms"])
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Performance assertions
        assert success_rate >= 0.8, f"Success rate too low: {success_rate * 100}% (expected >=80%)"
        
        if response_times:
            assert avg_response_time < 3000, f"Average response time too slow: {avg_response_time}ms"

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
            # Retry logic for transient connection issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = self.invoke_lambda_timed(
                        {"test": "memory_efficiency", "size": size_name, "data": payload_data}
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e)
                    print(f"Memory efficiency test attempt {attempt + 1}/{max_retries} failed: {type(e).__name__}: {error_str}")
                    
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(f"Memory efficiency test for {size_name} failed after {max_retries} attempts. Last error: {error_str}")
                    
                    # Wait before retry
                    import time
                    time.sleep(1 + attempt)  # 1s, 2s, 3s

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

        # Retry logic for transient connection issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.invoke_lambda_timed({"test": "overhead_measurement"})
                break  # Success, exit retry loop
            except Exception as e:
                error_str = str(e)
                print(f"SDK overhead test attempt {attempt + 1}/{max_retries} failed: {type(e).__name__}: {error_str}")
                
                if attempt == max_retries - 1:  # Last attempt
                    raise Exception(f"SDK overhead test failed after {max_retries} attempts. Last error: {error_str}")
                
                # Wait before retry
                import time
                time.sleep(1 + attempt)  # 1s, 2s, 3s

        assert result["statusCode"] == 200

        body = json.loads(result["body"])
        timings = body.get("timings", {})

        # Extract SDK-specific timings
        sdk_overhead = {
            "import_time_ms": timings.get("sdk_import_ms", 0),
            "init_time_ms": timings.get("tracer_init_ms", 0),
            "flush_time_ms": timings.get("flush_time_ms", 0),
        }

        # Calculate meaningful overhead metrics
        cold_start_overhead = sdk_overhead["import_time_ms"] + sdk_overhead["init_time_ms"]
        runtime_overhead = sdk_overhead["flush_time_ms"]  # Per-request overhead
        total_execution = timings.get("handler_total_ms", 0)
        work_time = timings.get("work_time_ms", total_execution)

        # Runtime overhead percentage (more meaningful)
        runtime_overhead_percentage = (
            (runtime_overhead / work_time * 100) if work_time > 0 else 0
        )

        # Overhead assertions - Fixed to be meaningful
        assert (
            cold_start_overhead < 500
        ), f"Cold start overhead too high: {cold_start_overhead}ms (expected <500ms for SDK import + init)"
        
        assert (
            runtime_overhead < 50
        ), f"Runtime overhead too high: {runtime_overhead}ms (expected <50ms per request)"
        
        assert (
            runtime_overhead_percentage < 10
        ), f"Runtime overhead percentage too high: {runtime_overhead_percentage:.1f}% (expected <10% of work time)"

        return {
            "cold_start_overhead_ms": cold_start_overhead,
            "runtime_overhead_ms": runtime_overhead,
            "runtime_overhead_percentage": runtime_overhead_percentage,
            "breakdown": sdk_overhead,
            "measurement_note": "Cold start overhead is one-time, runtime overhead is per-request"
        }

    @pytest.mark.benchmark
    def test_comprehensive_sdk_overhead(self):
        """Comprehensive SDK overhead measurement with statistical significance and minimal variance."""
        client = docker.from_env()
        
        # Use dedicated SDK overhead test container
        container = client.containers.run(
            "honeyhive-lambda:bundle-native",
            command="sdk_overhead_test.lambda_handler",
            ports={"8080/tcp": None},
            environment={
                "HH_API_KEY": "test-key",
                "HH_PROJECT": "overhead-test",
                "HH_TEST_MODE": "true",
            },
            detach=True,
            remove=True,
        )

        try:
            # Get assigned port
            container.reload()
            port_info = container.ports.get("8080/tcp")
            assert port_info, "Container port mapping failed"
            port = port_info[0]["HostPort"]

            # Wait for container to be ready
            self._wait_for_comprehensive_overhead_container_ready(port=port, timeout=30)

            # Test multiple work durations to validate overhead scaling
            test_scenarios = [
                {"work_duration_ms": 10, "name": "minimal_work"},
                {"work_duration_ms": 50, "name": "standard_work"},
                {"work_duration_ms": 100, "name": "extended_work"},
            ]
            
            results = {}
            
            for scenario in test_scenarios:
                url = f"http://localhost:{port}/2015-03-31/functions/function/invocations"
                
                # Multiple measurements for statistical significance
                measurements = []
                for run in range(3):
                    response = requests.post(
                        url,
                        json=scenario,
                        headers={"Content-Type": "application/json"},
                        timeout=30,
                    )
                    
                    assert response.status_code == 200, f"Request failed: {response.text}"
                    
                    result = response.json()
                    body = json.loads(result["body"])
                    measurements.append(body)
                    
                    # Small delay between measurements
                    time.sleep(0.1)
                
                # Analyze measurements for this scenario
                overhead_percentages = [
                    m["overhead_analysis"]["overhead_vs_work_percentage"] 
                    for m in measurements
                ]
                per_span_overheads = [
                    m["overhead_analysis"]["avg_per_span_overhead_ms"]
                    for m in measurements
                ]
                coefficients_of_variation = [
                    m["overhead_analysis"]["coefficient_of_variation"]
                    for m in measurements
                ]
                
                scenario_stats = {
                    "overhead_percentage": {
                        "mean": statistics.mean(overhead_percentages),
                        "std_dev": statistics.stdev(overhead_percentages) if len(overhead_percentages) > 1 else 0,
                        "values": overhead_percentages,
                    },
                    "per_span_overhead_ms": {
                        "mean": statistics.mean(per_span_overheads),
                        "std_dev": statistics.stdev(per_span_overheads) if len(per_span_overheads) > 1 else 0,
                        "values": per_span_overheads,
                    },
                    "measurement_stability": {
                        "avg_coefficient_of_variation": statistics.mean(coefficients_of_variation),
                        "measurement_count": len(measurements),
                    },
                    "sample_result": measurements[0],  # Include one full result for reference
                }
                
                results[scenario["name"]] = scenario_stats

            # Comprehensive assertions across all scenarios
            for scenario_name, stats in results.items():
                work_duration = next(s["work_duration_ms"] for s in test_scenarios if s["name"] == scenario_name)
                
                # Per-span overhead should be reasonable
                avg_per_span = stats["per_span_overhead_ms"]["mean"]
                assert avg_per_span < 5.0, (
                    f"{scenario_name}: Per-span overhead too high: {avg_per_span:.2f}ms "
                    f"(expected <5.0ms per span)"
                )
                
                # Overhead percentage should decrease with longer work
                avg_percentage = stats["overhead_percentage"]["mean"]
                if work_duration >= 50:  # Only assert for substantial work
                    assert avg_percentage < 20.0, (
                        f"{scenario_name}: Overhead percentage too high: {avg_percentage:.1f}% "
                        f"(expected <20% for {work_duration}ms work)"
                    )
                
                # Measurement variance should be low (good test stability)
                percentage_variance = stats["overhead_percentage"]["std_dev"]
                assert percentage_variance < 5.0, (
                    f"{scenario_name}: Overhead measurement too variable: {percentage_variance:.1f}% std dev "
                    f"(expected <5% for stable measurements)"
                )
                
                # SDK internal measurements should be stable
                avg_cv = stats["measurement_stability"]["avg_coefficient_of_variation"]
                assert avg_cv < 50.0, (
                    f"{scenario_name}: SDK internal measurements too variable: {avg_cv:.1f}% CV "
                    f"(expected <50% coefficient of variation)"
                )

            # Cold start overhead validation (from any scenario)
            sample_init = results["standard_work"]["sample_result"]["initialization_overhead"]
            cold_start_overhead = sample_init["total_init_ms"]
            if cold_start_overhead > 0:
                assert cold_start_overhead < 500, (
                    f"Cold start overhead too high: {cold_start_overhead:.1f}ms "
                    f"(expected <500ms for SDK import + init)"
                )

            return {
                "test_scenarios": results,
                "summary": {
                    "avg_per_span_overhead_ms": statistics.mean([
                        stats["per_span_overhead_ms"]["mean"] for stats in results.values()
                    ]),
                    "overhead_scales_with_work": (
                        results["minimal_work"]["overhead_percentage"]["mean"] >
                        results["extended_work"]["overhead_percentage"]["mean"]
                    ),
                    "measurement_stability": "high" if all(
                        stats["overhead_percentage"]["std_dev"] < 3.0 
                        for stats in results.values()
                    ) else "moderate",
                },
                "cold_start_overhead_ms": cold_start_overhead,
            }

        finally:
            container.stop()

    def _wait_for_comprehensive_overhead_container_ready(self, port: int, timeout: int = 30):
        """Wait for comprehensive overhead container to be ready with health checking."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.post(
                    f"http://localhost:{port}/2015-03-31/functions/function/invocations",
                    json={"work_duration_ms": 1},  # Minimal test
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )
                if response.status_code in [200, 500]:  # Accept both success and handler errors
                    print(f"✅ Comprehensive overhead container ready on port {port}")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        
        raise Exception(f"Comprehensive overhead container not ready after {timeout}s")


class TestLambdaStressTests:
    """Stress tests for Lambda environment."""

    def _wait_for_timeout_container_ready(self, port: int = 9200, timeout: int = 30) -> None:
        """Wait for timeout test container to be ready."""
        import time
        import requests
        
        url = f"http://localhost:{port}/2015-03-31/functions/function/invocations"
        start_time = time.time()
        
        print(f"⏳ Waiting for timeout test container on port {port}...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.post(
                    url, 
                    json={"health_check": True}, 
                    headers={"Content-Type": "application/json"}, 
                    timeout=5
                )
                if response.status_code in [200, 502]:  # 502 is also acceptable for initial connection
                    print(f"✅ Timeout test container ready after {time.time() - start_time:.2f}s")
                    return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                time.sleep(2)
                continue
            except Exception as e:
                print(f"⚠️ Unexpected error during timeout test health check: {e}")
                time.sleep(2)
                continue
        
        raise Exception(f"Timeout test container failed to become ready within {timeout} seconds")

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

            # Cold starts should be reasonably consistent (allowing for container startup variance)
            assert (
                std_dev < avg_cold_start * 0.5
            ), f"Cold start times too variable: {std_dev}ms std dev (avg: {avg_cold_start:.1f}ms)"
            assert (
                avg_cold_start < 3000
            ), f"Average cold start too slow: {avg_cold_start}ms"

    def test_lambda_timeout_handling(self):
        """Test SDK behavior near Lambda timeout limits."""
        # This would test with very short timeouts to ensure graceful handling
        # For now, we test with reasonable timeouts and ensure completion

        client = docker.from_env()

        # Use our pre-built container instead of the base ECR image
        container = client.containers.run(
            "honeyhive-lambda:bundle-native",
            command="working_sdk_test.lambda_handler",
            ports={"8080/tcp": 9200},
            environment={
                "AWS_LAMBDA_FUNCTION_NAME": "honeyhive-timeout-test",
                "AWS_LAMBDA_FUNCTION_TIMEOUT": "10",  # 10 second timeout
                "HH_API_KEY": "test-key",
                "HH_PROJECT": "timeout-test",
                "HH_SOURCE": "timeout-test",
                "HH_TEST_MODE": "true",
            },
            detach=True,
            remove=True,
        )

        try:
            # Wait for container to be ready
            self._wait_for_timeout_container_ready(port=9200, timeout=30)

            # Test that operations complete well within timeout
            url = "http://localhost:9200/2015-03-31/functions/function/invocations"

            # Test with proper payload that the handler expects
            start_time = time.time()
            
            # Use retry logic for connection stability
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        url,
                        json={"test": "timeout_handling", "work_duration": 1.0},
                        headers={"Content-Type": "application/json"},
                        timeout=8,  # Less than Lambda timeout
                    )
                    execution_time = time.time() - start_time
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e)
                    print(f"Timeout test attempt {attempt + 1}/{max_retries} failed: {type(e).__name__}: {error_str}")
                    
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(f"Timeout test failed after {max_retries} attempts. Last error: {error_str}")
                    
                    time.sleep(1 + attempt)  # 1s, 2s, 3s

            assert response.status_code == 200, f"Should complete before timeout, got {response.status_code}"
            assert execution_time < 8.0, f"Execution took too long: {execution_time}s (expected <8s)"

            result = response.json()
            body = json.loads(result["body"])
            assert body.get(
                "flush_success", False
            ), "Should successfully flush before timeout"

        finally:
            container.stop()
