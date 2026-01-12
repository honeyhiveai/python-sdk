"""Unit tests for FastAPI multi-session pattern with mocked API calls.

These tests verify the multi-session pattern works correctly without
requiring actual API access, making them faster and more reliable for CI.
"""

from typing import Any, Dict
from unittest.mock import patch

import pytest

# Check for required dependencies
try:
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from honeyhive import HoneyHiveTracer, trace

# Skip all tests if FastAPI is not installed
pytestmark = pytest.mark.skipif(
    not HAS_FASTAPI, reason="FastAPI not installed (pip install fastapi httpx)"
)


class TestFastAPIMultiSessionMocked:
    """Tests for FastAPI multi-session pattern with mocked API calls."""

    def test_session_id_stored_in_baggage_not_instance(self) -> None:
        """Verify that create_session stores session_id in baggage, not instance.

        This is critical for concurrent request isolation.
        """
        app = FastAPI()

        # Create tracer in test mode (no API calls)
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )

        # Track instance session_id
        initial_session_id = tracer._session_id

        @app.middleware("http")
        async def session_middleware(request: Request, call_next: Any) -> Any:
            # Mock the session API to return a session ID
            with patch.object(tracer, "session_api") as mock_api:
                mock_response = type(
                    "Response", (), {"session_id": "mock-session-123"}
                )()

                async def mock_create_async(_: Any) -> Any:
                    return mock_response

                mock_api.create_session_from_dict_async = mock_create_async

                session_id = await tracer.acreate_session(session_name="test-session")

                # Verify session was created
                assert session_id == "mock-session-123"

                # CRITICAL: Instance session_id should NOT be modified
                assert tracer._session_id == initial_session_id

            return await call_next(request)

        @app.get("/test")
        async def test_endpoint() -> Dict[str, str]:
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200

    def test_with_session_context_manager(self) -> None:
        """Test the with_session context manager pattern."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )

        # Mock create_session to return a session ID
        with patch.object(tracer, "create_session", return_value="ctx-session-456"):
            with tracer.with_session(
                session_name="context-manager-test",
                inputs={"test": "data"},
            ) as session_id:
                assert session_id == "ctx-session-456"

    def test_sync_create_session_for_flask_pattern(self) -> None:
        """Test sync create_session for Flask/Django patterns."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )

        # Mock the session API
        with patch.object(tracer, "session_api") as mock_api:
            mock_response = type("Response", (), {"session_id": "sync-session-789"})()
            mock_api.create_session_from_dict.return_value = mock_response

            session_id = tracer.create_session(
                session_name="sync-test-session",
                inputs={"sync": True},
            )

            assert session_id == "sync-session-789"

            # Verify API was called with correct params
            call_args = mock_api.create_session_from_dict.call_args[0][0]
            assert call_args["session_name"] == "sync-test-session"
            assert call_args["inputs"] == {"sync": True}

    def test_create_session_with_provided_session_id_calls_api(self) -> None:
        """Test that providing session_id still calls API by default."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )

        # Provide our own session ID - should call API with that ID
        with patch.object(tracer, "session_api") as mock_api:
            mock_response = type(
                "Response", (), {"session_id": "my-custom-session-id"}
            )()
            mock_api.create_session_from_dict.return_value = mock_response

            session_id = tracer.create_session(
                session_id="my-custom-session-id",
                session_name="custom-session",
            )

            # Verify returned session ID matches what we provided
            assert session_id == "my-custom-session-id"

            # Verify API WAS called with the provided session_id
            mock_api.create_session_from_dict.assert_called_once()
            call_args = mock_api.create_session_from_dict.call_args[0][0]
            assert call_args["session_id"] == "my-custom-session-id"

    def test_create_session_with_skip_api_call(self) -> None:
        """Test that skip_api_call=True skips the API call."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )

        # Provide session_id with skip_api_call=True - should NOT call API
        with patch.object(tracer, "session_api") as mock_api:
            session_id = tracer.create_session(
                session_id="existing-session-id",
                skip_api_call=True,
            )

            # Verify returned session ID matches what we provided
            assert session_id == "existing-session-id"

            # Verify API was NOT called
            mock_api.create_session_from_dict.assert_not_called()


class TestFastAPIMiddlewareExample:
    """Example-driven tests showing the recommended patterns."""

    # pylint: disable=too-few-public-methods
    # Justification: This is an example test class, not a production class

    def test_complete_fastapi_example(self) -> None:
        """Complete example of FastAPI multi-session pattern.

        This test serves as executable documentation of the recommended pattern.
        """
        # ===== SETUP: Initialize tracer ONCE at app startup =====
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="my-api",
            source="production",
            test_mode=True,  # Use test_mode for this example
        )

        app = FastAPI()

        # ===== MIDDLEWARE: Create session per request =====
        @app.middleware("http")
        async def honeyhive_session_middleware(request: Request, call_next: Any) -> Any:
            """
            Multi-session middleware pattern.

            Key points:
            1. acreate_session() stores session_id in baggage (ContextVar)
            2. Does NOT modify tracer._session_id (would cause race conditions)
            3. Each concurrent request gets isolated session context
            """
            # For test mode, mock the session creation
            with patch.object(tracer, "session_api") as mock_api:
                mock_session_id = f"session-{id(request)}"
                mock_response = type("Response", (), {"session_id": mock_session_id})()

                async def mock_create_async(_: Any) -> Any:
                    return mock_response

                mock_api.create_session_from_dict_async = mock_create_async

                session_id = await tracer.acreate_session(
                    session_name=f"api-{request.url.path}",
                    inputs={
                        "method": request.method,
                        "path": str(request.url.path),
                        "user_id": request.headers.get("X-User-ID"),
                    },
                )

            # Store session_id in request state for access in endpoints
            request.state.session_id = session_id

            response = await call_next(request)

            # Enrich session with response data
            # enrich_session reads session_id from baggage automatically
            tracer.enrich_session(outputs={"status_code": response.status_code})

            # Optionally add session_id to response headers
            if session_id:
                response.headers["X-Session-ID"] = session_id

            return response

        # ===== ENDPOINTS: Spans automatically use request's session =====
        @app.post("/chat")
        @trace(tracer=tracer, event_type="chain")
        async def chat_endpoint(request: Request) -> Dict[str, Any]:
            """
            Chat endpoint with automatic session association.

            The @trace decorator creates a span that automatically picks up
            session_id from baggage (set by middleware).
            """
            tracer.enrich_span(metadata={"endpoint": "chat"})

            # Nested function calls also use the same session
            result = await process_message("Hello")

            return {
                "response": result,
                "session_id": request.state.session_id,
            }

        @trace(tracer=tracer, event_type="tool")
        async def process_message(message: str) -> str:
            """Process message - span uses parent's session context."""
            tracer.enrich_span(
                inputs={"message": message},
                outputs={"processed": True},
            )
            return f"Processed: {message}"

        # ===== TEST THE PATTERN =====
        client = TestClient(app)

        response = client.post(
            "/chat",
            headers={"X-User-ID": "user-123"},
        )

        assert response.status_code == 200
        assert "session_id" in response.json()
        assert "X-Session-ID" in response.headers

        # Cleanup
        tracer.shutdown()
