# Integration Test Plan for Config Collision Fix

## Test Philosophy

**Key Insight**: Integration tests expose bugs that unit tests miss because:
- Unit tests mock the code being tested
- Integration tests run real code with real backend verification
- Different priority modes expose different bugs

## Priority Order (Documented in create_unified_config)

```
1. individual_params (highest - backwards compatibility)
2. SessionConfig (session-specific overrides)
3. EvaluationConfig (evaluation-specific overrides)
4. TracerConfig (base defaults)
```

## Test Coverage Strategy

### Tier 1: Comprehensive Multi-Mode Testing

**Fields**: `session_id`, `project`

**Test Modes** (4 per field):
1. **Config Alone**: SessionConfig only, no TracerConfig, no individual param
   - Tests: Original bug report scenario
2. **Config vs TracerConfig**: SessionConfig > TracerConfig
   - Tests: Promotion logic
3. **Individual Param vs Config**: individual param > SessionConfig
   - Tests: Backwards compatibility priority
4. **All Three Together**: individual param > SessionConfig > TracerConfig
   - Tests: Full priority chain

### Tier 2: Essential Mode Testing

**Fields**: `api_key`, `inputs`, `is_evaluation`, `run_id`, `dataset_id`, `datapoint_id`

**Test Mode** (1 per field):
- **Config vs TracerConfig**: SessionConfig/EvaluationConfig > TracerConfig
  - Tests: Core promotion logic (the original bug)

### Tier 3: Unit Test Coverage Only

**Fields**: `test_mode`, `verbose`, `link_carrier`
- Client-side only, no backend verification needed
- Covered by existing unit tests

## Test Results Analysis

### Before Comprehensive Testing
- **Unit Tests**: ✅ ALL PASSED (false confidence - mocked broken code)
- **Integration Tests**: 1 test for session_id only

### After Comprehensive Testing
- **Unit Tests**: ✅ Still passing (test the config dict)
- **Integration Tests**: 
  - Will expose bugs in tracer attribute initialization
  - Will expose bugs in priority ordering
  - Will expose bugs in backwards compatibility

## Fields Tested

### SessionConfig Fields (5 colliding with TracerConfig)
1. ✅ `session_id` - Tier 1 (4 modes)
2. ✅ `project` - Tier 1 (4 modes) 
3. ✅ `api_key` - Tier 2 (1 mode)
4. ✅ `inputs` - Tier 2 (1 mode)
5. `server_url` - Unit test coverage sufficient

### EvaluationConfig Fields (4 colliding with TracerConfig)
1. ✅ `is_evaluation` - Tier 2 (1 mode)
2. ✅ `run_id` - Tier 2 (1 mode)
3. ✅ `dataset_id` - Tier 2 (1 mode)
4. ✅ `datapoint_id` - Tier 2 (1 mode)

## Expected Test Count

- **Tier 1**: 2 fields × 4 modes = 8 tests
- **Tier 2**: 6 fields × 1 mode = 6 tests
- **Total**: 14 integration tests for comprehensive coverage

## Why This Approach Works

1. **Comprehensive coverage** where it matters (session_id, project)
2. **Essential coverage** for all backend-critical fields  
3. **Efficient** - doesn't create 40+ redundant tests
4. **Proves the pattern** - if 2 fields work in all 4 modes, the system works
5. **Catches regressions** - any change to priority logic will fail tests

## Next Steps

1. Complete tier 1 tests (session_id ✅, project - in progress)
2. Simplify tier 2 tests (remove old tests, create focused ones)
3. Run full test suite
4. Document failures and root causes
5. Fix bugs exposed by comprehensive testing

