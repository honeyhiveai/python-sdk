"""Test HoneyHive SDK behavior during Lambda cold starts."""

import json
import os
import sys
import time
from typing import Any, Dict

sys.path.insert(0, "/var/task")

# Track cold start behavior
COLD_START = True
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
            project="lambda-cold-start-test",
            source="aws-lambda",
            session_name="cold-start-test",
            test_mode=True,
            disable_http_tracing=True,
        )
        TRACER_INIT_TIME = time.time() - init_start
        print(f"✅ Tracer initialization took: {TRACER_INIT_TIME * 1000:.2f}ms")
    except Exception as e:
        print(f"❌ Tracer initialization failed: {e}")
        TRACER_INIT_TIME = -1


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test cold start performance impact."""
    global COLD_START

    handler_start = time.time()
    current_cold_start = COLD_START
    COLD_START = False  # Subsequent invocations are warm starts

    print(f"🔥 {'Cold' if current_cold_start else 'Warm'} start detected")

    try:
        if not tracer:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "error": "Tracer not available",
                        "cold_start": current_cold_start,
                        "sdk_import_time_ms": (
                            SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                        ),
                        "tracer_init_time_ms": (
                            TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                        ),
                    }
                ),
            }

        # Test SDK operations during cold/warm start
        with tracer.start_span("cold_start_test") as span:
            span.set_attribute("lambda.cold_start", current_cold_start)
            span.set_attribute(
                "lambda.sdk_import_time_ms",
                SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1,
            )
            span.set_attribute(
                "lambda.tracer_init_time_ms",
                TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1,
            )

            # Simulate some work
            work_start = time.time()
            with tracer.enrich_span(
                metadata={
                    "test_type": "cold_start",
                    "iteration": event.get("iteration", 1),
                },
                outputs={"cold_start": current_cold_start},
                error=None,
            ):
                # Simulate processing
                time.sleep(0.05)

            work_time = time.time() - work_start
            span.set_attribute("lambda.work_time_ms", work_time * 1000)

        # Test flush performance
        flush_start = time.time()
        flush_success = tracer.force_flush(timeout_millis=1000)
        flush_time = time.time() - flush_start

        total_handler_time = time.time() - handler_start

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Cold start test completed",
                    "cold_start": current_cold_start,
                    "timings": {
                        "sdk_import_ms": (
                            SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                        ),
                        "tracer_init_ms": (
                            TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                        ),
                        "handler_total_ms": total_handler_time * 1000,
                        "work_time_ms": work_time * 1000,
                        "flush_time_ms": flush_time * 1000,
                    },
                    "flush_success": flush_success,
                    "performance_impact": {
                        "init_overhead_ms": (
                            (SDK_IMPORT_TIME + TRACER_INIT_TIME) * 1000
                            if current_cold_start
                            else 0
                        ),
                        "runtime_overhead_ms": (work_time + flush_time) * 1000,
                    },
                }
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                    "cold_start": current_cold_start,
                    "handler_time_ms": (time.time() - handler_start) * 1000,
                }
            ),
        }
