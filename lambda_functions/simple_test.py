"""Simple Lambda function to test basic Docker setup."""

import json
import os
import time
from typing import Any, Dict


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simple Lambda handler for testing Docker setup."""
    print(f"🚀 Lambda invocation started: {getattr(context, 'aws_request_id', 'test')}")

    start_time = time.time()

    try:
        # Test basic Lambda functionality
        result = {
            "message": "Lambda Docker setup works!",
            "event": event,
            "lambda_context": {
                "function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
                "function_version": os.getenv("AWS_LAMBDA_FUNCTION_VERSION"),
                "memory_limit": os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "128"),
            },
            "execution_time_ms": (time.time() - start_time) * 1000,
            "timestamp": time.time(),
        }

        return {
            "statusCode": 200,
            "body": json.dumps(result),
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
