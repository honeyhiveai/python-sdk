"""Container demo Lambda function that works with mock HoneyHive SDK."""

import json
import os
import time
from typing import Any, Dict


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Demo Lambda handler for container testing."""
    print(
        f"🚀 Container Lambda started: {getattr(context, 'aws_request_id', 'container-test')}"
    )

    start_time = time.time()

    try:
        # Test basic functionality
        from honeyhive.tracer import HoneyHiveTracer

        # Initialize the tracer (mock version)
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "container-test-key"),
            project=os.getenv("HH_PROJECT", "lambda-container-demo"),
            test_mode=True,
        )

        # Create a span
        with tracer.start_span("container_demo_operation") as span:
            span.set_attribute("container.test", True)
            span.set_attribute("event.type", event.get("test", "unknown"))

            # Use enrich_span context manager
            with tracer.enrich_span(
                metadata={"demo": True, "container_build": True},
                outputs={"success": True},
                error=None,
            ):
                # Simulate work
                time.sleep(0.1)

                result = {
                    "message": "🎉 Custom container Lambda test successful!",
                    "event": event,
                    "lambda_info": {
                        "function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
                        "memory_size": os.getenv(
                            "AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "128"
                        ),
                        "runtime": "python3.11",
                    },
                    "container_info": {
                        "build_type": "custom_container",
                        "sdk_type": "mock_honeyhive",
                        "test_mode": True,
                    },
                    "execution_time_ms": (time.time() - start_time) * 1000,
                    "timestamp": time.time(),
                }

        # Test force flush
        flush_success = tracer.force_flush(timeout_millis=1000)
        result["flush_success"] = flush_success

        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }

    except Exception as e:
        print(f"❌ Container test failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                    "message": "Container test failed",
                    "execution_time_ms": (time.time() - start_time) * 1000,
                }
            ),
        }
