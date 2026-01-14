# v0 API Unit Tests Archive

This directory contains unit tests from the v0 SDK API structure. These tests are archived here because:

1. **Architecture Mismatch**: v1 uses an auto-generated httpx client with ergonomic wrapper layer, while v0 had individual API classes (`BaseAPI`, `ConfigurationsAPI`, `DatapointsAPI`, etc.)
2. **No Direct Migration Path**: The v0 API classes no longer exist in v1, making these unit tests incompatible without complete rewrites
3. **Integration Tests Coverage**: The integration tests in `tests/integration/` provide real API coverage for v1 functionality

## Files Archived
- `test_api_base.py` - Tests for v0 BaseAPI class
- `test_api_client.py` - Tests for v0 client (including RateLimiter)
- `test_api_*.py` - Tests for individual v0 API resource classes
- `test_models_*.py` - Tests for v0 model structure

## Future Considerations
If unit test coverage is needed for v1:
- Mock the auto-generated client instead of individual API classes
- Test the ergonomic wrapper layer methods directly
- Focus on error handling and response transformation logic
