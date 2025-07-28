# Changelog

## [Unreleased]

### Added
- **Tagging**: Added comprehensive tagging functionality to HoneyHive tracer
  - Session-level tags: Initialize tracer with `tags` parameter or add tags dynamically with `add_tags()` method
  - Span-level tags: Add tags to individual traces using `@trace(tags={...})`, `@atrace(tags={...})` decorators or `enrich_span(tags={...})` function
  - Tag propagation: Tags are automatically propagated through OpenTelemetry baggage and stored as span attributes with `honeyhive_tags` prefix
  - Supports nested tag structures, multiple data types, and special characters in tag keys

### Fixed
- **CRITICAL**: Fixed evaluation SDK breaking past 100 datapoints due to multi-threaded tracing issues
- **Performance**: Implemented batch datapoint fetching, replacing N individual API calls with 1 batch call (up to 400x faster)
- **Concurrency**: Fixed non-blocking flush race condition that silently skipped span exports in concurrent evaluations  
- **Reliability**: Enabled OTEL export timeout (30s) to prevent span export failures in evaluation workloads
- **Robustness**: Added graceful fallback when TracerWrapper concurrency issues occur - evaluations continue without tracing
- **Error Handling**: Improved ThreadPoolExecutor error handling with timeouts and better exception reporting
- Added comprehensive tests for multi-threaded evaluation robustness and large dataset handling

## [0.2.56] - 2025-01-22

### Fixed
- **CRITICAL**: Fixed OTEL span dropping in evaluation harness
- Changed default `max_workers` from 10 to 1 to eliminate TracerWrapper concurrency bugs
- Resolved `'TracerWrapper' object has no attribute '_TracerWrapper__spans_processor'` errors
- Users can still enable concurrency via `max_workers=N` or `HH_MAX_WORKERS` env var