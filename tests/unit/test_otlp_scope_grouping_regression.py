"""Regression test for HHAI-4245: OTLP batch export must group spans by scope.

When BatchSpanProcessor batches spans from different instrumentors (e.g.
pydantic-ai chat + httpx POST), the OTLP JSON payload must place each span
under its own instrumentation scope. Otherwise the ingestion pipeline
misidentifies the instrumentor and misclassifies model events as chains.

This test was written BEFORE the fix to prove the bug exists, then verified
to pass after the fix.
"""

from typing import Any, Dict, List
from unittest.mock import Mock

import pytest
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import StatusCode

from honeyhive.tracer.processing.otlp_exporter import OTLPJSONExporter


def _make_span(
    name: str,
    scope_name: str,
    scope_version: str = "",
    trace_id: int = 0xABCD1234ABCD1234ABCD1234ABCD1234,
    span_id: int = 0x1234567890ABCDEF,
    parent_span_id: int = 0,
    attributes: Dict[str, str] | None = None,
) -> Mock:
    """Create a mock ReadableSpan with a specific instrumentation scope."""
    span = Mock(spec=ReadableSpan)
    span.name = name

    # Context
    ctx = Mock()
    ctx.trace_id = trace_id
    ctx.span_id = span_id
    span.context = ctx

    # Parent
    if parent_span_id:
        parent = Mock()
        parent.span_id = parent_span_id
        span.parent = parent
    else:
        span.parent = None

    # Attributes
    span.attributes = attributes or {}

    # Events
    span.events = []

    # Status
    status = Mock()
    status.status_code = StatusCode.OK
    status.description = None
    span.status = status

    # Kind
    kind = Mock()
    kind.name = "INTERNAL"
    span.kind = kind

    # Timestamps
    span.start_time = 1000000000
    span.end_time = 2000000000

    # Resource
    span.resource = None

    # Instrumentation scope
    scope = Mock()
    scope.name = scope_name
    scope.version = scope_version if scope_version else None
    span.instrumentation_scope = scope

    return span


class TestOTLPScopeGroupingRegression:
    """HHAI-4245: Spans from different scopes must be in separate scopeSpans."""

    def test_multi_scope_batch_preserves_each_spans_scope(self) -> None:
        """A batch with pydantic-ai and httpx spans must produce two scopeSpans.

        This is the exact customer scenario: PydanticAI emits a 'chat' span
        and httpx emits a 'POST' child span. When batched together, each must
        retain its own instrumentation scope so the ingestion pipeline can
        correctly route them.
        """
        exporter = OTLPJSONExporter(endpoint="http://localhost:9999/v1/traces")

        chat_span = _make_span(
            name="chat gpt-4o-mini",
            scope_name="pydantic-ai",
            scope_version="0.1.0",
            span_id=0xAAAAAAAAAAAAAAAA,
        )
        post_span = _make_span(
            name="POST",
            scope_name="opentelemetry.instrumentation.httpx",
            scope_version="0.50b0",
            span_id=0xBBBBBBBBBBBBBBBB,
            parent_span_id=0xAAAAAAAAAAAAAAAA,
        )

        # httpx POST ends first → appears first in batch
        payload = exporter._spans_to_otlp_json_payload([post_span, chat_span])

        scope_spans = payload["resourceSpans"][0]["scopeSpans"]

        # There must be exactly 2 scopeSpans entries, one per instrumentor
        assert len(scope_spans) == 2, (
            f"Expected 2 scopeSpans (one for pydantic-ai, one for httpx), "
            f"got {len(scope_spans)}. Scope names: "
            f"{[ss['scope'].get('name') for ss in scope_spans]}"
        )

        # Extract the scope names from the payload
        scope_names = {ss["scope"]["name"] for ss in scope_spans}
        assert "pydantic-ai" in scope_names, (
            f"pydantic-ai scope missing from scopeSpans. Found: {scope_names}"
        )
        assert "opentelemetry.instrumentation.httpx" in scope_names, (
            f"httpx scope missing from scopeSpans. Found: {scope_names}"
        )

    def test_chat_span_not_tagged_with_httpx_scope(self) -> None:
        """The chat span must NOT be placed under the httpx scope.

        This was the root cause: when httpx POST was the first span in the
        batch, ALL spans got tagged with httpx's scope name, causing the
        ingestion pipeline to misclassify the chat span.
        """
        exporter = OTLPJSONExporter(endpoint="http://localhost:9999/v1/traces")

        chat_span = _make_span(
            name="chat gpt-4o-mini",
            scope_name="pydantic-ai",
            span_id=0xAAAAAAAAAAAAAAAA,
        )
        post_span = _make_span(
            name="POST",
            scope_name="opentelemetry.instrumentation.httpx",
            span_id=0xBBBBBBBBBBBBBBBB,
            parent_span_id=0xAAAAAAAAAAAAAAAA,
        )

        # httpx first in batch (this was the trigger)
        payload = exporter._spans_to_otlp_json_payload([post_span, chat_span])

        # Find which scopeSpan contains the chat span
        for scope_span in payload["resourceSpans"][0]["scopeSpans"]:
            for span in scope_span["spans"]:
                if span["name"] == "chat gpt-4o-mini":
                    assert scope_span["scope"]["name"] == "pydantic-ai", (
                        f"chat span is under scope "
                        f"'{scope_span['scope']['name']}' but should be "
                        f"under 'pydantic-ai'"
                    )
                    return

        pytest.fail("chat gpt-4o-mini span not found in payload")

    def test_single_scope_batch_still_works(self) -> None:
        """A batch where all spans share the same scope produces one scopeSpan."""
        exporter = OTLPJSONExporter(endpoint="http://localhost:9999/v1/traces")

        span_a = _make_span(
            name="span_a",
            scope_name="pydantic-ai",
            span_id=0x1111111111111111,
        )
        span_b = _make_span(
            name="span_b",
            scope_name="pydantic-ai",
            span_id=0x2222222222222222,
        )

        payload = exporter._spans_to_otlp_json_payload([span_a, span_b])

        scope_spans = payload["resourceSpans"][0]["scopeSpans"]
        assert len(scope_spans) == 1
        assert scope_spans[0]["scope"]["name"] == "pydantic-ai"
        assert len(scope_spans[0]["spans"]) == 2

    def test_three_different_scopes(self) -> None:
        """A batch with 3 instrumentors produces 3 scopeSpans."""
        exporter = OTLPJSONExporter(endpoint="http://localhost:9999/v1/traces")

        spans = [
            _make_span(
                name="POST",
                scope_name="opentelemetry.instrumentation.httpx",
                span_id=0x1111111111111111,
            ),
            _make_span(
                name="chat", scope_name="pydantic-ai", span_id=0x2222222222222222
            ),
            _make_span(
                name="invoke_agent",
                scope_name="customer.framework",
                span_id=0x3333333333333333,
            ),
        ]

        payload = exporter._spans_to_otlp_json_payload(spans)

        scope_spans = payload["resourceSpans"][0]["scopeSpans"]
        assert len(scope_spans) == 3, f"Expected 3 scopeSpans, got {len(scope_spans)}"
        scope_names = {ss["scope"]["name"] for ss in scope_spans}
        assert scope_names == {
            "opentelemetry.instrumentation.httpx",
            "pydantic-ai",
            "customer.framework",
        }
