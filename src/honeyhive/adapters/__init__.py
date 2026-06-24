"""Adapters that convert third-party telemetry exports into OpenTelemetry spans.

Import each adapter's submodule directly (e.g.
``from honeyhive.adapters.copilot_studio import copilot_studio_records_to_spans``) so that
pulling in one adapter does not eagerly import the OpenTelemetry SDK for users who don't need
it. This package intentionally does not re-export adapter symbols at the top level.
"""

__all__: list[str] = []
