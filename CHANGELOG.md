# Changelog

## [0.2.56] - 2025-01-22

### Fixed
- **CRITICAL**: Fixed OTEL span dropping in evaluation harness
- Changed default `max_workers` from 10 to 1 to eliminate TracerWrapper concurrency bugs
- Resolved `'TracerWrapper' object has no attribute '_TracerWrapper__spans_processor'` errors
- Users can still enable concurrency via `max_workers=N` or `HH_MAX_WORKERS` env var