"""Basic Lambda function to test HoneyHive SDK compatibility."""

import json
import os
import sys
import time
from typing import Any, Dict

# Add the SDK to the path (simulates pip install in real Lambda)
sys.path.insert(0, "/var/task")

try:
    from honeyhive.tracer import HoneyHiveTracer
    from honeyhive.tracer.decorators import trace

    SDK_AVAILABLE = True
except ImportError as e:
    print(f"❌ SDK import failed: {e}")
    SDK_AVAILABLE = False

# Initialize tracer outside handler for reuse across invocations
tracer = None
if SDK_AVAILABLE:
    try:
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "test-key"),
            project=os.getenv("HH_PROJECT", "lambda-test"),
            source="aws-lambda",
            session_name="lambda-basic-test",
            test_mode=True,  # Enable test mode for Lambda
            disable_http_tracing=True,  # Avoid Lambda networking issues
        )
        print("✅ HoneyHive tracer initialized successfully")
    except Exception as e:
        print(f"❌ Tracer initialization failed: {e}")
        tracer = None


@trace(tracer=tracer, event_type="lambda", event_name="basic_operation")
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data with tracing."""
    if not tracer:
        return {"error": "Tracer not available"}

    # Simulate work
    time.sleep(0.1)

    # Test span enrichment
    from honeyhive.tracer.otel_tracer import enrich_span

    with enrich_span(
        metadata={"lambda_test": True, "data_size": len(str(data))},
        outputs={"processed": True},
        error=None,
        tracer=tracer,
    ):
        result = {
            "processed_data": data,
            "timestamp": time.time(),
            "lambda_context": {
                "function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
                "function_version": os.getenv("AWS_LAMBDA_FUNCTION_VERSION"),
                "memory_limit": os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "128"),
            },
        }

    return result


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler function."""
    print(
        f"🚀 Lambda invocation started: {context.aws_request_id if hasattr(context, 'aws_request_id') else 'test'}"
    )

    start_time = time.time()

    try:
        # Test basic SDK functionality
        if not SDK_AVAILABLE:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "HoneyHive SDK not available"}),
            }

        if not tracer:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "HoneyHive tracer not initialized"}),
            }

        # Create a span for the entire Lambda execution
        with tracer.start_span("lambda_execution") as span:
            span.set_attribute(
                "lambda.request_id", getattr(context, "aws_request_id", "test")
            )
            span.set_attribute(
                "lambda.function_name", os.getenv("AWS_LAMBDA_FUNCTION_NAME", "unknown")
            )
            span.set_attribute(
                "lambda.remaining_time",
                getattr(context, "get_remaining_time_in_millis", lambda: 30000)(),
            )

            # Process the event
            result = process_data(event)

            # Test force_flush before Lambda completes
            flush_success = tracer.force_flush(timeout_millis=2000)
            span.set_attribute("lambda.flush_success", flush_success)

        execution_time = (time.time() - start_time) * 1000

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "HoneyHive SDK works in Lambda!",
                    "execution_time_ms": execution_time,
                    "flush_success": flush_success,
                    "result": result,
                }
            ),
        }

    except Exception as e:
        print(f"❌ Lambda execution failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                    "execution_time_ms": (time.time() - start_time) * 1000,
                }
            ),
        }

    finally:
        # Ensure cleanup
        if tracer:
            try:
                tracer.force_flush(timeout_millis=1000)
            except Exception as e:
                print(f"⚠️ Final flush failed: {e}")
