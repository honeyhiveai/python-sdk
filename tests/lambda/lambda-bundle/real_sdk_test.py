"""Real HoneyHive SDK test in Lambda environment."""

import json
import os
import time
from typing import Any, Dict


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test the real HoneyHive SDK in Lambda."""
    print(
        f"🚀 Real SDK Lambda test started: {getattr(context, 'aws_request_id', 'test')}"
    )

    start_time = time.time()

    try:
        # Import the real HoneyHive SDK
        from honeyhive.tracer import HoneyHiveTracer
        from honeyhive.tracer.otel_tracer import enrich_span

        print("✅ Successfully imported real HoneyHive SDK")

        # Initialize the real tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "test-key"),
            project=os.getenv("HH_PROJECT", "lambda-real-test"),
            source="aws-lambda",
            session_name="real-sdk-lambda-test",
            test_mode=True,  # Use test mode to avoid real API calls
            disable_http_tracing=True,  # Optimize for Lambda
        )

        print("✅ Real HoneyHive tracer initialized successfully")

        # Test span creation and management
        with tracer.start_span("real_lambda_test") as span:
            # Set span attributes
            span.set_attribute(
                "lambda.function_name", os.getenv("AWS_LAMBDA_FUNCTION_NAME")
            )
            span.set_attribute(
                "lambda.request_id", getattr(context, "aws_request_id", "test")
            )
            span.set_attribute(
                "lambda.memory_size",
                os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "128"),
            )
            span.set_attribute("test.type", "real_sdk")
            span.set_attribute("test.event", event.get("test", "unknown"))

            print("✅ Span attributes set successfully")

            # Test enrich_span context manager
            with enrich_span(
                metadata={
                    "test_type": "real_sdk_lambda",
                    "container_type": "custom_build",
                    "runtime": "python3.11",
                    "sdk_version": "real",
                    "event_data": event,
                },
                outputs={
                    "lambda_execution": "success",
                    "sdk_integration": "working",
                    "performance_ok": True,
                },
                error=None,
                tracer=tracer,
            ):
                print("✅ enrich_span context manager working")

                # Simulate some work
                work_start = time.time()
                time.sleep(0.1)  # Simulate processing
                work_time = (time.time() - work_start) * 1000

                print(f"✅ Work simulation completed in {work_time:.2f}ms")

        # Test force_flush functionality
        print("🔄 Testing force_flush...")
        flush_start = time.time()
        flush_success = tracer.force_flush(timeout_millis=2000)
        flush_time = (time.time() - flush_start) * 1000

        print(f"✅ Force flush completed: {flush_success} in {flush_time:.2f}ms")

        # Prepare response
        execution_time = (time.time() - start_time) * 1000

        result = {
            "message": "🎉 Real HoneyHive SDK working perfectly in Lambda!",
            "sdk_info": {
                "type": "real_honeyhive_sdk",
                "import_success": True,
                "tracer_init_success": True,
                "span_creation_success": True,
                "enrich_span_success": True,
                "force_flush_success": flush_success,
            },
            "performance": {
                "total_execution_ms": execution_time,
                "work_simulation_ms": work_time,
                "flush_time_ms": flush_time,
            },
            "lambda_info": {
                "function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
                "memory_size": os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "128"),
                "runtime": "python3.11",
                "request_id": getattr(context, "aws_request_id", "test"),
            },
            "event": event,
            "timestamp": time.time(),
        }

        print("✅ Real SDK test completed successfully")

        return {"statusCode": 200, "body": json.dumps(result)}

    except ImportError as e:
        print(f"❌ SDK import failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": f"SDK import failed: {str(e)}",
                    "type": "ImportError",
                    "execution_time_ms": (time.time() - start_time) * 1000,
                }
            ),
        }

    except Exception as e:
        print(f"❌ Real SDK test failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                    "type": type(e).__name__,
                    "execution_time_ms": (time.time() - start_time) * 1000,
                }
            ),
        }
