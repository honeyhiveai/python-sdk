# Python SDK Performance Guidelines

**Ensure optimal performance through profiling, optimization, and monitoring best practices**

---

## 🚨 TL;DR - Performance Quick Reference

**Keywords for search**: Python SDK performance guidelines, HoneyHive SDK performance optimization, performance profiling cProfile, memory profiling tracemalloc psutil, benchmark framework timing, performance targets tracer span, memory management weakref gc, generator large datasets, cache management TTL LRU, network performance connection pooling, async performance asyncio aiohttp, load testing concurrent users, performance monitoring metrics, optimization priorities correctness first, measure before optimizing profile, batch processing request batching, HTTP/2 httpx timeout configuration

**Core Optimization Philosophy:**
1. **Correctness First**: Never sacrifice correctness for performance
2. **Readability Second**: Maintain code clarity and maintainability  
3. **Performance Third**: Optimize only after measuring
4. **Measure Before Optimizing**: Always profile before making changes
5. **Document Optimizations**: Explain why optimizations were made

**Performance Targets (Python SDK):**
- **Tracer Initialization**: <100ms for basic setup
- **Span Creation**: <1ms per span in normal operation
- **Batch Processing**: Process 1000+ spans per second
- **Memory Usage**: <50MB baseline, <1MB per 1000 spans
- **Network Latency**: <200ms for API calls (excluding network time)

**Key Tools:**
- **Profiling**: cProfile, pstats, time.perf_counter()
- **Memory**: tracemalloc, psutil, weakref, gc
- **Benchmarking**: statistics, dataclasses
- **Network**: httpx, aiohttp, connection pooling
- **Async**: asyncio, concurrent.futures

---

## ❓ Questions This Answers

1. "How do I profile Python SDK performance?"
2. "What are the performance targets for Python SDK?"
3. "How do I measure memory usage?"
4. "How do I benchmark code execution?"
5. "How do I optimize memory management?"
6. "How do I use generators for large datasets?"
7. "How do I implement caching?"
8. "How do I optimize network performance?"
9. "How do I use connection pooling?"
10. "How do I batch requests?"
11. "How do I optimize async performance?"
12. "How do I run load tests?"
13. "How do I monitor runtime performance?"
14. "What is the optimization priority order?"
15. "When should I optimize performance?"
16. "How do I profile code execution time?"
17. "How do I profile memory allocations?"
18. "How do I prevent memory leaks?"
19. "How do I implement batch processing?"
20. "How do I measure requests per second?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Profiling** | `pos_search_project(action="search_standards", query="Python SDK performance profiling cProfile")` |
| **Memory** | `pos_search_project(action="search_standards", query="Python SDK memory profiling optimization")` |
| **Benchmarking** | `pos_search_project(action="search_standards", query="Python SDK benchmark framework timing")` |
| **Network** | `pos_search_project(action="search_standards", query="Python SDK network performance pooling")` |
| **Async** | `pos_search_project(action="search_standards", query="Python SDK async performance best practices")` |
| **Load testing** | `pos_search_project(action="search_standards", query="Python SDK load testing concurrent users")` |
| **Monitoring** | `pos_search_project(action="search_standards", query="Python SDK performance monitoring metrics")` |
| **Targets** | `pos_search_project(action="search_standards", query="Python SDK performance targets requirements")` |

---

## 🎯 Performance Philosophy

### Optimization Priorities

1. **Correctness First**: Never sacrifice correctness for performance
2. **Readability Second**: Maintain code clarity and maintainability  
3. **Performance Third**: Optimize only after measuring
4. **Measure Before Optimizing**: Always profile before making changes
5. **Document Optimizations**: Explain why optimizations were made

### Performance Targets

- **Tracer Initialization**: <100ms for basic setup
- **Span Creation**: <1ms per span in normal operation
- **Batch Processing**: Process 1000+ spans per second
- **Memory Usage**: <50MB baseline, <1MB per 1000 spans
- **Network Latency**: <200ms for API calls (excluding network time)

---

## Profiling and Measurement

### Performance Profiling

```python
import cProfile
import pstats
import time
from contextlib import contextmanager
from typing import Generator

@contextmanager
def profile_code(description: str) -> Generator[None, None, None]:
    """Profile code execution with context manager."""
    profiler = cProfile.Profile()
    start_time = time.perf_counter()
    
    profiler.enable()
    try:
        yield
    finally:
        profiler.disable()
        end_time = time.perf_counter()
        
        # Print timing
        print(f"{description}: {end_time - start_time:.4f}s")
        
        # Print top functions
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

# Usage
with profile_code("Tracer initialization"):
    tracer = HoneyHiveTracer(api_key="test", project="test")
```

### Memory Profiling

```python
import tracemalloc
import psutil
import os

class MemoryProfiler:
    """Profile memory usage."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_memory = None
        
    def start(self):
        """Start memory profiling."""
        tracemalloc.start()
        self.start_memory = self.process.memory_info().rss
        
    def stop(self, description: str):
        """Stop profiling and report results."""
        current_memory = self.process.memory_info().rss
        memory_diff = current_memory - self.start_memory
        
        # Get top memory allocations
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"{description}:")
        print(f"  RSS Memory: {memory_diff / 1024 / 1024:.2f} MB")
        print(f"  Traced Memory: {current / 1024 / 1024:.2f} MB")
        print(f"  Peak Memory: {peak / 1024 / 1024:.2f} MB")

# Usage
profiler = MemoryProfiler()
profiler.start()

# Code to profile
for i in range(1000):
    tracer.start_span(f"span_{i}")

profiler.stop("1000 span creation")
```

### Benchmark Framework

```python
import time
import statistics
from typing import Callable, List, Any
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    """Benchmark execution results."""
    name: str
    mean_time: float
    median_time: float
    std_dev: float
    min_time: float
    max_time: float
    iterations: int

class Benchmark:
    """Performance benchmark framework."""
    
    def __init__(self, iterations: int = 100, warmup: int = 10):
        self.iterations = iterations
        self.warmup = warmup
        
    def run(self, name: str, func: Callable[[], Any]) -> BenchmarkResult:
        """Run benchmark and return results."""
        # Warmup runs
        for _ in range(self.warmup):
            func()
        
        # Actual benchmark runs
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)
        
        return BenchmarkResult(
            name=name,
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            min_time=min(times),
            max_time=max(times),
            iterations=self.iterations
        )
    
    def compare(self, benchmarks: List[BenchmarkResult]) -> None:
        """Compare benchmark results."""
        print("Benchmark Comparison:")
        print("-" * 80)
        print(f"{'Name':<30} {'Mean (ms)':<12} {'Median (ms)':<12} {'Std Dev':<12}")
        print("-" * 80)
        
        for result in sorted(benchmarks, key=lambda x: x.mean_time):
            print(f"{result.name:<30} "
                  f"{result.mean_time * 1000:<12.3f} "
                  f"{result.median_time * 1000:<12.3f} "
                  f"{result.std_dev * 1000:<12.3f}")

# Usage
benchmark = Benchmark(iterations=1000)

results = [
    benchmark.run("span_creation", lambda: tracer.start_span("test")),
    benchmark.run("event_creation", lambda: tracer.create_event(name="test")),
    benchmark.run("context_switch", lambda: tracer.enrich_span({"key": "value"}))
]

benchmark.compare(results)
```

---

## Memory Management

### Memory Optimization Strategies

```python
import weakref
from typing import Dict, Any, Optional
import gc

class MemoryEfficientSpanProcessor:
    """Span processor optimized for memory usage."""
    
    def __init__(self, max_batch_size: int = 512):
        self.max_batch_size = max_batch_size
        self._span_buffer = []
        self._weak_refs = weakref.WeakSet()  # Prevent memory leaks
        
    def on_end(self, span):
        """Process span end with memory optimization."""
        # Use weak references to avoid circular references
        self._weak_refs.add(span)
        
        # Convert to lightweight representation
        span_data = self._extract_span_data(span)
        self._span_buffer.append(span_data)
        
        # Batch processing to reduce memory pressure
        if len(self._span_buffer) >= self.max_batch_size:
            self._flush_batch()
    
    def _extract_span_data(self, span) -> Dict[str, Any]:
        """Extract minimal data from span."""
        return {
            "name": span.name,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "attributes": dict(span.attributes) if span.attributes else {},
            "status": span.status.status_code if span.status else None,
        }
    
    def _flush_batch(self):
        """Flush span batch and clear memory."""
        if not self._span_buffer:
            return
            
        # Process batch
        self._export_spans(self._span_buffer.copy())
        
        # Clear buffer and force garbage collection
        self._span_buffer.clear()
        gc.collect()
```

### Generator Usage for Large Datasets

```python
from typing import Iterator, Dict, Any

def process_large_dataset(data_source: str) -> Iterator[Dict[str, Any]]:
    """Process large dataset using generators to minimize memory usage."""
    with open(data_source, 'r') as file:
        for line in file:
            # Process one line at a time
            processed_data = process_line(line)
            yield processed_data
            
            # Optional: Yield control periodically
            if processed_data.get('should_yield'):
                time.sleep(0.001)  # Allow other operations

# Usage - memory efficient
for item in process_large_dataset('large_file.json'):
    tracer.create_event(**item)
    # Memory is freed after each iteration
```

### Cache Management

```python
import functools
import threading
import time
from typing import Any, Callable, Optional

class TTLCache:
    """Time-to-live cache with automatic cleanup."""
    
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return None
                
            # Check if expired
            if time.time() - self._timestamps[key] > self.ttl:
                del self._cache[key]
                del self._timestamps[key]
                return None
                
            return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        with self._lock:
            # Cleanup if at max size
            if len(self._cache) >= self.max_size:
                self._cleanup_expired()
                
            # If still at max size, remove oldest
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._timestamps.keys(), 
                               key=lambda k: self._timestamps[k])
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self.ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
            del self._timestamps[key]

# Usage
cache = TTLCache(max_size=500, ttl=60.0)  # 1 minute TTL

@functools.lru_cache(maxsize=128)
def expensive_computation(param: str) -> str:
    """Expensive computation with LRU cache."""
    time.sleep(0.1)  # Simulate expensive operation
    return f"result_for_{param}"
```

---

## Network Performance

### Connection Pooling

```python
import httpx
import asyncio
from typing import Optional

class OptimizedHTTPClient:
    """HTTP client optimized for performance."""
    
    def __init__(self):
        # Configure connection pooling
        limits = httpx.Limits(
            max_connections=100,        # Total connections
            max_keepalive_connections=20,  # Keep-alive connections
            keepalive_expiry=30.0       # Keep-alive timeout
        )
        
        # Configure timeouts
        timeout = httpx.Timeout(
            connect=5.0,    # Connection timeout
            read=30.0,      # Read timeout
            write=10.0,     # Write timeout
            pool=5.0        # Pool timeout
        )
        
        self.client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            http2=True,     # Enable HTTP/2
        )
    
    async def batch_request(self, requests: List[Dict[str, Any]]) -> List[httpx.Response]:
        """Send multiple requests concurrently."""
        tasks = []
        
        for request in requests:
            task = self.client.request(**request)
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        successful_responses = [
            resp for resp in responses 
            if isinstance(resp, httpx.Response)
        ]
        
        return successful_responses
```

### Request Batching

```python
import asyncio
from collections import deque
from typing import List, Dict, Any
import time

class BatchProcessor:
    """Batch processor for API requests."""
    
    def __init__(self, 
                 batch_size: int = 100,
                 flush_interval: float = 5.0,
                 max_wait_time: float = 30.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_wait_time = max_wait_time
        
        self._queue = deque()
        self._last_flush = time.time()
        self._processing = False
        
    async def add_request(self, request: Dict[str, Any]) -> None:
        """Add request to batch queue."""
        self._queue.append({
            'request': request,
            'timestamp': time.time()
        })
        
        # Check if we should flush
        await self._check_flush_conditions()
    
    async def _check_flush_conditions(self) -> None:
        """Check if batch should be flushed."""
        current_time = time.time()
        
        should_flush = (
            len(self._queue) >= self.batch_size or
            current_time - self._last_flush >= self.flush_interval or
            (self._queue and 
             current_time - self._queue[0]['timestamp'] >= self.max_wait_time)
        )
        
        if should_flush and not self._processing:
            await self._flush_batch()
    
    async def _flush_batch(self) -> None:
        """Flush current batch."""
        if not self._queue or self._processing:
            return
            
        self._processing = True
        
        try:
            # Extract batch
            batch = []
            while self._queue and len(batch) < self.batch_size:
                item = self._queue.popleft()
                batch.append(item['request'])
            
            if batch:
                await self._process_batch(batch)
                
        finally:
            self._processing = False
            self._last_flush = time.time()
    
    async def _process_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Process batch of requests."""
        # Implementation would send batch to API
        print(f"Processing batch of {len(batch)} requests")
```

---

## Async Performance

### Async Best Practices

```python
import asyncio
from typing import List, Coroutine, Any
import aiohttp

class AsyncTracer:
    """Async-optimized tracer implementation."""
    
    def __init__(self):
        self._session = None
        self._background_tasks = set()
        
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=100,              # Connection pool size
                limit_per_host=30,      # Per-host limit
                keepalive_timeout=30,   # Keep-alive timeout
                enable_cleanup_closed=True
            ),
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Wait for background tasks
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Close session
        if self._session:
            await self._session.close()
    
    async def create_span_async(self, name: str, **attributes) -> None:
        """Create span asynchronously."""
        # Create background task to avoid blocking
        task = asyncio.create_task(self._send_span_data(name, attributes))
        
        # Keep reference to prevent garbage collection
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
    
    async def _send_span_data(self, name: str, attributes: Dict[str, Any]) -> None:
        """Send span data to API."""
        try:
            async with self._session.post('/api/spans', json={
                'name': name,
                'attributes': attributes
            }) as response:
                await response.json()
        except Exception as e:
            # Handle error without blocking
            print(f"Failed to send span: {e}")

# Usage
async def main():
    async with AsyncTracer() as tracer:
        # Create multiple spans concurrently
        tasks = [
            tracer.create_span_async(f"span_{i}")
            for i in range(100)
        ]
        
        await asyncio.gather(*tasks)

# Run with proper event loop
asyncio.run(main())
```

---

## Performance Testing

### Load Testing

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import statistics

class LoadTester:
    """Load testing framework for performance validation."""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        
    def run_load_test(self, 
                     test_func: Callable,
                     concurrent_users: int = 10,
                     duration_seconds: int = 60) -> Dict[str, Any]:
        """Run load test with specified parameters."""
        
        results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            while time.time() < end_time:
                # Submit new requests
                while len(futures) < concurrent_users and time.time() < end_time:
                    future = executor.submit(self._execute_test, test_func)
                    futures.append(future)
                
                # Collect completed requests
                completed_futures = [f for f in futures if f.done()]
                for future in completed_futures:
                    try:
                        response_time = future.result()
                        results['successful_requests'] += 1
                        results['response_times'].append(response_time)
                    except Exception as e:
                        results['failed_requests'] += 1
                        results['errors'].append(str(e))
                    
                    futures.remove(future)
                    results['total_requests'] += 1
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
        
        # Calculate statistics
        if results['response_times']:
            results['avg_response_time'] = statistics.mean(results['response_times'])
            results['median_response_time'] = statistics.median(results['response_times'])
            results['p95_response_time'] = statistics.quantiles(results['response_times'], n=20)[18]  # 95th percentile
        
        results['requests_per_second'] = results['total_requests'] / duration_seconds
        results['success_rate'] = results['successful_requests'] / results['total_requests'] if results['total_requests'] > 0 else 0
        
        return results
    
    def _execute_test(self, test_func: Callable) -> float:
        """Execute single test and return response time."""
        start = time.perf_counter()
        test_func()
        end = time.perf_counter()
        return end - start

# Usage
def test_span_creation():
    tracer = HoneyHiveTracer(api_key="test", project="test")
    tracer.start_span("load_test_span")

load_tester = LoadTester()
results = load_tester.run_load_test(
    test_func=test_span_creation,
    concurrent_users=50,
    duration_seconds=30
)

print(f"Requests per second: {results['requests_per_second']:.2f}")
print(f"Average response time: {results['avg_response_time'] * 1000:.2f}ms")
print(f"Success rate: {results['success_rate'] * 100:.1f}%")
```

---

## Performance Monitoring

### Runtime Performance Metrics

```python
import time
import threading
from collections import defaultdict
from typing import Dict, Any

class PerformanceMonitor:
    """Monitor runtime performance metrics."""
    
    def __init__(self):
        self._metrics = defaultdict(list)
        self._counters = defaultdict(int)
        self._lock = threading.Lock()
        
    def record_timing(self, operation: str, duration: float):
        """Record operation timing."""
        with self._lock:
            self._metrics[f"{operation}_duration"].append(duration)
            self._counters[f"{operation}_count"] += 1
    
    def increment_counter(self, metric: str, value: int = 1):
        """Increment counter metric."""
        with self._lock:
            self._counters[metric] += value
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self._lock:
            summary = {}
            
            # Process timing metrics
            for metric_name, values in self._metrics.items():
                if values:
                    summary[metric_name] = {
                        'count': len(values),
                        'avg': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values)
                    }
            
            # Add counters
            summary.update(dict(self._counters))
            
            return summary

# Global performance monitor
perf_monitor = PerformanceMonitor()

# Usage in tracer
class PerformanceAwareTracer:
    def start_span(self, name: str):
        start_time = time.perf_counter()
        
        try:
            # Actual span creation logic
            span = self._create_span(name)
            return span
        finally:
            duration = time.perf_counter() - start_time
            perf_monitor.record_timing('span_creation', duration)
```

---

## 🔗 Related Standards

**Query workflow for performance:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK performance guidelines")`
2. **Learn test commands** → `pos_search_project(action="search_standards", query="Python SDK test commands")` → `standards/development/testing/test-execution-commands.md`
3. **Learn production checklist** → `pos_search_project(action="search_standards", query="Python SDK production checklist")` → `standards/development/coding/production-checklist.md`
4. **Learn quality gates** → `pos_search_project(action="search_standards", query="Python SDK quality gates")` → `standards/development/coding/quality-standards.md`

---

## Validation Checklist

Before marking performance work as complete:

- [ ] Performance targets met (see targets section)
- [ ] Profiling conducted before optimization
- [ ] Benchmark results documented
- [ ] Memory usage measured
- [ ] Load testing completed (if applicable)
- [ ] Performance metrics monitored
- [ ] Optimizations documented with reasoning
- [ ] No correctness sacrificed for performance
- [ ] Code readability maintained

---

**💡 Key Principle**: Measure before optimizing. Performance optimization without profiling is premature optimization.

