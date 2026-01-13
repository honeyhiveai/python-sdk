"""Integration test for FastAPI multi-session handling with global tracer.

This test demonstrates and validates the recommended pattern for handling
multiple concurrent sessions with a single globally-initialized tracer.

The key pattern:
1. Initialize tracer ONCE at app startup (shared across all requests)
2. Use create_session() or acreate_session() in middleware to create
   request-scoped sessions stored in baggage (ContextVar-based)
3. All spans within a request automatically use the correct session

This test requires:
- HH_API_KEY environment variable (or in .env file)
- Network access to HoneyHive API
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

import pytest

# Check for required dependencies
try:
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from httpx import ASGITransport, AsyncClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from honeyhive import HoneyHiveTracer, trace

# Skip all tests if FastAPI is not installed
pytestmark = pytest.mark.skipif(
    not HAS_FASTAPI, reason="FastAPI not installed (pip install fastapi httpx)"
)


# pylint: disable=redefined-outer-name
# Justification: Pytest fixtures use the name as dependency injection


@pytest.fixture
def api_key() -> Optional[str]:
    """Get API key from environment."""
    return os.getenv("HH_API_KEY") or os.getenv("HONEYHIVE_API_KEY")


@pytest.fixture
def has_api_key(api_key: Optional[str]) -> bool:
    """Check if API key is available."""
    return api_key is not None


class TestFastAPIMultiSessionIntegration:
    """Integration tests for FastAPI multi-session handling.

    These tests use real API calls to validate the multi-session pattern.
    """

    def test_middleware_creates_isolated_sessions_sync(
        self, api_key: Optional[str], has_api_key: bool
    ) -> None:
        """Test that middleware creates isolated sessions for each request.

        This test uses the synchronous create_session() to avoid event loop
        issues with Starlette's TestClient between requests.
        """
        if not has_api_key:
            pytest.skip("HH_API_KEY not set - skipping integration test")

        # Track created sessions for verification
        created_sessions: List[str] = []

        # Create FastAPI app with multi-session middleware
        app = FastAPI()

        # Initialize tracer ONCE (shared across all requests)
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project="test-fastapi-multi-session",
            source="integration-test",
        )

        @app.middleware("http")
        async def session_middleware(request: Request, call_next: Any) -> Any:
            """Create isolated session for each request using baggage."""
            # Use sync create_session to avoid event loop issues with TestClient
            # In production with real async servers (uvicorn), use acreate_session
            session_id = tracer.create_session(
                session_name=f"test-request-{request.url.path}",
                inputs={
                    "method": request.method,
                    "path": str(request.url.path),
                },
            )

            if session_id:
                created_sessions.append(session_id)

            response = await call_next(request)

            # Enrich session with response data
            tracer.enrich_session(
                outputs={"status_code": response.status_code},
                metadata={"completed": True},
            )

            return response

        @app.get("/test/{item_id}")
        @trace(tracer=tracer, event_type="chain")
        async def test_endpoint(item_id: str) -> Dict[str, str]:
            """Test endpoint that creates a traced span."""
            # This span automatically uses the session_id from baggage
            tracer.enrich_span(metadata={"item_id": item_id})
            return {"item_id": item_id, "status": "processed"}

        # Make multiple requests using sync TestClient
        client = TestClient(app)

        response1 = client.get("/test/item-1")
        assert response1.status_code == 200
        assert response1.json()["item_id"] == "item-1"

        response2 = client.get("/test/item-2")
        assert response2.status_code == 200
        assert response2.json()["item_id"] == "item-2"

        # Verify sessions were created
        assert len(created_sessions) == 2
        # Verify sessions are different (isolated)
        assert created_sessions[0] != created_sessions[1]

        # Cleanup
        tracer.shutdown()

    @pytest.mark.asyncio
    async def test_concurrent_requests_have_isolated_sessions(
        self, api_key: Optional[str], has_api_key: bool
    ) -> None:
        """Test that concurrent async requests have properly isolated sessions.

        This is the critical test for multi-session handling - verifying that
        concurrent requests don't interfere with each other's session context.
        """
        if not has_api_key:
            pytest.skip("HH_API_KEY not set - skipping integration test")

        # Track session IDs per request
        request_sessions: Dict[str, str] = {}

        app = FastAPI()

        # Initialize tracer ONCE
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project="test-fastapi-concurrent",
            source="integration-test",
        )

        @app.middleware("http")
        async def session_middleware(request: Request, call_next: Any) -> Any:
            """Create isolated session for each request."""
            request_id = request.headers.get("X-Request-ID", "unknown")

            session_id = await tracer.acreate_session(
                session_name=f"concurrent-test-{request_id}",
                inputs={"request_id": request_id},
            )

            if session_id:
                request_sessions[request_id] = session_id

            response = await call_next(request)
            return response

        @app.get("/slow/{delay}")
        @trace(tracer=tracer, event_type="chain")
        async def slow_endpoint(delay: float) -> Dict[str, Any]:
            """Endpoint with artificial delay to test concurrency."""
            await asyncio.sleep(delay)
            return {"delay": delay, "completed": True}

        # Make concurrent requests
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Start multiple requests concurrently with different delays
            tasks = [
                client.get("/slow/0.1", headers={"X-Request-ID": "req-1"}),
                client.get("/slow/0.05", headers={"X-Request-ID": "req-2"}),
                client.get("/slow/0.15", headers={"X-Request-ID": "req-3"}),
            ]

            responses = await asyncio.gather(*tasks)

        # Verify all requests completed successfully
        assert all(r.status_code == 200 for r in responses)

        # Verify each request got a unique session
        assert len(request_sessions) == 3
        session_ids = list(request_sessions.values())
        assert len(set(session_ids)) == 3, "All sessions should be unique"

        # Cleanup
        tracer.shutdown()
