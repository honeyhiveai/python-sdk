Performance Testing & Benchmarking
==================================

.. note::
   **Problem-solving guide for performance testing HoneyHive SDK**
   
   Comprehensive solutions for measuring, validating, and optimizing HoneyHive SDK performance across different environments and workloads.

Performance testing ensures that HoneyHive SDK meets your application's performance requirements and identifies potential bottlenecks before they impact production.

Quick Start
-----------

**Problem**: I need to quickly test if HoneyHive SDK adds acceptable overhead.

**Solution**:

.. code-block:: python

   import time
   import statistics
   from honeyhive import HoneyHiveTracer, trace
   
   def quick_performance_test():
       """Quick performance impact assessment."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",      # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       
       # Baseline measurement
       def baseline_operation():
           return sum(range(1000))
       
       baseline_times = []
       for _ in range(10):
           start = time.perf_counter()
           baseline_operation()
           end = time.perf_counter()
           baseline_times.append(end - start)
       
       # Traced measurement
       @trace(tracer=tracer)
       def traced_operation():
           return sum(range(1000))
       
       traced_times = []
       for _ in range(10):
           start = time.perf_counter()
           traced_operation()
           end = time.perf_counter()
           traced_times.append(end - start)
       
       # Calculate overhead
       baseline_avg = statistics.mean(baseline_times)
       traced_avg = statistics.mean(traced_times)
       overhead_ratio = traced_avg / baseline_avg
       
       print(f"Baseline average: {baseline_avg * 1000:.2f}ms")
       print(f"Traced average: {traced_avg * 1000:.2f}ms")
       print(f"Overhead ratio: {overhead_ratio:.2f}x")
       
       # Acceptable overhead: < 2x for most applications
       assert overhead_ratio < 2.0, f"Overhead too high: {overhead_ratio:.2f}x"
       
       return {
           "baseline_ms": baseline_avg * 1000,
           "traced_ms": traced_avg * 1000, 
           "overhead_ratio": overhead_ratio
       }
   
   # Run the test
   results = quick_performance_test()
   print(f"✅ Performance test passed: {results['overhead_ratio']:.2f}x overhead")

Performance Testing Framework
-----------------------------

**Problem**: Set up comprehensive performance testing infrastructure.

**Solution - Performance Test Framework**:

.. code-block:: python

   """Comprehensive performance testing framework for HoneyHive SDK."""
   
   import time
   import statistics
   import threading
   import asyncio
   import psutil
   import os
   from typing import Dict, List, Any, Callable
   from dataclasses import dataclass
   from honeyhive import HoneyHiveTracer, trace
   
   @dataclass
   class PerformanceMetrics:
       """Performance measurement results."""
       avg_time_ms: float
       std_dev_ms: float
       min_time_ms: float
       max_time_ms: float
       p95_time_ms: float
       p99_time_ms: float
       throughput_ops_per_sec: float
       memory_usage_mb: float
       
   class PerformanceTester:
       """Performance testing framework."""
       
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
           self.results = {}
       
       def measure_function_performance(
           self,
           func: Callable,
           iterations: int = 100,
           warmup_iterations: int = 10,
           name: str = None
       ) -> PerformanceMetrics:
           """Measure function performance with statistical analysis."""
           
           name = name or func.__name__
           
           # Warmup runs
           for _ in range(warmup_iterations):
               func()
           
           # Measurement runs
           times = []
           initial_memory = self._get_memory_usage()
           
           for _ in range(iterations):
               start = time.perf_counter()
               func()
               end = time.perf_counter()
               times.append(end - start)
           
           final_memory = self._get_memory_usage()
           memory_delta = final_memory - initial_memory
           
           # Calculate statistics
           times_ms = [t * 1000 for t in times]
           avg_time = statistics.mean(times_ms)
           std_dev = statistics.stdev(times_ms) if len(times_ms) > 1 else 0
           min_time = min(times_ms)
           max_time = max(times_ms)
           
           # Calculate percentiles
           sorted_times = sorted(times_ms)
           p95_index = int(0.95 * len(sorted_times))
           p99_index = int(0.99 * len(sorted_times))
           p95_time = sorted_times[p95_index]
           p99_time = sorted_times[p99_index]
           
           # Calculate throughput
           total_time = sum(times)
           throughput = iterations / total_time if total_time > 0 else 0
           
           metrics = PerformanceMetrics(
               avg_time_ms=avg_time,
               std_dev_ms=std_dev,
               min_time_ms=min_time,
               max_time_ms=max_time,
               p95_time_ms=p95_time,
               p99_time_ms=p99_time,
               throughput_ops_per_sec=throughput,
               memory_usage_mb=memory_delta
           )
           
           self.results[name] = metrics
           return metrics
       
       def compare_performance(
           self,
           baseline_func: Callable,
           traced_func: Callable,
           iterations: int = 100,
           name: str = "comparison"
       ) -> Dict[str, Any]:
           """Compare performance between baseline and traced functions."""
           
           baseline_metrics = self.measure_function_performance(
               baseline_func, iterations, name=f"{name}_baseline"
           )
           
           traced_metrics = self.measure_function_performance(
               traced_func, iterations, name=f"{name}_traced"
           )
           
           overhead_ratio = traced_metrics.avg_time_ms / baseline_metrics.avg_time_ms
           throughput_ratio = traced_metrics.throughput_ops_per_sec / baseline_metrics.throughput_ops_per_sec
           
           comparison = {
               "baseline": baseline_metrics,
               "traced": traced_metrics,
               "overhead_ratio": overhead_ratio,
               "throughput_ratio": throughput_ratio,
               "is_acceptable": overhead_ratio < 2.0,  # Configurable threshold
               "memory_overhead_mb": traced_metrics.memory_usage_mb - baseline_metrics.memory_usage_mb
           }
           
           self.results[f"{name}_comparison"] = comparison
           return comparison
       
       def measure_concurrent_performance(
           self,
           func: Callable,
           num_threads: int = 10,
           operations_per_thread: int = 50
       ) -> Dict[str, Any]:
           """Measure performance under concurrent load."""
           
           results = []
           errors = []
           
           def worker():
               """Worker thread function."""
               thread_results = []
               try:
                   for _ in range(operations_per_thread):
                       start = time.perf_counter()
                       func()
                       end = time.perf_counter()
                       thread_results.append(end - start)
                   results.extend(thread_results)
               except Exception as e:
                   errors.append(e)
           
           # Start concurrent workers
           start_time = time.perf_counter()
           threads = []
           
           for _ in range(num_threads):
               thread = threading.Thread(target=worker)
               threads.append(thread)
               thread.start()
           
           # Wait for completion
           for thread in threads:
               thread.join()
           
           end_time = time.perf_counter()
           total_time = end_time - start_time
           
           # Calculate concurrent metrics
           if results:
               times_ms = [t * 1000 for t in results]
               avg_time = statistics.mean(times_ms)
               total_operations = len(results)
               throughput = total_operations / total_time
               error_rate = len(errors) / (total_operations + len(errors))
           else:
               avg_time = 0
               throughput = 0
               error_rate = 1.0
           
           concurrent_metrics = {
               "num_threads": num_threads,
               "operations_per_thread": operations_per_thread,
               "total_operations": len(results),
               "avg_time_ms": avg_time,
               "total_time_s": total_time,
               "throughput_ops_per_sec": throughput,
               "error_count": len(errors),
               "error_rate": error_rate,
               "errors": [str(e) for e in errors[:5]]  # First 5 errors
           }
           
           self.results["concurrent_performance"] = concurrent_metrics
           return concurrent_metrics
       
       def _get_memory_usage(self) -> float:
           """Get current memory usage in MB."""
           process = psutil.Process(os.getpid())
           return process.memory_info().rss / 1024 / 1024
       
       def generate_report(self) -> str:
           """Generate performance test report."""
           report = ["Performance Test Report", "=" * 25, ""]
           
           for name, result in self.results.items():
               report.append(f"## {name}")
               if isinstance(result, PerformanceMetrics):
                   report.extend([
                       f"Average Time: {result.avg_time_ms:.2f}ms",
                       f"Std Deviation: {result.std_dev_ms:.2f}ms",
                       f"P95: {result.p95_time_ms:.2f}ms",
                       f"P99: {result.p99_time_ms:.2f}ms",
                       f"Throughput: {result.throughput_ops_per_sec:.2f} ops/sec",
                       f"Memory Usage: {result.memory_usage_mb:.2f}MB",
                       ""
                   ])
               elif "comparison" in name:
                   report.extend([
                       f"Overhead Ratio: {result['overhead_ratio']:.2f}x",
                       f"Throughput Ratio: {result['throughput_ratio']:.2f}x",
                       f"Acceptable: {'✅' if result['is_acceptable'] else '❌'}",
                       f"Memory Overhead: {result['memory_overhead_mb']:.2f}MB",
                       ""
                   ])
           
           return "\n".join(report)

**Using the Performance Framework**:

.. code-block:: python

   def test_comprehensive_performance():
       """Comprehensive performance test using the framework."""
       tracer = HoneyHiveTracer.init(
           api_key="perf-test-key", # Or set HH_API_KEY environment variable
           project="perf-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       
       tester = PerformanceTester(tracer)
       
       # Define test functions
       def baseline_computation():
           return sum(i * i for i in range(100))
       
       @trace(tracer=tracer)
       def traced_computation():
           return sum(i * i for i in range(100))
       
       # Run performance comparisons
       comparison = tester.compare_performance(
           baseline_computation,
           traced_computation,
           iterations=200,
           name="computation_test"
       )
       
       # Test concurrent performance
       concurrent_results = tester.measure_concurrent_performance(
           traced_computation,
           num_threads=5,
           operations_per_thread=20
       )
       
       # Generate and print report
       report = tester.generate_report()
       print(report)
       
       # Assert performance requirements
       assert comparison["overhead_ratio"] < 2.0
       assert concurrent_results["error_rate"] < 0.01
       assert concurrent_results["throughput_ops_per_sec"] > 100

Memory Performance Testing
--------------------------

**Problem**: Test memory usage and detect memory leaks.

**Solution - Memory Testing Framework**:

.. code-block:: python

   """Memory performance testing for HoneyHive SDK."""
   
   import gc
   import psutil
   import os
   import time
   from typing import List, Dict
   from honeyhive import HoneyHiveTracer
   
   class MemoryTester:
       """Memory usage testing framework."""
       
       def __init__(self):
           self.process = psutil.Process(os.getpid())
           self.baseline_memory = None
       
       def start_monitoring(self):
           """Start memory monitoring baseline."""
           gc.collect()  # Force garbage collection
           time.sleep(0.1)  # Allow GC to complete
           self.baseline_memory = self.process.memory_info().rss / 1024 / 1024
       
       def measure_memory_usage(self) -> float:
           """Get current memory usage in MB."""
           return self.process.memory_info().rss / 1024 / 1024
       
       def test_tracer_memory_usage(self, num_tracers: int = 10) -> Dict[str, float]:
           """Test memory usage with multiple tracers."""
           self.start_monitoring()
           initial_memory = self.measure_memory_usage()
           
           tracers = []
           for i in range(num_tracers):
               tracer = HoneyHiveTracer.init(
                   api_key=f"memory-test-key-{i}",  # Unique API key for each tracer instance
                   project=f"memory-project-{i}",   # Unique project for each tracer instance
                   test_mode=True                    # Or set HH_TEST_MODE=true
               )
               tracers.append(tracer)
               
               # Create some spans
               for j in range(10):
                   with tracer.trace(f"memory-span-{j}") as span:
                       span.set_attribute("iteration", j)
                       span.set_attribute("tracer_id", i)
           
           after_creation_memory = self.measure_memory_usage()
           
           # Clean up tracers
           for tracer in tracers:
               tracer.close()
           
           del tracers
           gc.collect()
           time.sleep(0.1)
           
           after_cleanup_memory = self.measure_memory_usage()
           
           return {
               "initial_mb": initial_memory,
               "after_creation_mb": after_creation_memory,
               "after_cleanup_mb": after_cleanup_memory,
               "peak_usage_mb": after_creation_memory - initial_memory,
               "memory_leak_mb": after_cleanup_memory - initial_memory,
               "memory_per_tracer_mb": (after_creation_memory - initial_memory) / num_tracers
           }
       
       def test_span_memory_growth(self, num_spans: int = 1000) -> Dict[str, float]:
           """Test memory growth with many spans."""
           tracer = HoneyHiveTracer.init(
               api_key="span-memory-test",  # Or set HH_API_KEY environment variable
               project="span-memory-project", # Or set HH_PROJECT environment variable
               test_mode=True               # Or set HH_TEST_MODE=true
           )
           
           self.start_monitoring()
           initial_memory = self.measure_memory_usage()
           
           memory_samples = []
           sample_interval = max(1, num_spans // 10)  # Sample 10 times
           
           for i in range(num_spans):
               with tracer.trace(f"memory-test-span-{i}") as span:
                   span.set_attribute("span.index", i)
                   span.set_attribute("span.data", f"data-{i}" * 10)  # Some data
               
               if i % sample_interval == 0:
                   memory_samples.append(self.measure_memory_usage())
           
           final_memory = self.measure_memory_usage()
           
           # Calculate memory growth
           if len(memory_samples) > 1:
               memory_growth_rate = (memory_samples[-1] - memory_samples[0]) / len(memory_samples)
           else:
               memory_growth_rate = 0
           
           tracer.close()
           
           return {
               "initial_mb": initial_memory,
               "final_mb": final_memory,
               "total_growth_mb": final_memory - initial_memory,
               "memory_per_span_kb": (final_memory - initial_memory) * 1024 / num_spans,
               "memory_growth_rate_mb": memory_growth_rate,
               "memory_samples": memory_samples
           }
       
       def test_long_running_memory_stability(self, duration_seconds: int = 60) -> Dict[str, Any]:
           """Test memory stability over time."""
           tracer = HoneyHiveTracer.init(
               api_key="stability-test",    # Or set HH_API_KEY environment variable
               project="stability-project", # Or set HH_PROJECT environment variable
               test_mode=True               # Or set HH_TEST_MODE=true
           )
           
           self.start_monitoring()
           start_time = time.time()
           memory_samples = []
           
           span_count = 0
           while time.time() - start_time < duration_seconds:
               with tracer.trace(f"stability-span-{span_count}") as span:
                   span.set_attribute("timestamp", time.time())
                   span_count += 1
               
               # Sample memory every second
               if span_count % 10 == 0:  # Assuming ~10 spans per second
                   memory_samples.append({
                       "time": time.time() - start_time,
                       "memory_mb": self.measure_memory_usage(),
                       "span_count": span_count
                   })
               
               time.sleep(0.1)  # ~10 spans per second
           
           tracer.close()
           
           # Analyze memory stability
           memories = [sample["memory_mb"] for sample in memory_samples]
           if memories:
               avg_memory = sum(memories) / len(memories)
               max_memory = max(memories)
               min_memory = min(memories)
               memory_variance = max_memory - min_memory
           else:
               avg_memory = max_memory = min_memory = memory_variance = 0
           
           return {
               "duration_seconds": duration_seconds,
               "span_count": span_count,
               "memory_samples": memory_samples,
               "avg_memory_mb": avg_memory,
               "max_memory_mb": max_memory,
               "min_memory_mb": min_memory,
               "memory_variance_mb": memory_variance,
               "spans_per_second": span_count / duration_seconds
           }

**Running Memory Tests**:

.. code-block:: python

   def test_memory_performance():
       """Run comprehensive memory performance tests."""
       tester = MemoryTester()
       
       # Test multiple tracers
       tracer_memory = tester.test_tracer_memory_usage(num_tracers=5)
       print(f"Memory per tracer: {tracer_memory['memory_per_tracer_mb']:.2f}MB")
       print(f"Memory leak: {tracer_memory['memory_leak_mb']:.2f}MB")
       
       # Test span memory growth
       span_memory = tester.test_span_memory_growth(num_spans=500)
       print(f"Memory per span: {span_memory['memory_per_span_kb']:.2f}KB")
       
       # Test long-running stability
       stability = tester.test_long_running_memory_stability(duration_seconds=30)
       print(f"Memory variance: {stability['memory_variance_mb']:.2f}MB")
       
       # Assert memory requirements
       assert tracer_memory['memory_per_tracer_mb'] < 10.0  # < 10MB per tracer
       assert tracer_memory['memory_leak_mb'] < 1.0  # < 1MB leak
       assert span_memory['memory_per_span_kb'] < 5.0  # < 5KB per span
       assert stability['memory_variance_mb'] < 50.0  # < 50MB variance

Async Performance Testing
-------------------------

**Problem**: Test performance of async operations with HoneyHive.

**Solution - Async Performance Framework**:

.. code-block:: python

   """Async performance testing for HoneyHive SDK."""
   
   import asyncio
   import time
   import statistics
   from typing import List, Callable, Awaitable
   from honeyhive import HoneyHiveTracer, atrace
   
   class AsyncPerformanceTester:
       """Async performance testing framework."""
       
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
       
       async def measure_async_function(
           self,
           async_func: Callable[[], Awaitable],
           iterations: int = 100,
           concurrent_tasks: int = 1
       ) -> Dict[str, float]:
           """Measure async function performance."""
           
           async def timed_execution():
               start = time.perf_counter()
               await async_func()
               return time.perf_counter() - start
           
           # Run iterations with specified concurrency
           all_times = []
           
           for batch in range(0, iterations, concurrent_tasks):
               batch_size = min(concurrent_tasks, iterations - batch)
               
               # Create concurrent tasks
               tasks = [timed_execution() for _ in range(batch_size)]
               
               # Execute concurrently
               batch_times = await asyncio.gather(*tasks)
               all_times.extend(batch_times)
           
           # Calculate statistics
           times_ms = [t * 1000 for t in all_times]
           
           return {
               "avg_time_ms": statistics.mean(times_ms),
               "std_dev_ms": statistics.stdev(times_ms) if len(times_ms) > 1 else 0,
               "min_time_ms": min(times_ms),
               "max_time_ms": max(times_ms),
               "p95_time_ms": sorted(times_ms)[int(0.95 * len(times_ms))],
               "total_time_s": sum(all_times),
               "throughput_ops_per_sec": len(all_times) / sum(all_times) if sum(all_times) > 0 else 0
           }
       
       async def compare_async_performance(
           self,
           baseline_func: Callable[[], Awaitable],
           traced_func: Callable[[], Awaitable],
           iterations: int = 50,
           concurrent_tasks: int = 5
       ) -> Dict[str, Any]:
           """Compare async performance between baseline and traced functions."""
           
           baseline_metrics = await self.measure_async_function(
               baseline_func, iterations, concurrent_tasks
           )
           
           traced_metrics = await self.measure_async_function(
               traced_func, iterations, concurrent_tasks
           )
           
           overhead_ratio = traced_metrics["avg_time_ms"] / baseline_metrics["avg_time_ms"]
           
           return {
               "baseline": baseline_metrics,
               "traced": traced_metrics,
               "overhead_ratio": overhead_ratio,
               "is_acceptable": overhead_ratio < 2.0
           }

**Async Performance Test Example**:

.. code-block:: python

   from honeyhive.models import EventType
   
   async def test_async_performance():
       """Test async performance with HoneyHive tracing."""
       tracer = HoneyHiveTracer.init(
           api_key="async-test-key",    # Or set HH_API_KEY environment variable
           project="async-test-project", # Or set HH_PROJECT environment variable
           test_mode=True               # Or set HH_TEST_MODE=true
       )
       
       tester = AsyncPerformanceTester(tracer)
       
       # Define async test functions
       async def baseline_async_operation():
           await asyncio.sleep(0.01)  # Simulate async work
           return sum(range(100))
       
       @atrace(tracer=tracer, event_type=EventType.tool)
       async def traced_async_operation():
           await asyncio.sleep(0.01)  # Simulate async work
           return sum(range(100))
       
       # Compare performance
       comparison = await tester.compare_async_performance(
           baseline_async_operation,
           traced_async_operation,
           iterations=30,
           concurrent_tasks=10
       )
       
       print(f"Async overhead: {comparison['overhead_ratio']:.2f}x")
       print(f"Baseline throughput: {comparison['baseline']['throughput_ops_per_sec']:.2f} ops/sec")
       print(f"Traced throughput: {comparison['traced']['throughput_ops_per_sec']:.2f} ops/sec")
       
       # Assert performance requirements
       assert comparison["overhead_ratio"] < 1.5  # < 1.5x overhead for async
       assert comparison["traced"]["throughput_ops_per_sec"] > 50  # > 50 ops/sec

Load Testing
------------

**Problem**: Test performance under high load conditions.

**Solution - Load Testing Framework**:

.. code-block:: python

   """Load testing framework for HoneyHive SDK."""
   
   import time
   import threading
   import queue
   import statistics
   from typing import Dict, List, Any
   from honeyhive import HoneyHiveTracer, trace
   
   class LoadTester:
       """Load testing framework."""
       
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
           self.results = queue.Queue()
           self.errors = queue.Queue()
       
       def run_load_test(
           self,
           target_function: callable,
           num_threads: int = 10,
           duration_seconds: int = 60,
           ramp_up_seconds: int = 10
       ) -> Dict[str, Any]:
           """Run load test with gradual ramp-up."""
           
           start_time = time.time()
           end_time = start_time + duration_seconds
           ramp_up_interval = ramp_up_seconds / num_threads if num_threads > 0 else 0
           
           threads = []
           
           def worker(worker_id: int, start_delay: float):
               """Worker thread for load testing."""
               time.sleep(start_delay)  # Ramp-up delay
               
               while time.time() < end_time:
                   try:
                       operation_start = time.perf_counter()
                       target_function()
                       operation_end = time.perf_counter()
                       
                       self.results.put({
                           "worker_id": worker_id,
                           "timestamp": time.time(),
                           "duration_ms": (operation_end - operation_start) * 1000
                       })
                       
                   except Exception as e:
                       self.errors.put({
                           "worker_id": worker_id,
                           "timestamp": time.time(),
                           "error": str(e)
                       })
                   
                   # Small delay to prevent overwhelming
                   time.sleep(0.001)
           
           # Start workers with ramp-up
           for i in range(num_threads):
               start_delay = i * ramp_up_interval
               thread = threading.Thread(
                   target=worker,
                   args=(i, start_delay)
               )
               threads.append(thread)
               thread.start()
           
           # Wait for test completion
           for thread in threads:
               thread.join()
           
           # Collect results
           results = []
           while not self.results.empty():
               results.append(self.results.get())
           
           errors = []
           while not self.errors.empty():
               errors.append(self.errors.get())
           
           # Analyze results
           if results:
               durations = [r["duration_ms"] for r in results]
               avg_duration = statistics.mean(durations)
               p95_duration = sorted(durations)[int(0.95 * len(durations))]
               p99_duration = sorted(durations)[int(0.99 * len(durations))]
               
               total_operations = len(results)
               throughput = total_operations / duration_seconds
               error_rate = len(errors) / (total_operations + len(errors))
           else:
               avg_duration = p95_duration = p99_duration = 0
               total_operations = 0
               throughput = 0
               error_rate = 1.0
           
           return {
               "test_config": {
                   "num_threads": num_threads,
                   "duration_seconds": duration_seconds,
                   "ramp_up_seconds": ramp_up_seconds
               },
               "results": {
                   "total_operations": total_operations,
                   "total_errors": len(errors),
                   "error_rate": error_rate,
                   "avg_duration_ms": avg_duration,
                   "p95_duration_ms": p95_duration,
                   "p99_duration_ms": p99_duration,
                   "throughput_ops_per_sec": throughput
               },
               "raw_data": {
                   "operations": results,
                   "errors": errors[:10]  # First 10 errors
               }
           }

**Load Test Example**:

.. code-block:: python

   def test_high_load_performance():
       """Test performance under high load."""
       tracer = HoneyHiveTracer.init(
           api_key="load-test-key",     # Or set HH_API_KEY environment variable
           project="load-test-project", # Or set HH_PROJECT environment variable
           test_mode=True               # Or set HH_TEST_MODE=true
       )
       
       tester = LoadTester(tracer)
       
       @trace(tracer=tracer, event_type=EventType.tool)
       def load_test_operation():
           """Operation to test under load."""
           # Simulate realistic work
           data = list(range(50))
           result = sum(x * x for x in data)
           return result
       
       # Run load test
       load_results = tester.run_load_test(
           target_function=load_test_operation,
           num_threads=20,
           duration_seconds=30,
           ramp_up_seconds=5
       )
       
       print(f"Throughput: {load_results['results']['throughput_ops_per_sec']:.2f} ops/sec")
       print(f"Error Rate: {load_results['results']['error_rate']:.2%}")
       print(f"P95 Duration: {load_results['results']['p95_duration_ms']:.2f}ms")
       
       # Assert load test requirements
       assert load_results["results"]["error_rate"] < 0.01  # < 1% error rate
       assert load_results["results"]["throughput_ops_per_sec"] > 100  # > 100 ops/sec
       assert load_results["results"]["p95_duration_ms"] < 100  # P95 < 100ms

Lambda Performance Testing
--------------------------

**Problem**: Test Lambda-specific performance characteristics.

**Solution - Lambda Performance Framework** (extracted from comprehensive testing):

.. code-block:: python

   """Lambda-specific performance testing."""
   
   import docker
   import json
   import time
   import requests
   import statistics
   from typing import Dict, List
   
   class LambdaPerformanceTester:
       """Lambda performance testing framework."""
       
       def __init__(self, container_image: str = "honeyhive-lambda:bundle-native"):
           self.container_image = container_image
           self.container = None
       
       def start_lambda_container(self, memory_size: int = 256):
           """Start Lambda container for testing."""
           client = docker.from_env()
           
           self.container = client.containers.run(
               self.container_image,
               ports={"8080/tcp": 9000},
               environment={
                   "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": str(memory_size),
                   "HH_API_KEY": "test-key",
                   "HH_PROJECT": "lambda-perf-test",
                   "HH_TEST_MODE": "true"
               },
               detach=True,
               remove=True
           )
           
           # Wait for container startup
           time.sleep(3)
       
       def stop_lambda_container(self):
           """Stop Lambda container."""
           if self.container:
               try:
                   self.container.stop()
               except:
                   pass
               self.container = None
       
       def invoke_lambda(self, payload: Dict) -> Dict:
           """Invoke Lambda function and measure response time."""
           url = "http://localhost:9000/2015-03-31/functions/function/invocations"
           
           start_time = time.perf_counter()
           response = requests.post(
               url,
               json=payload,
               headers={"Content-Type": "application/json"},
               timeout=30
           )
           end_time = time.perf_counter()
           
           result = response.json()
           result["_total_time_ms"] = (end_time - start_time) * 1000
           
           return result
       
       def test_cold_start_performance(self, iterations: int = 5) -> Dict[str, Any]:
           """Test cold start performance."""
           cold_start_times = []
           
           for i in range(iterations):
               # Stop and start container to simulate cold start
               self.stop_lambda_container()
               time.sleep(1)
               self.start_lambda_container()
               
               # Invoke and measure
               result = self.invoke_lambda({"test": f"cold_start_{i}"})
               
               if result.get("statusCode") == 200:
                   body = json.loads(result["body"])
                   timings = body.get("timings", {})
                   cold_start_times.append({
                       "total_time_ms": result["_total_time_ms"],
                       "sdk_import_ms": timings.get("sdk_import_ms", 0),
                       "tracer_init_ms": timings.get("tracer_init_ms", 0),
                       "handler_total_ms": timings.get("handler_total_ms", 0)
                   })
           
           # Calculate cold start statistics
           if cold_start_times:
               total_times = [t["total_time_ms"] for t in cold_start_times]
               avg_cold_start = statistics.mean(total_times)
               p95_cold_start = sorted(total_times)[int(0.95 * len(total_times))]
           else:
               avg_cold_start = p95_cold_start = 0
           
           return {
               "iterations": iterations,
               "avg_cold_start_ms": avg_cold_start,
               "p95_cold_start_ms": p95_cold_start,
               "raw_measurements": cold_start_times,
               "meets_target": avg_cold_start < 500  # Target: < 500ms
           }
       
       def test_warm_start_performance(self, iterations: int = 10) -> Dict[str, Any]:
           """Test warm start performance."""
           # Ensure container is warm
           self.invoke_lambda({"test": "warmup"})
           
           warm_start_times = []
           for i in range(iterations):
               result = self.invoke_lambda({"test": f"warm_start_{i}"})
               
               if result.get("statusCode") == 200:
                   body = json.loads(result["body"])
                   warm_start_times.append({
                       "total_time_ms": result["_total_time_ms"],
                       "handler_total_ms": body.get("timings", {}).get("handler_total_ms", 0)
                   })
           
           # Calculate warm start statistics
           if warm_start_times:
               total_times = [t["total_time_ms"] for t in warm_start_times]
               avg_warm_start = statistics.mean(total_times)
               std_dev = statistics.stdev(total_times) if len(total_times) > 1 else 0
           else:
               avg_warm_start = std_dev = 0
           
           return {
               "iterations": iterations,
               "avg_warm_start_ms": avg_warm_start,
               "std_dev_ms": std_dev,
               "raw_measurements": warm_start_times,
               "meets_target": avg_warm_start < 100  # Target: < 100ms
           }

**Lambda Performance Test Usage**:

.. code-block:: python

   def test_lambda_performance_comprehensive():
       """Comprehensive Lambda performance test."""
       tester = LambdaPerformanceTester()
       
       try:
           # Test cold start performance
           cold_start_results = tester.test_cold_start_performance(iterations=3)
           print(f"Cold start average: {cold_start_results['avg_cold_start_ms']:.2f}ms")
           
           # Test warm start performance
           warm_start_results = tester.test_warm_start_performance(iterations=10)
           print(f"Warm start average: {warm_start_results['avg_warm_start_ms']:.2f}ms")
           
           # Assert performance targets
           assert cold_start_results["meets_target"], "Cold start target not met"
           assert warm_start_results["meets_target"], "Warm start target not met"
           
       finally:
           tester.stop_lambda_container()

Performance Testing Commands
----------------------------

**Running Performance Tests**:

.. code-block:: bash

   # Run all performance tests
   pytest tests/performance/ -v
   
   # Run specific performance test categories
   pytest tests/performance/ -m "benchmark" -v
   pytest tests/performance/ -m "memory" -v
   pytest tests/performance/ -m "load" -v
   pytest tests/performance/ -m "lambda" -v
   
   # Run performance tests with reporting
   pytest tests/performance/ --benchmark-json=performance_results.json
   
   # Run Lambda performance tests
   cd tests/lambda
   make test-performance
   
   # Run memory tests
   pytest tests/performance/test_memory.py -v -s
   
   # Run load tests
   pytest tests/performance/test_load.py -v --duration=30

**Performance Test Organization**:

.. code-block:: bash

   tests/performance/
   ├── test_basic_performance.py      # Basic overhead testing
   ├── test_memory_performance.py     # Memory usage testing
   ├── test_async_performance.py      # Async operation testing
   ├── test_load_performance.py       # High load testing
   ├── test_lambda_performance.py     # Lambda-specific testing
   ├── conftest.py                    # Performance test fixtures
   └── performance_utils.py           # Performance testing utilities

Performance Benchmarking
------------------------

**Problem**: Establish performance baselines and track regression.

**Solution - Benchmarking Framework**:

.. code-block:: python

   """Performance benchmarking and regression tracking."""
   
   import json
   import time
   from pathlib import Path
   from typing import Dict, Any, Optional
   
   class PerformanceBenchmark:
       """Performance benchmarking and regression tracking."""
       
       def __init__(self, benchmark_file: str = "performance_baselines.json"):
           self.benchmark_file = Path(benchmark_file)
           self.baselines = self._load_baselines()
       
       def _load_baselines(self) -> Dict[str, Any]:
           """Load existing performance baselines."""
           if self.benchmark_file.exists():
               with open(self.benchmark_file, 'r') as f:
                   return json.load(f)
           return {}
       
       def save_baselines(self):
           """Save performance baselines to file."""
           with open(self.benchmark_file, 'w') as f:
               json.dump(self.baselines, f, indent=2)
       
       def record_baseline(self, test_name: str, metrics: Dict[str, float]):
           """Record performance baseline for a test."""
           self.baselines[test_name] = {
               "metrics": metrics,
               "timestamp": time.time(),
               "version": "current"  # Could be git commit hash
           }
       
       def check_regression(
           self,
           test_name: str,
           current_metrics: Dict[str, float],
           threshold_percent: float = 20.0
       ) -> Dict[str, Any]:
           """Check for performance regression."""
           if test_name not in self.baselines:
               # No baseline, record current as baseline
               self.record_baseline(test_name, current_metrics)
               return {
                   "status": "baseline_recorded",
                   "message": f"Baseline recorded for {test_name}"
               }
           
           baseline = self.baselines[test_name]["metrics"]
           regressions = []
           improvements = []
           
           for metric, current_value in current_metrics.items():
               if metric in baseline:
                   baseline_value = baseline[metric]
                   if baseline_value > 0:
                       change_percent = ((current_value - baseline_value) / baseline_value) * 100
                       
                       if change_percent > threshold_percent:
                           regressions.append({
                               "metric": metric,
                               "baseline": baseline_value,
                               "current": current_value,
                               "change_percent": change_percent
                           })
                       elif change_percent < -5:  # Improvement threshold
                           improvements.append({
                               "metric": metric,
                               "baseline": baseline_value,
                               "current": current_value,
                               "change_percent": change_percent
                           })
           
           status = "regression" if regressions else "pass"
           if improvements and not regressions:
               status = "improvement"
           
           return {
               "status": status,
               "regressions": regressions,
               "improvements": improvements,
               "baseline": baseline,
               "current": current_metrics
           }

**Benchmark Usage Example**:

.. code-block:: python

   def test_with_benchmarking():
       """Performance test with regression checking."""
       benchmark = PerformanceBenchmark()
       
       # Run performance test
       tracer = HoneyHiveTracer.init(
           api_key="test",          # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       tester = PerformanceTester(tracer)
       
       # Measure performance
       metrics = tester.measure_function_performance(
           lambda: sum(range(1000)),
           iterations=100
       )
       
       # Check for regression
       regression_check = benchmark.check_regression(
           "basic_computation_test",
           {
               "avg_time_ms": metrics.avg_time_ms,
               "p95_time_ms": metrics.p95_time_ms,
               "throughput_ops_per_sec": metrics.throughput_ops_per_sec
           },
           threshold_percent=15.0  # 15% regression threshold
       )
       
       # Save updated baselines
       benchmark.save_baselines()
       
       # Assert no significant regression
       if regression_check["status"] == "regression":
           regression_details = regression_check["regressions"]
           raise AssertionError(f"Performance regression detected: {regression_details}")
       
       print(f"Performance check: {regression_check['status']}")

Performance Monitoring Integration
----------------------------------

**Problem**: Integrate performance testing with monitoring systems.

**Solution - Monitoring Integration**:

.. code-block:: python

   """Integration with monitoring systems for performance tracking."""
   
   import requests
   import time
   from typing import Dict, Any
   
   class PerformanceMonitor:
       """Performance monitoring integration."""
       
       def __init__(self, monitoring_endpoint: str = None):
           self.monitoring_endpoint = monitoring_endpoint
       
       def send_metrics(self, metrics: Dict[str, Any], tags: Dict[str, str] = None):
           """Send performance metrics to monitoring system."""
           if not self.monitoring_endpoint:
               return
           
           payload = {
               "timestamp": time.time(),
               "metrics": metrics,
               "tags": tags or {},
               "source": "honeyhive_performance_tests"
           }
           
           try:
               response = requests.post(
                   self.monitoring_endpoint,
                   json=payload,
                   timeout=5
               )
               response.raise_for_status()
           except Exception as e:
               print(f"Failed to send metrics: {e}")
       
       def create_alert(self, test_name: str, regression_info: Dict[str, Any]):
           """Create alert for performance regression."""
           alert_payload = {
               "alert_type": "performance_regression",
               "test_name": test_name,
               "severity": "warning",
               "details": regression_info,
               "timestamp": time.time()
           }
           
           if self.monitoring_endpoint:
               try:
                   requests.post(
                       f"{self.monitoring_endpoint}/alerts",
                       json=alert_payload,
                       timeout=5
                   )
               except Exception as e:
                   print(f"Failed to create alert: {e}")

See Also
--------

- :doc:`lambda-testing` - AWS Lambda performance testing
- :doc:`integration-testing` - Integration performance testing
- :doc:`ci-cd-integration` - Automated performance testing
- :doc:`../../tutorials/advanced-configuration` - Performance optimization configuration
- :doc:`../../reference/configuration/environment-vars` - Performance-related settings
