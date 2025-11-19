# 400 Error in update_run_with_results - Investigation Summary

## Customer Issue
- No results logged in experiment UI
- HTTP request completed with status: 400
- Logs show successful runs of input_function and evaluator
- Likely failed in `update_run_with_results`

## Root Cause Analysis

The issue occurs in `_update_run_with_results()` function in `src/honeyhive/experiments/core.py`:
1. Function successfully collects session IDs and evaluator metrics
2. Calls `client.evaluations.update_run_from_dict(run_id, update_data)`
3. Backend returns 400 error
4. Exception is caught but only logged as a warning (line 437)
5. No results appear in UI because the update failed silently

## Changes Made

### 1. Enhanced Error Logging in `_update_run_with_results`
**File**: `src/honeyhive/experiments/core.py`

- Added detailed logging before the update request (verbose mode)
- Enhanced exception handling to extract:
  - Response status code
  - Error response body/details
  - Update data being sent
  - Evaluator metrics count
- Improved error messages to include all relevant context
- Added authentication exception warning per memory requirement

### 2. Response Status Validation in `update_run_from_dict`
**File**: `src/honeyhive/api/evaluations.py`

- Added status code check before parsing response JSON
- Raises `APIError` with structured `ErrorResponse` for 400+ status codes
- Includes error response body in exception details
- Properly structured error context for debugging

## Repro Script

Created `repro_400_error.py` to reproduce the issue:
- Based on integration test patterns from `test_experiments_integration.py`
- Runs a simple experiment with evaluators
- Enables verbose logging to capture 400 error details
- Validates backend state after execution

### Usage:
```bash
export HONEYHIVE_API_KEY="your-api-key"
export HONEYHIVE_PROJECT="your-project"
python repro_400_error.py
```

## Next Steps

1. **Run the repro script** to capture the actual 400 error response from backend
2. **Check verbose logs** for:
   - Update data structure being sent
   - Error response body from backend
   - Which field is causing validation failure
3. **Common causes of 400 errors**:
   - Invalid UUID format in `event_ids`
   - Invalid `evaluator_metrics` structure
   - Invalid `status` value
   - Invalid `metadata` structure
   - Missing required fields
   - Backend schema validation failures

## Expected Behavior After Fix

With the enhanced error logging:
- Detailed error messages will show exactly what data was sent
- Error response body will be logged for debugging
- Authentication errors will be clearly flagged
- Developers can identify the root cause of 400 errors quickly

## Files Modified

1. `src/honeyhive/experiments/core.py` - Enhanced error handling in `_update_run_with_results`
2. `src/honeyhive/api/evaluations.py` - Added status code validation in `update_run_from_dict`
3. `repro_400_error.py` - New repro script for testing

