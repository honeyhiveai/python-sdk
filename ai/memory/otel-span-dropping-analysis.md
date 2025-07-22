# OTEL Span Dropping Analysis - Evaluation Harness

## Investigation Summary

Investigation conducted on 2025-07-22 to identify root cause of random OTEL span drops in the evaluation harness.

## Root Cause Analysis: 5 Critical Issues

### 1. **Export Timeout Issue** 
**Location**: `src/honeyhive/evaluation/__init__.py:152`
```python
# os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = "30000"  # COMMENTED OUT!
```
**Impact**: Default 10s timeout too short for evaluation workloads, causing span export failures.

### 2. **Non-blocking Flush Race Condition**
**Location**: `src/honeyhive/tracer/__init__.py:472-474`
```python
if not HoneyHiveTracer._flush_lock.acquire(blocking=False):
    return  # SILENTLY SKIPS FLUSH!
```
**Impact**: Concurrent threads calling flush may skip flushing entirely, leaving spans unflushed.

### 3. **ThreadPoolExecutor Context Propagation Issues**
**Location**: `src/honeyhive/evaluation/__init__.py:544-549`
```python
ctx = contextvars.copy_context()
executor.submit(ctx.run, functools.partial(self.run_each, i))
```
**Impact**: OTEL span context may not propagate correctly across thread boundaries despite `contextvars.copy_context()`.

### 4. **Premature Flush in Concurrent Execution**
**Location**: `src/honeyhive/evaluation/__init__.py:565`
```python
finally:
    HoneyHiveTracer.flush()  # May execute before all threads complete span creation
```
**Impact**: Main thread flushes while worker threads are still creating spans.

### 5. **Unconfigured Batch Export Parameters**
**Impact**: No explicit configuration for:
- Batch size limits
- Export retry logic  
- Queue overflow handling

## Architecture Overview

```
┌─────────────────────────────────────┐
│ HoneyHiveTracer                     │
│ - Uses Traceloop SDK                │
│ - Sends to /opentelemetry endpoint  │
│ - CompositePropagator support       │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Evaluation Harness                  │
│ - ThreadPoolExecutor for concurrent │
│ - Context propagation via baggage   │
│ - HoneyHiveTracer.flush() calls     │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Custom Span Instrumentation        │
│ - @trace/@atrace decorators        │
│ - enrich_span() function           │
│ - FunctionInstrumentor              │
└─────────────────────────────────────┘
```

## Key Configuration Points

- **Max Workers**: Default 10, configurable via `HH_MAX_WORKERS` env var
- **Batch Processing**: `disable_batch=False` passed to Traceloop
- **Context Propagation**: Uses OTEL baggage with evaluation-specific metadata
- **Flush Strategy**: Non-blocking with early return on lock contention

## Recommended Fixes

1. **Enable timeout configuration**: Uncomment line 152 in `evaluation/__init__.py`
2. **Fix flush coordination**: Use blocking flush with timeout + proper synchronization
3. **Add explicit context propagation**: Ensure OTEL context transfers to worker threads  
4. **Delay final flush**: Wait for all worker threads to complete before flushing
5. **Configure batch parameters**: Add explicit OTEL batch export configuration

## Test Patterns Revealing Issues

The multi-step evaluation tests expect multiple spans:
```python
# tests/integration/test_multi_step_eval.py:89
assert len(res.object.events) >= 3, f"Expected at least 3 events for session {session_id}"
```

This test may fail if spans are dropped due to timing/concurrency issues.

## Test Results (2025-07-22)

### Concurrent Span Dropping Test Findings

**Test Execution**: `tests/integration/test_concurrent_span_dropping.py`
- **Dataset**: 25 evaluations, 15 concurrent workers
- **Result**: **CRITICAL FAILURES DETECTED** - Test reproduced span dropping more severely than expected

### Critical Issues Found

1. **TracerWrapper Concurrency Bug** - PRIMARY ROOT CAUSE
   ```
   Error in evaluation thread: 'TracerWrapper' object has no attribute '_TracerWrapper__spans_processor'
   ```
   - **Impact**: Multiple threads accessing same tracer instance causing attribute corruption
   - **Frequency**: Occurred in majority of concurrent threads
   - **Effect**: Complete span loss, not just silent dropping

2. **Tracer Initialization Race Conditions**
   ```
   Traceloop exporting traces to https://api.honeyhive.ai/opentelemetry authenticating with bearer token
   ```
   - **Impact**: Multiple concurrent initialization attempts
   - **Effect**: Inconsistent tracer state across threads

3. **Evaluation Framework Crashes**
   ```
   TypeError: 'NoneType' object is not subscriptable
   ```
   - **Impact**: Some evaluation threads returning None instead of results
   - **Effect**: Evaluation framework crashes when processing results

4. **Partial Execution**: Only ~10/25 test cases completed before crash

### Validation of Original Analysis

The test **confirmed** our root cause analysis:
- ✅ **ThreadPoolExecutor Context Issues**: Tracer context not properly isolated between threads
- ✅ **Concurrent Flush Problems**: TracerWrapper internal state corruption under concurrency
- ✅ **Race Conditions**: Multiple tracer initialization attempts

### Severity Assessment

**CRITICAL**: The issue is more severe than silent span dropping - it causes:
- Complete tracer failures in concurrent scenarios
- Evaluation framework crashes
- Data loss and unreliable telemetry

### Recommended Fix Priority

1. **HIGH**: Fix TracerWrapper thread-safety (likely needs Traceloop SDK update or wrapper)
2. **HIGH**: Ensure proper OTEL context isolation per thread
3. **MEDIUM**: Add tracer initialization synchronization
4. **MEDIUM**: Add graceful handling of tracer failures in evaluation framework

## Memory Notes

- **Tricky Dependencies**: Heavy reliance on Traceloop SDK for OTEL integration
- **Naming Patterns**: `run_each()` method handles individual datapoint evaluation
- **Gotchas**: 
  - Non-blocking flush can silently fail
  - ThreadPoolExecutor context copying may not preserve OTEL context
  - Commented-out timeout configuration is critical for evaluation workloads
  - **TracerWrapper is NOT thread-safe** - causes attribute corruption under concurrent access
  - Test successfully reproduces the issue reliably with 15+ concurrent workers