# Changelog

## [0.2.57] - 2025-08-11

### Added
- **Event ID Enrichment**: Added ability to enrich spans with custom event IDs via `enrich_span(event_id=...)`
- UUID v4 validation for custom event IDs to ensure proper format
- Enhanced span enrichment functionality in tracer module

### Changed
- **Evaluation Stability**: Changed default `max_workers` from 10 to 1 for improved stability
- Made evaluations run synchronously by default to prevent concurrency issues
- Users can still enable concurrency via `max_workers=N` parameter or `HH_MAX_WORKERS` environment variable

## [0.2.56] - 2025-01-22

### Fixed
- **CRITICAL**: Fixed OTEL span dropping in evaluation harness
- Changed default `max_workers` from 10 to 1 to eliminate TracerWrapper concurrency bugs
- Resolved `'TracerWrapper' object has no attribute '_TracerWrapper__spans_processor'` errors
- Users can still enable concurrency via `max_workers=N` or `HH_MAX_WORKERS` env var