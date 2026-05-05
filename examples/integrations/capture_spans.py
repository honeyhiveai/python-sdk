"""Simple span capture utility for generating test cases."""

import json
import os
from datetime import datetime
from pathlib import Path

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanProcessor

TMP_DUMP_ROOT = Path(".tmp/integration-example-dumps")


class SpanCaptureProcessor(SpanProcessor):
    """Captures spans for test case generation."""

    def __init__(self, output_dir: Path, output_file: str):
        self.output_dir = output_dir
        self.output_file = output_file
        self.spans = []

    def on_start(self, span: ReadableSpan, parent_context=None):
        pass

    def on_end(self, span: ReadableSpan):
        """Capture span data."""
        span_data = {
            "name": span.name,
            "context": {
                "trace_id": f"{span.context.trace_id:032x}",
                "span_id": f"{span.context.span_id:016x}",
            },
            "parent": (
                {"span_id": f"{span.parent.span_id:016x}" if span.parent else None}
                if span.parent
                else None
            ),
            "kind": span.kind.name,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "status": {
                "status_code": span.status.status_code.name,
                "description": span.status.description,
            },
            "attributes": dict(span.attributes) if span.attributes else {},
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": dict(event.attributes) if event.attributes else {},
                }
                for event in span.events
            ],
            "links": [],
            "resource": dict(span.resource.attributes) if span.resource else {},
            "instrumentation_info": {
                "name": (
                    span.instrumentation_scope.name
                    if span.instrumentation_scope
                    else ""
                ),
                "version": (
                    span.instrumentation_scope.version
                    if span.instrumentation_scope
                    else ""
                ),
                "schema_url": (
                    span.instrumentation_scope.schema_url
                    if span.instrumentation_scope
                    else ""
                ),
            },
        }
        self.spans.append(span_data)

    def shutdown(self):
        """Save captured spans."""
        if self.spans:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = self.output_dir / self.output_file

            with open(output_path, "w") as f:
                json.dump(
                    {
                        "test_name": self.output_file.replace(".json", ""),
                        "timestamp": datetime.now().isoformat(),
                        "total_spans": len(self.spans),
                        "spans": self.spans,
                    },
                    f,
                    indent=2,
                    default=str,
                )

            print(f"✅ Captured {len(self.spans)} spans to {output_path}")

    def force_flush(self, timeout_millis: int = 30000):
        self.shutdown()


def setup_span_capture(integration_name: str, tracer):
    """Add span capture to a tracer."""
    if os.getenv("CAPTURE_SPANS", "").lower() == "true":
        output_file = (
            f"{integration_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        output_dir = TMP_DUMP_ROOT / integration_name
        processor = SpanCaptureProcessor(output_dir=output_dir, output_file=output_file)
        tracer.provider.add_span_processor(processor)
        return processor
    return None
