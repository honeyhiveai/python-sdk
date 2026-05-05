"""Working HoneyHive SDK test in Lambda."""

import json
import os
import sys
import time
from typing import Any, Dict

# Add the task root to Python path
sys.path.insert(0, "/var/task")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test working HoneyHive SDK in Lambda."""
    print(f"🚀 Working SDK test: {getattr(context, 'aws_request_id', 'test')}")
    start_time = time.time()

    try:
        # Import HoneyHive
        print("📦 Importing HoneyHive...")
        import honeyhive

        print(f"✅ HoneyHive package imported from: {honeyhive.__file__}")

        from honeyhive.tracer import HoneyHiveTracer

        print("✅ HoneyHiveTracer imported successfully")

        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "working-test"),
            project=os.getenv("HH_PROJECT", "lambda-working-test"),
            test_mode=True,
        )
        print("✅ Tracer initialized")

        # Test basic functionality
        with tracer.start_span("working_test") as span:
            span.set_attribute("test.working", True)
            span.set_attribute("lambda.test", "success")
            print("✅ Span created and attributes set")

        # Test force flush
        flush_success = tracer.force_flush(timeout_millis=1000)
        print(f"✅ Force flush: {flush_success}")

        result = {
            "status": "SUCCESS",
            "message": "🎉 Real HoneyHive SDK working in Lambda!",
            "sdk_location": str(honeyhive.__file__),
            "tracer_initialized": True,
            "span_created": True,
            "flush_success": flush_success,
            "execution_time_ms": (time.time() - start_time) * 1000,
            "event": event,
        }

        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "ERROR",
                    "error": str(e),
                    "type": type(e).__name__,
                    "execution_time_ms": (time.time() - start_time) * 1000,
                }
            ),
        }
