#!/usr/bin/env python3
"""Comprehensive performance test for OpenAI provider (detection + extraction)."""

import time
from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)

# Test data
TRACELOOP_TEST_ATTRS = {
    "gen_ai.system": "openai",
    "gen_ai.request.model": "gpt-4o",
    "gen_ai.usage.prompt_tokens": 10,
    "gen_ai.usage.completion_tokens": 8,
    "gen_ai.prompt": "What is Python?",
    "gen_ai.completion": "Python is a programming language.",
    "gen_ai.request.temperature": 0.7,
}

processor = UniversalProviderProcessor()

print("=" * 70)
print("OpenAI Performance Validation")
print("=" * 70)
print()

# Warm-up (10 iterations)
print("Warming up...")
for _ in range(10):
    processor.process_span_attributes(TRACELOOP_TEST_ATTRS)

# Test detection only (1000 iterations)
print("\n1. Detection Performance (1000 iterations):")
print("-" * 70)
start = time.perf_counter()
for _ in range(1000):
    processor._detect_instrumentor_and_provider(TRACELOOP_TEST_ATTRS)
end = time.perf_counter()
detection_avg_ms = (end - start) / 1000 * 1000
print(f"Average detection time: {detection_avg_ms:.4f} ms")
print(f"Target: < 1.0 ms")
print(f"Status: {'✅ PASS' if detection_avg_ms < 1.0 else '❌ FAIL'}")

# Test full extraction (1000 iterations)
print("\n2. Full Extraction Performance (1000 iterations):")
print("-" * 70)
start = time.perf_counter()
for _ in range(1000):
    processor.process_span_attributes(TRACELOOP_TEST_ATTRS)
end = time.perf_counter()
extraction_avg_ms = (end - start) / 1000 * 1000
print(f"Average total time: {extraction_avg_ms:.4f} ms")
print(f"Target: < 6.0 ms")
print(f"Status: {'✅ PASS' if extraction_avg_ms < 6.0 else '❌ FAIL'}")

# Calculate extraction-only time
extraction_only_ms = extraction_avg_ms - detection_avg_ms
print(f"\nExtraction only (total - detection): {extraction_only_ms:.4f} ms")
print(f"Target: < 5.0 ms")
print(f"Status: {'✅ PASS' if extraction_only_ms < 5.0 else '❌ FAIL'}")

# Test percentiles (100 iterations for percentile calculation)
print("\n3. Latency Percentiles (100 iterations):")
print("-" * 70)
times = []
for _ in range(100):
    start = time.perf_counter()
    processor.process_span_attributes(TRACELOOP_TEST_ATTRS)
    end = time.perf_counter()
    times.append((end - start) * 1000)

times_sorted = sorted(times)
p50 = times_sorted[49]
p95 = times_sorted[94]
p99 = times_sorted[98]

print(f"P50: {p50:.4f} ms")
print(f"P95: {p95:.4f} ms")
print(f"P99: {p99:.4f} ms")
print(f"P99 Target: < 2.0 ms")
print(f"Status: {'✅ PASS' if p99 < 2.0 else '❌ FAIL'}")

# Summary
print("\n" + "=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)
all_pass = (
    detection_avg_ms < 1.0
    and extraction_avg_ms < 6.0
    and extraction_only_ms < 5.0
    and p99 < 2.0
)

if all_pass:
    print("✅ ALL PERFORMANCE TARGETS MET")
else:
    print("❌ SOME PERFORMANCE TARGETS FAILED")
    exit(1)

print()
print(f"Detection:        {detection_avg_ms:.4f} ms  (target: < 1.0 ms)")
print(f"Extraction only:  {extraction_only_ms:.4f} ms  (target: < 5.0 ms)")
print(f"Total:            {extraction_avg_ms:.4f} ms  (target: < 6.0 ms)")
print(f"P99:              {p99:.4f} ms  (target: < 2.0 ms)")
print("=" * 70)
