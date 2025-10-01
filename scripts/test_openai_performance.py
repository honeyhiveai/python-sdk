#!/usr/bin/env python3
"""Performance test for OpenAI provider detection."""

import time
from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)

# Test data
TRACELOOP_TEST_ATTRS = {
    "gen_ai.system": "openai",
    "gen_ai.request.model": "gpt-4o",
    "gen_ai.usage.prompt_tokens": 100,
    "gen_ai.usage.completion_tokens": 50,
}

processor = UniversalProviderProcessor()

# Warm-up (10 iterations)
print("Warming up...")
for _ in range(10):
    processor._detect_instrumentor_and_provider(TRACELOOP_TEST_ATTRS)

# Performance test (1000 iterations)
print("Running performance test (1000 iterations)...")
start = time.perf_counter()
for _ in range(1000):
    instrumentor, provider = processor._detect_instrumentor_and_provider(
        TRACELOOP_TEST_ATTRS
    )
end = time.perf_counter()

avg_time_ms = (end - start) / 1000 * 1000

print()
print("=" * 70)
print("Performance Results")
print("=" * 70)
print(f"Total time: {(end - start) * 1000:.2f} ms")
print(f"Iterations: 1000")
print(f"Average detection time: {avg_time_ms:.4f} ms")
print()

if avg_time_ms < 0.1:
    print(f"✅ EXCELLENT: Detection is O(1) ({avg_time_ms:.4f} ms < 0.1 ms target)")
elif avg_time_ms < 1.0:
    print(f"✅ GOOD: Detection is fast ({avg_time_ms:.4f} ms < 1 ms)")
else:
    print(f"❌ SLOW: Detection is too slow ({avg_time_ms:.4f} ms >= 1 ms)")
    exit(1)

print("=" * 70)
